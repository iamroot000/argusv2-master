from django.shortcuts import render, redirect
from django.contrib import messages
from .process import *
from .forms import *
from django.conf import settings
import os, difflib, json, ast


# Create your views here.

##########################################################-----HOME SERVERS

def SSRhome(request):
    ssr_dataok = SSRinitdataModel.objects.filter(STATUS='OK')
    ssr_datanotok = SSRinitdataModel.objects.exclude(STATUS='OK')
    my_form = SSRhomeForm()
    return render(request, 'SSRCHECKER/base.html', {'ssr_dataok': ssr_dataok,'ssr_datanotok': ssr_datanotok, 'form': my_form, 'logs_recap': True})

def SSRhomehistory(request):
    ssrhistory = SSRhomehistoryModel.objects.all()
    return render(request, 'SSRCHECKER/homehistory.html', {'ssrhistory':ssrhistory, 'logs_recap': True})

def SSRhomedelete(request, SSRID):
    if request.method == 'GET':
        try:
            domain_id = SSRinitdataModel.objects.get(id=SSRID)
            domain_id.delete()
            ssrhomehistory = SSRhomehistoryModel()
            ssrhomehistory.USERNAME = request.user.username
            ssrhomehistory.IP = domain_id.IP
            ssrhomehistory.IDC = domain_id.IDC
            ssrhomehistory.ACTION = 'Delete'
            ssrhomehistory.STATUS = 'Removed'
            ssrhomehistory.DATE = datetime.datetime.now()
            ssrhomehistory.save()
            messages.warning(request, '{} has been Deleted!'.format(domain_id.IP))
            return redirect(SSRhome)
        except:
            return redirect(SSRhome)



def SSRhomecheck(SSRID=None, SSRIP=None, SSRIDC=None, SSRUSER=None):
    try:
        if SSRIP is not None:
            try:
                domain_id = SSRinitdataModel.objects.get(IP=SSRIP)
                domain_id.IDC = SSRIDC
                domain_id.save()
            except:
                SSRinitdataModel.objects.create(
                    IP=SSRIP,
                    PORT=None,
                    STATUS=None,
                    SSR_LINK=None,
                    SSR_CODE=None,
                    IDC=SSRIDC,
                    SS_CODE=None,
                    SS_LINK=None,
                    LAST_CHECK=datetime.datetime.now()
                )
                domain_id = SSRinitdataModel.objects.get(IP=SSRIP)

        else:
            domain_id = SSRinitdataModel.objects.get(id=SSRID)
        pingstatus = SSRsave().ssrping(IPadd=domain_id.IP)
        time.sleep(3)
        if pingstatus == "UNREACHABLE":
            if SSRIP is not None:
                ssrinitdata = SSRinitdataModel.objects.get(IP=SSRIP)
                ssrhomehistory = SSRhomehistoryModel()
                ssrhomehistory.USERNAME = SSRUSER
                ssrhomehistory.IP = SSRIP
                ssrhomehistory.IDC = SSRIDC
                ssrhomehistory.ACTION = 'Add'
                ssrhomehistory.DATE = datetime.datetime.now()
            else:
                ssrinitdata = SSRinitdataModel.objects.get(id=SSRID)
                ssrhomehistory = SSRhomehistoryModel()
                ssrhomehistory.USERNAME = SSRUSER
                ssrhomehistory.IP = ssrinitdata.IP
                ssrhomehistory.IDC = ssrinitdata.IDC
                ssrhomehistory.ACTION = 'Check&Restart'
                ssrhomehistory.DATE = datetime.datetime.now()
            ssrinitdata.PORT = domain_id.PORT
            ssrinitdata.STATUS = pingstatus
            ssrinitdata.SSR_LINK = None
            ssrinitdata.SSR_CODE = None
            ssrinitdata.LAST_CHECK = datetime.datetime.now()
            ssrinitdata.save()
            ssrhomehistory.STATUS = pingstatus
            ssrhomehistory.save()
            return 'Done'
        else:
            ssrdata = SSRsave().ssrinfo(IPok=domain_id.IP, SSRrestart=True)
            time.sleep(3)
            if ssrdata == "TIMEOUT":
                ssrstatus = ssrdata
            else:
                domain_id.PORT = ssrdata["ssr_port"]
                ssrstatus = SSRsave().ssrcheck(ssrip=str(domain_id.IP), ssrport=domain_id.PORT)
            if ssrstatus == 'TIMEOUT' or ssrstatus == 'DOWN':
                if SSRIP is not None:
                    ssrinitdata = SSRinitdataModel.objects.get(IP=SSRIP)
                    ssrhomehistory = SSRhomehistoryModel()
                    ssrhomehistory.USERNAME = SSRUSER
                    ssrhomehistory.IP = SSRIP
                    ssrhomehistory.IDC = SSRIDC
                    ssrhomehistory.ACTION = 'Add'
                    ssrhomehistory.DATE = datetime.datetime.now()
                else:
                    ssrinitdata = SSRinitdataModel.objects.get(id=SSRID)
                    ssrhomehistory = SSRhomehistoryModel()
                    ssrhomehistory.USERNAME = SSRUSER
                    ssrhomehistory.IP = ssrinitdata.IP
                    ssrhomehistory.IDC = ssrinitdata.IDC
                    ssrhomehistory.ACTION = 'Check&Restart'
                    ssrhomehistory.DATE = datetime.datetime.now()
                ssrinitdata.PORT = domain_id.PORT
                ssrinitdata.STATUS = ssrstatus
                ssrinitdata.SSR_LINK = None
                ssrinitdata.SSR_CODE = None
                ssrinitdata.LAST_CHECK = datetime.datetime.now()
                ssrhomehistory.STATUS = ssrstatus


            else:
                if SSRIP is not None:
                    ssrinitdata = SSRinitdataModel.objects.get(IP=SSRIP)
                    ssrhomehistory = SSRhomehistoryModel()
                    ssrhomehistory.USERNAME = SSRUSER
                    ssrhomehistory.IP = SSRIP
                    ssrhomehistory.IDC = SSRIDC
                    ssrhomehistory.ACTION = 'Add'
                    ssrhomehistory.DATE = datetime.datetime.now()
                else:
                    ssrinitdata = SSRinitdataModel.objects.get(id=SSRID)
                    ssrhomehistory = SSRhomehistoryModel()
                    ssrhomehistory.USERNAME = SSRUSER
                    ssrhomehistory.IP = ssrinitdata.IP
                    ssrhomehistory.IDC = ssrinitdata.IDC
                    ssrhomehistory.ACTION = 'Check&Restart'
                    ssrhomehistory.DATE = datetime.datetime.now()
                ssrinitdata.PORT = domain_id.PORT
                ssrinitdata.STATUS = ssrstatus
                ssrinitdata.SSR_LINK = ssrdata['ssr_link']
                ssrinitdata.SSR_CODE = ssrdata['ssr_code']
                ssrinitdata.LAST_CHECK = datetime.datetime.now()
                ssrhomehistory.STATUS = ssrstatus
            ssrinitdata.save()
            ssrhomehistory.save()
            return 'Done'

    except Exception as e:
        pass


