from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.pageDisplay, name="pageDisplayCDN"),
    url(r'^domainDeleted', views.toDeleteCDN, name="toDeleteCDN"),
    url(r'^bulkAdded', views.bulkAddCDN, name="bulkAddCDN"),
    url(r'^checkAudit', views.checkAudit, name="checkAudit"),
]