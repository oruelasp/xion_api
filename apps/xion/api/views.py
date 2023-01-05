import os
import json

from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
import xmlrpc.client

from apps.xion.api.serializer import SessionSerializer


class ValidarSerialAPIView(RetrieveAPIView):
    http_method_names = [u'get', u'options']

    def get_object(self):
        db = os.environ.get('ODOO_DB', 'db_xion')
        username = os.environ.get('ODOO_USER', 'admin')
        password = os.environ.get('ODOO_PASSWORD', 'admin')
        url = os.environ.get('ODOO_URL', 'http://soyxion.com:8069')
        print(db, username, password, url)
        serial = self.kwargs.get('serial', None)
        print(serial)
        # Consultar Odoo
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        print("Version: ", version)
        uid = common.authenticate(db, username, password, {})
        print(uid)
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        data = [{'serial': serial, }]
        resultado = common.execute_kw(db, uid, password, 'res.partner', 'api_validar_serial', data)
        return resultado

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            if obj.get('status') == status.HTTP_200_OK:
                return Response({'active': obj.get('active', ''),
                                'date_end': obj.get('date_end', '')},
                                status=obj.get('status', 200))
            else:
                return Response({'error': obj.get('error', '')},
                                status=obj.get('status', 404))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionCreateAPIView(CreateAPIView):
    serializer_class = SessionSerializer

    def perform_create(self, serializer):
        db = os.environ.get('ODOO_DB', 'db_xion')
        username = os.environ.get('ODOO_USER', 'admin')
        password = os.environ.get('ODOO_PASSWORD', 'admin')
        url = os.environ.get('ODOO_URL', 'http://soyxion.com:8069')
        print(db, username, password, url)
        serial = self.kwargs.get('serial', None)
        print(serial)
        # Enviar a Odoo
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        except Exception as e:
            raise APIException(detail=str(e))
        data = [{
            'serial': serial,
            'duration': serializer.data.get('duration'),
            'voltage': serializer.data.get('voltage')
        }]
        resultado = common.execute_kw(db, uid, password, 'xion.session', 'api_save_session', data)
        if resultado.get('status') == 500 or resultado.get('status') == 404:
            raise APIException(detail=resultado.get('error'))
        return resultado

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultado = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(resultado, status=status.HTTP_201_CREATED, headers=headers)