def SSRcheck(request, SSRID):
    SSRhomecheck(SSRID=SSRID, SSRUSER=request.user.username)
    domain_id = SSRinitdataModel.objects.get(id=SSRID)
    messages.success(request, '{} has been Checked!'.format(domain_id.IP))
    return redirect(SSRhome)

def SSRhomeadd(request):
    ssr_max = 50
    ssr_dataok = SSRinitdataModel.objects.filter(STATUS='OK')
    ssr_datanotok = SSRinitdataModel.objects.exclude(STATUS='OK')
    my_form = SSRhomeForm()
    ipsuccess = []
    if request.method == 'POST':
        my_form = SSRhomeForm(request.POST)
        if my_form.is_valid():
            if len(request.POST["IP"].split('\n')) > int(ssr_max):
                messages.error(request, '{} only {} IPs are allowed!'.format(request.POST["IP"].split('\n'), str(ssr_max)))
            else:
                for i in request.POST["IP"].split('\n'):
                    data = {'IP': str(i).strip(),
                            'IDC': request.POST['IDC']}
                    if SSRhomeForm(data).is_valid():
                        ipsuccess.append(data['IP'])
                        SSRhomecheck(SSRIP=data['IP'], SSRIDC=data['IDC'], SSRUSER=request.user.username)
                messages.success(request, '{} has been added Successfully!'.format(ipsuccess))
            my_form = SSRhomeForm()

    return render(request, 'SSRCHECKER/base.html', {'ssr_dataok': ssr_dataok,'ssr_datanotok': ssr_datanotok, 'form': my_form, 'logs_recap': True})

