from django.db import models
from .apps import *


# Create your models here.
class CDNDomainRouter:
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == CdncheckerConfig.name:
#            return 'CDN_domain_db'
            return 'argus_v2_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == CdncheckerConfig.name:
#            return 'CDN_domain_db'
            return 'argus_v2_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == CdncheckerConfig.name or \
           obj2._meta.app_label == CdncheckerConfig.name:
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == CDNDomainRouter:
#            return db == 'CDN_domain_db'
            return db == 'argus_v2_db'
        return None



class DomainChecker(models.Model):
    product = models.CharField(max_length=50)
    domains = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    lastcheck = models.CharField(max_length=50)
    forcecheck = models.CharField(max_length=50, default='---')

    def __str__(self):
        return self.domains


class DomainCheckerHistory(models.Model):
    username = models.CharField(max_length=50)
    domains = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    action = models.CharField(max_length=50)
    date = models.CharField(max_length=50)

    def __str__(self):
        return self.domains

