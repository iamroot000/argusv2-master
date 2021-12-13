from django.db import models
import datetime


# Create your models here.
class SSRinitModel(models.Model):
    IP = models.CharField(max_length=16, null=True)
    PORT = models.IntegerField(null=True)
    USER = models.CharField(max_length=15, null=True)
    PASSWORD = models.CharField(max_length=50, null=True)
    IDC = models.CharField(max_length=20, null=True)

    V2RAY_PORT = models.IntegerField(null=True)
    V2RAY_PATH = models.TextField(null=True)
    V2RAY_DOMAIN = models.TextField(null=True)

    def __str__(self):
        return self.IP


class SSRinitdataModel(models.Model):
    IP = models.CharField(max_length=16, null=True)
    PORT = models.IntegerField(null=True)
    STATUS = models.CharField(max_length=15, null=True)
    SSR_LINK = models.TextField(null=True)
    SSR_CODE = models.TextField(null=True)
    SS_LINK = models.TextField(null=True)
    SS_CODE = models.TextField(null=True)
    IDC = models.CharField(max_length=20, null=True)
    LAST_CHECK = models.CharField(max_length=50, null=True)

    V2RAY_STATUS = models.TextField(null=True)
    V2RAY_PORT = models.IntegerField(null=True)
    V2RAY_DOMAIN = models.TextField(null=True)
    V2RAY_PATH = models.TextField(null=True)
    V2RAY_URL = models.TextField(null=True)
    V2RAY_DATE = models.TextField(null=True)

    def __str__(self):
        return self.IP


class SSRinithistoryModel(models.Model):
    USERNAME = models.CharField(max_length=50, null=True)
    IP = models.CharField(max_length=16, null=True)
    STATUS = models.CharField(max_length=15, null=True)
    LOGS = models.TextField(null=True)
    IDC = models.CharField(max_length=20, null=True)
    CREATED = models.CharField(max_length=50, null=True)



    def __str__(self):
        return self.IP


class SSRconfighistoryModel(models.Model):
    USERNAME = models.CharField(max_length=50, null=True)
    IP = models.TextField(null=True)
    PORT = models.IntegerField(null=True)
    STATUS = models.CharField(max_length=15, null=True)
    LOGS = models.TextField(null=True)
    DATE = models.CharField(max_length=50, null=True)


    def __str__(self):
        return self.IP


class SSRmasterconfighistoryModel(models.Model):
    USERNAME = models.CharField(max_length=50, null=True)
    IP = models.TextField(null=True)
    PORT = models.IntegerField(null=True)
    FILE = models.CharField(max_length=50, null=True)
    CHANGED_ADDED = models.TextField(null=True)
    PREVIOUS = models.TextField(null=True)
    DATE = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.FILE


class SSRconfigsummaryModel(models.Model):
    IP = models.CharField(max_length=16, null=True)
    PORT = models.IntegerField(null=True)
    IDC = models.CharField(max_length=20, null=True)
    def __str__(self):
        return self.IP

class V2rayconfighistoryModel(models.Model):
    IP = models.TextField(null=True)
    V2RAY_USERNAME = models.TextField(null=True)
    V2RAY_STATUS = models.TextField(null=True)
    V2RAY_LOGS = models.TextField(null=True)
    V2RAY_DATE = models.TextField(null=True)
    V2RAY_PORT = models.IntegerField(null=True)


    def __str__(self):
        return self.IP

class V2rayconfigsummaryModel(models.Model):
    IP = models.CharField(max_length=16, null=True)
    IDC = models.CharField(max_length=20, null=True)
    V2RAY_PORT = models.IntegerField(null=True)
    V2RAY_PATH = models.TextField(null=True)
    V2RAY_DOMAIN = models.TextField(null=True)
    def __str__(self):
        return self.IP




class SSRhomehistoryModel(models.Model):
    USERNAME = models.CharField(max_length=50, null=True)
    IP = models.TextField(null=True)
    STATUS = models.CharField(max_length=50, null=True)
    IDC = models.CharField(max_length=50, null=True)
    ACTION = models.CharField(max_length=50, null=True)
    DATE = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.IP