##########################################################-----INTIALIZATION
def SSRinitialization(request):
    my_form = SSRinitForm()
    ssr_data = SSRinitModel.objects.all()
    ssr_initdata = SSRinithistoryModel.objects.all()
    logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r')
    if request.method == 'POST':
        my_form = SSRinitForm(request.POST)
        if my_form.is_valid():
            if len(request.POST["IP"].split('\n')) > 10:
                messages.error(request, '{} only 10 IPs are allowed!'.format(request.POST["IP"].split('\n')))
            else:
                for i in request.POST["IP"].split('\n'):
                    data = {'IP': str(i).strip(),
                            'PORT': request.POST['PORT'],
                            'USER': request.POST['USER'],
                            'PASSWORD': request.POST['PASSWORD'],
                            'IDC': request.POST['IDC']}
                    if SSRinitForm(data).is_valid():
                        my_form = SSRinitForm(data)
                        my_form.save()
                ssr_data = SSRinitModel.objects.all()
                my_form = SSRinitForm()
    return render(request, 'SSRCHECKER/ssrinit.html', {'form': my_form, 'ssr_data': ssr_data, 'ssr_initdata': ssr_initdata ,'logs': logs.read(), 'logs_recap': SSRsetup().ansiblerecap()})

def SSRinitlogs(request):
    if request.method == 'GET':
        logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r')
        # logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/testlogs'), 'r')
        SSRsave().ssrlogs(str(request.user.username))
        return render(request, 'SSRCHECKER/logs.html', {'logs': logs.read(), 'logs_recap': SSRsetup().ansiblerecap()})


def SSRdelete(request, SSRID):
    if request.method == 'GET':
        try:
            domain_id = SSRinitModel.objects.get(id=SSRID)
            domain_id.delete()
            return redirect(SSRinitialization)
        except:
            return redirect(SSRinitialization)

def SSRinit(request):
    SSRsetup().ansibleConf()
    SSRsetup().ansibleHosts()
    SSRsetup().ansibleExecute()
    return redirect(SSRinitlogs)


def SSRhistorylogs(request, IPID):
    logs = SSRinithistoryModel.objects.get(id=IPID)
    logs = logs.LOGS
    SSRsave().ssrlogs(request.user.username)
    return render(request, 'SSRCHECKER/logs.html', {'logs': logs, 'logs_recap': True})
##########################################################-----PORT CONFIGURATION


def SSRconfig(request):
    my_form = SSRconfigForm()
    ssr_data = SSRconfigsummaryModel.objects.all()
    ssr_initdata = SSRconfighistoryModel.objects.all()
    ssr_dataall = []
    ssr_dataallmodel = SSRinitdataModel.objects.all()
    ssr_idcform = SSRconfigIDCForm()
    for iplist in SSRinitdataModel.objects.all():
        ssr_dataall.append(iplist.IP)
    logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r')
    if request.method == 'POST':
        my_form = SSRconfigForm(request.POST)
        if my_form.is_valid():
            if len(request.POST["IP"].split('\n')) > 10:
                messages.error(request, '{} only 10 IPs are allowed!'.format(request.POST["IP"].split('\n')))
            else:
                for i in request.POST["IP"].split('\n'):
                    data = {'IP': str(i).strip(),
                            'PORT': request.POST['PORT']
                            }
                    if SSRconfigForm(data).is_valid():
                        my_form = SSRconfigForm(data)
                        my_form.save()
                ssr_data = SSRconfigsummaryModel.objects.all()
                my_form = SSRconfigForm()

    return render(request, 'SSRCHECKER/ssrconfig.html',
                  {'form': my_form, 'ssr_data': ssr_data, 'ssr_initdata': ssr_initdata, 'logs': logs.read(),
                   'logs_recap': SSRsetup().ansiblerecap(), 'ssr_dataall': ssr_dataall, 'ssr_dataallmodel':ssr_dataallmodel,
                   'ssr_idcform':ssr_idcform})




def SSRconfiglogs(request):
    if request.method == 'GET':
        logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r')
        # logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/testlogs'), 'r')
        SSRsave().ssrlogs(str(request.user.username), restartssr=True)
        return render(request, 'SSRCHECKER/logs.html', {'logs': logs.read(), 'logs_recap': SSRsetup().ansiblerecap()})

def SSRconfigdelete(request, SSRID):
    if request.method == 'GET':
        try:
            domain_id = SSRconfigsummaryModel.objects.get(id=SSRID)
            domain_id.delete()
            return redirect(SSRconfig)
        except:
            return redirect(SSRconfig)


