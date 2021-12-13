from django.db import models

class sslDomain(models.Model):
    domain = models.CharField(max_length=20, default='')
    expiration = models.TextField(max_length=50, default='')
    date_now = models.TextField(max_length=50, default='')
    status = models.IntegerField(max_length=50, default=0)
    daysleft = models.TextField(max_length=50, default='')

    def __str__(self):
        return self.domain


class logsTable(models.Model):
	logs_field = models.TextField(max_length=100, default='')

	def ___str__(self):
		return self.id
