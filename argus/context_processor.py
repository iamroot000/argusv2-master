from fwdcontrol.models import NGINX_CONFIG_LOCATION
from argus.defs.choices import CHOICES_PROJECTS

def nginx_hosts_processor(request):

    nginx_hosts = NGINX_CONFIG_LOCATION.objects.all().values('host_group')

    return {'NGINX_HOSTS':nginx_hosts}


def dps_menu_processor(request):
    menu = []
    perm='can_view_DPS-'

    if 'permissions' in request.session:
        for i in request.session['permissions']:
            if perm in i:
                menu.append(i.strip(perm))
    return {'dps_menu':menu}


def business_unit_processor(request):

    rVal=[]
    for i in CHOICES_PROJECTS:
        rVal.append(i[0])
    return {'projects':rVal}
