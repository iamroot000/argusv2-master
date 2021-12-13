from django.db import models

# Create your models here.
class JenkinsModel(models.Model):
    UPDATE = models.TextField(null=True)
    CSTEST_DATE = models.TextField(null=True)
    REAL_DATE = models.TextField(null=True)
    DURATION = models.TextField(null=True)
    APPROVER = models.TextField(null=True)
    APPROVER_STATUS = models.TextField(null=True)
    DEVELOPER = models.TextField(null=True)
    ARGUS_USER = models.TextField(null=True)
    BUILD_STATUS = models.TextField(null=True)
    URL = models.TextField(null=True)
    JOBNUMBER = models.TextField(null=True)

    def __str__(self):
        return self.UPDATE


class JenkinsUserKeyModel(models.Model):
    APPROVER = models.TextField(null=True)
    APIKEY = models.TextField(null=True)

    def __str__(self):
        return self.APPROVER


class JenkinsUserOmKeyModel(models.Model):
    OM = models.TextField(null=True)
    APIKEY = models.TextField(null=True)

    def __str__(self):
        return self.OM
