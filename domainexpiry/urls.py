from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.pageDisplay, name="pageDisplaydomainexp"),
    url(r'^domainDeleted', views.toDeleteDomain, name="toDeleteDomain"),
    url(r'^domainStatusRenew', views.toRenew, name="toRenew"),
    url(r'^bulkAdded', views.bulkAddDomain, name="bulkAddDomain"),
]