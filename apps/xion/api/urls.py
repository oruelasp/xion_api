from django.urls import include, re_path, path
from apps.xion.api.views import ValidarSerialAPIView, SessionCreateAPIView

app_name = 'xion-api'

urlpatterns = [
    path('v1/', include([
        path('validar-serial/<str:serial>/', ValidarSerialAPIView.as_view(), name='validar'),
        path('session/<str:serial>/', SessionCreateAPIView.as_view(), name='buscar-uuid'),
    ])),
]
