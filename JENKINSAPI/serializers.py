from rest_framework import serializers
from JENKINSAPI.models import *
import datetime


class JenkinsSerializer(serializers.HyperlinkedModelSerializer):
#    URL = serializers.CharField(max_length=100, read_only=True)
    URL = serializers.CharField(max_length=100)
#    JOBNUMBER = serializers.CharField(max_length=100, read_only=True)
    JOBNUMBER = serializers.CharField(max_length=100)
#    UPDATE = serializers.CharField(max_length=100, read_only=True)
    UPDATE = serializers.CharField(max_length=100)
#    APPROVER = serializers.CharField(max_length=100, read_only=True)
    APPROVER = serializers.CharField(max_length=100)
#    DEVELOPER = serializers.CharField(max_length=100, read_only=True)
    DEVELOPER = serializers.CharField(max_length=100)
#    BUILD_STATUS = serializers.CharField(max_length=100, read_only=True)
    BUILD_STATUS = serializers.CharField(max_length=100)


    class Meta:
        model = JenkinsModel
        fields = ['URL', 'UPDATE', 'APPROVER', 'DEVELOPER', 'BUILD_STATUS', 'JOBNUMBER']


    def validate(self, data):
        try:
            jenkinsdata = JenkinsModel.objects.get(UPDATE=data['UPDATE'])
            jenkinsdata.delete()
        except:
            pass
        return data



class JenkinsSerializerUpdate(serializers.HyperlinkedModelSerializer):
    JOBNUMBER = serializers.CharField(max_length=100)
    BUILD_STATUS = serializers.CharField(max_length=100)
    REAL_DATE = serializers.CharField(max_length=100, allow_null=True)

    class Meta:
        model = JenkinsModel
        fields = ['BUILD_STATUS', 'JOBNUMBER', 'REAL_DATE']

    def validate(self, data):
        data['REAL_DATE'] = datetime.datetime.now()
        return data
