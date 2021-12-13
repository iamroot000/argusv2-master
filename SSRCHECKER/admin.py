from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SSRinitModel)
admin.site.register(SSRinitdataModel)
admin.site.register(SSRinithistoryModel)
admin.site.register(SSRconfighistoryModel)
admin.site.register(SSRconfigsummaryModel)
admin.site.register(SSRmasterconfighistoryModel)
admin.site.register(SSRhomehistoryModel)


