from rest_framework import serializers


class SessionSerializer(serializers.Serializer):
    duration = serializers.IntegerField()
    datetime_start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    datetime_end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    voltage = serializers.IntegerField()