def SSRconfigrestart(request):
    ssr_dataall = []
    ssr_summaryidc = []
    ssr_ippass = []
    ssr_ipfail = []
    for iplist in SSRinitdataModel.objects.all():
        ssr_dataall.append(iplist.IP)
    for idclist in SSRconfigsummaryModel.objects.all():
        ssr_summaryidc.append(idclist.IP)
    for i in SSRconfigsummaryModel.objects.all():
        if i.IP in ssr_dataall:
            ssr_ippass.append(i.IP)
        elif i.IDC:
            ssr_ippass.append(i.IP)
        else:
            ssr_ipfail.append(i.IP)
    if len(ssr_ipfail) == 0:
        SSRsetup().ansibleConf()
        SSRsetup().ansibleHosts(ssrrestart=True)
        SSRsetup().ansibleExecute(ssrrestart=True)
        return redirect(SSRconfiglogs)
    elif len(ssr_summaryidc) == 0:
        return redirect(SSRconfig)
    else:
        for errormsg in ssr_ipfail:
            messages.warning(request, 'IDC for {} is missing!'.format(errormsg))
        return redirect(SSRconfig)


def SSRIDCcheck(request, IPsummary):
    my_form = SSRconfigForm()
    ssr_data = SSRconfigsummaryModel.objects.all()
    ssr_initdata = SSRconfighistoryModel.objects.all()
    ssr_dataall = []
    ssr_summaryidc = []
    ssr_dataallmodel = SSRinitdataModel.objects.all()
    ssr_idcform = SSRconfigIDCForm()
    for iplist in SSRinitdataModel.objects.all():
        ssr_dataall.append(iplist.IP)
    for idclist in SSRconfigsummaryModel.objects.all():
        ssr_summaryidc.append(idclist.IP)
    logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r')
    if request.method == 'POST':
        # ssr_idcform = SSRconfigIDCForm({'IDC': '---'})
        ssr_idcform = SSRconfigIDCForm(request.POST)
        if ssr_idcform.is_valid():
            # ssr_form = SSRconfigIDCForm(request.POST)
            # ssr_form.save()
            ssr_idcmodel = SSRconfigsummaryModel.objects.get(IP=IPsummary)
            ssr_idcmodel.IDC = request.POST['IDC']
            ssr_idcmodel.save()
    return render(request, 'SSRCHECKER/ssrconfig.html',
                  {'form': my_form, 'ssr_data': ssr_data, 'ssr_initdata': ssr_initdata, 'logs': logs.read(),
                   'logs_recap': SSRsetup().ansiblerecap(), 'ssr_dataall': ssr_dataall,
                   'ssr_dataallmodel': ssr_dataallmodel,
                   'ssr_idcform': ssr_idcform, 'ssr_summaryidc':ssr_summaryidc})


def SSRconfighistorylogs(request, IPID):
    logs = SSRconfighistoryModel.objects.get(id=IPID)
    logs = logs.LOGS
    SSRsave().ssrlogs(request.user.username, restartssr=True)
    return render(request, 'SSRCHECKER/logs.html', {'logs': logs, 'logs_recap': True})

##########################################################-----FILE CONFIGURATION
def SSRfilelogs(request, IPID):
    logs = SSRmasterconfighistoryModel.objects.get(id=IPID)
    logs = logs.IP
    return render(request, 'SSRCHECKER/logs.html', {'logs': logs, 'logs_recap': True})

def SSRfileupdate(request, IPID):
    filelabel = 'SSR Updated File'
    logs = SSRmasterconfighistoryModel.objects.get(id=IPID)
    logs = logs.CHANGED_ADDED
    myform = SSRconfigtextForm(fileconfig=logs, filelabelname='Update File')
    changelist = []
    for line in difflib.unified_diff(SSRmasterconfighistoryModel.objects.get(id=IPID).PREVIOUS.strip().splitlines(),
                                     SSRmasterconfighistoryModel.objects.get(
                                         id=IPID).CHANGED_ADDED.strip().splitlines(), fromfile='file1',
                                     tofile='file2', lineterm='', n=0):
        for prefix in ('---', '+++', '@@'):
            if line.startswith(prefix):
                break
        else:
            changelist.append(line)
    data = '\n'.join(changelist)
    return render(request, 'SSRCHECKER/filedata.html', {'myform':myform, 'changed_added':data,'logs': logs, 'logs_recap': True, 'filelabel':filelabel})

