from SSRCHECKER.models import *

ssr_dataall = {}
ssr_summaryidc = {}
for iplist in SSRinitdataModel.objects.all():
    ssr_dataall.update({iplist.IP:iplist.IDC})

for idclist in SSRconfigsummaryModel.objects.all():
    ssr_summaryidc.update({idclist.IP:idclist.IDC})

for key,value in ssr_summaryidc.items():
    if key in ssr_dataall.keys():
        ssr_summaryidc[key] = ssr_dataall[key]

ssr_summaryidc