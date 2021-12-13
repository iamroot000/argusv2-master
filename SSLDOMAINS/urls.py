from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.pageDisplay, name="pageDisplay"),
    url(r'^domainAdded', views.addDomain, name="addDomain"),
    url(r'^domainDeleted', views.toDelete, name="toDelete"),
    url(r'^bulkAdded', views.bulkAdd, name="bulkAdd")
]