def SSRfileprevious(request, IPID):
    filelabel = 'SSR Previous File'
    logs = SSRmasterconfighistoryModel.objects.get(id=IPID)
    logs = logs.PREVIOUS
    myform = SSRconfigtextForm(fileconfig=logs, filelabelname='Previous File')
    changelist = []
    for line in difflib.unified_diff(SSRmasterconfighistoryModel.objects.get(id=IPID).PREVIOUS.strip().splitlines(),
                                     SSRmasterconfighistoryModel.objects.get(
                                             id=IPID).CHANGED_ADDED.strip().splitlines(), fromfile='file1',
                                     tofile='file2', lineterm='', n=0):
        for prefix in ('---', '+++', '@@'):
            if line.startswith(prefix):
                break
        else:
            changelist.append(line)
    data = '\n'.join(changelist)
    return render(request, 'SSRCHECKER/filedata.html',
                  {'myform': myform, 'changed_added': data, 'logs': logs, 'logs_recap': True, 'filelabel': filelabel})

def SSRfileconfig(request):
    historydata = SSRmasterconfighistoryModel.objects.all()
    my_form = SSRconfigtextForm()
    return render(request, 'SSRCHECKER/fileconfig.html', {'myform': my_form, 'logs_recap': SSRsetup().ansiblerecap(), 'historydata': historydata})


def SSRfileedit(request):
    historydata = SSRmasterconfighistoryModel.objects.all()
    config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
    config_read = open(config_file, 'r').read()
    condigdata = json.loads(config_read)
    filenames = condigdata["configfile"]
    file_names = {}
    for key, value in filenames.items():
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/{}'.format(value))
        config_read = open(config_file, 'r').read()
        file_names.update({key:config_read})
    my_form = SSRconfigtextForm()
    if request.method == 'POST':
        my_form = SSRconfigtextForm(fileconfig=file_names[request.POST['FILE']], fileinitial=request.POST['FILE'], filechoicesdisabled=True)
    return render(request, 'SSRCHECKER/fileconfig.html', {'myform': my_form, 'logs_recap': SSRsetup().ansiblerecap(), 'historydata': historydata})



def SSRfilsave(request):
    historydata = SSRmasterconfighistoryModel.objects.all()
    config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
    config_read = open(config_file, 'r').read()
    condigdata = json.loads(config_read)
    filenames = condigdata["configfile"]
    my_form = SSRconfigtextForm()
    if request.method == 'POST':
        if filenames[request.POST['FILE']] == 'config.json':
            config_read = request.POST['PREVIOUS']
            try:
                json.loads(config_read)
                checkconfig = ast.literal_eval(config_read)
                checkconfig['configlist']
                checkconfig['configlist']['IDC']
                fail = []
                success = []
                for key, value in checkconfig["configfile"].items():
                    configfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/{}'.format(value))
                    if os.path.exists(configfile):
                        success.append(key)
                    else:
                        fail.append(key)

                if len(checkconfig["configfile"]) != len(checkconfig["configfiledest"]):
                    messages.warning(request, '{} (configfile or configfiledest) missing value!'.format(str(request.POST['FILE'])))
                elif len(fail) == 0:
                    SSRfileconfigprocess().SSRfilesave(fileusername=request.user.username, filename=request.POST['FILE'],filelatest=request.POST['PREVIOUS'])
                    messages.success(request, '{} has been save!'.format(str(request.POST['FILE'])))
                else:
                    for failstatus in fail:
                        messages.warning(request, '{} file does not exist!'.format(failstatus))
            except Exception as e:
                messages.error(request, '{} wrong format!'.format(str(request.POST['FILE'])))
        else:
            SSRfileconfigprocess().SSRfilesave(fileusername=request.user.username, filename=request.POST['FILE'], filelatest=request.POST['PREVIOUS'])
            messages.success(request, '{} has been save!'.format(str(request.POST['FILE'])))

        my_form = SSRconfigtextForm(fileconfig=request.POST['PREVIOUS'], fileinitial=request.POST['FILE'], filechoicesdisabled=True)
    return render(request, 'SSRCHECKER/fileconfig.html', {'myform': my_form, 'logs_recap': SSRsetup().ansiblerecap(), 'historydata': historydata})


def SSRfileprocesslogs(request):
    logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r').read()
    print(logs)
    SSRfileconfigprocess().SSRfilesyncsave(fileusername=request.user.username, filelogs=logs)
    return render(request, 'SSRCHECKER/logs.html', {'logs': logs, 'logs_recap': SSRsetup().ansiblerecap()})


def SSRfilesync(request):
    SSRsetup().ansibleConf()
    SSRfileconfigprocess().SSRfilehosts()
    SSRfileconfigprocess().SSRfileyml()
    SSRfileconfigprocess().SSRfileexecute()
    return redirect(SSRfileprocesslogs)
