from django.shortcuts import render, redirect
from .SSLCHECKER import sslchecker_notA
# from .models import sslDomain, logsTable
from .models import *
from django.contrib import messages
import datetime
from datetime import timedelta
import logging, os

def loggingFile(log_debug=None,log_info=None,log_warning=None,log_error=None,log_critical=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logdir = os.path.join(BASE_DIR, 'SSLDOMAINS/logs/')
    os.popen("find {0} -type f -name '*.log' -mtime +7 -exec rm {1} \;".format(logdir,''))
    LOG_FORMAT = "%(asctime)s %(levelname)s - %(message)s"
    logging.basicConfig(
            filename='{}sslchecker-{}.log'.format(logdir, datetime.datetime.now().strftime("%Y-%m-%d-%H")),
            format=LOG_FORMAT, level=logging.DEBUG)
    logger = logging.getLogger()
    if log_debug:
        logger.debug(str(log_debug))
    if log_info:
        logger.info(str(log_info))
    if log_warning:
        logger.warning(str(log_warning))
    if log_error:
        logger.error(str(log_error))
    if log_critical:
        logger.critical(str(log_critical))


def pageDisplay(request):
    query_set = sslDomain2.objects.all().exclude(skip='yes')
    date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_now = datetime.datetime.strptime(date_now_fmt, '%Y-%m-%d %H:%M:%S')




    user = request.user
    loggingFile(log_debug="({}) - {}".format(user, "Successfully loaded and updated table"))
    query_log = logsTable.objects.all()
    args = {
        "object_list"   : query_set,
        "query_log"     : query_log
    }
    return render(request, 'SSLDOMAINS/home.html', args)


def addDomain(request):
    try:
        if request.method == 'POST':
            get_domain_nstrip = request.POST["get_domain"]
            get_domain = str(get_domain_nstrip.strip().lower())
            user = request.user
            sslchecker_fmt = str(sslchecker_notA(get_domain))
            dom_expiry = datetime.datetime.strptime(sslchecker_fmt, '%Y-%m-%d %H:%M:%S')
            date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_now = datetime.datetime.strptime(date_now_fmt, '%Y-%m-%d %H:%M:%S')
            calc_date = dom_expiry - date_now
            datedif = 0
            dom_list = []

            for check_dom in sslDomain2.objects.all():
                dom_list.append(check_dom.domain)

            if get_domain not in dom_list:

                if calc_date < timedelta(days=0):
                    daysleft = dom_expiry - date_now
                    addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=2,
                                       daysleft=daysleft)
                    addssl.save()
                elif calc_date <= timedelta(days=14):
                    daysleft = dom_expiry - date_now
                    addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=1,
                                       daysleft=daysleft)
                    addssl.save()
                else:
                    daysleft = dom_expiry - date_now
                    addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=0,
                                       daysleft=daysleft)
                    addssl.save()

                query_set = sslDomain2.objects.all()
                log = "{} : ({}) - Successfully added {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,get_domain)
                print(log)
                logsave = logsTable(logs_field=log)
                logsave.save()
                query_log = logsTable.objects.all()
                args = {
                    "object_list"   : query_set,
                    "query_log"     : query_log
                }
                messages.success(request, '({}) Successfully Added!'.format(get_domain))
                return render(request, 'SSLDOMAINS/home.html', args)
            else:
                query_log = logsTable.objects.all()
                query_set = sslDomain2.objects.all()
                messages.warning(request, '({}) already Exist!'.format(get_domain))
                args = {
                    "object_list"   : query_set,
                    "query_log"     : query_log,
                }
                return render(request, 'SSLDOMAINS/home.html', args)

    except Exception as e:
        messages.warning(request, '({}) ERROR! - Invalid Domain | Certificate Expired.'.format(get_domain))
        return redirect(pageDisplay)

def bulkAdd(request):
        if request.method == 'POST':
            get_domain_split = request.POST["get_bulk"]
            get_domains = get_domain_split.splitlines()

            for get_domain in get_domains:
                user = request.user

                try:
                    sslchecker_fmt = str(sslchecker_notA(get_domain))
                    dom_expiry = datetime.datetime.strptime(sslchecker_fmt, '%Y-%m-%d %H:%M:%S')
                    date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    date_now = datetime.datetime.strptime(date_now_fmt, '%Y-%m-%d %H:%M:%S')
                    calc_date = dom_expiry - date_now
                    dom_list = []


                    for check_dom in sslDomain2.objects.all():
                        dom_list.append(check_dom.domain)

                    if get_domain not in dom_list:

                        if calc_date < timedelta(days=0):
                            daysleft = dom_expiry - date_now
                            addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=2,
                                               daysleft=daysleft)
                            addssl.save()
                        elif calc_date <= timedelta(days=14):
                            daysleft = dom_expiry - date_now
                            addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=1,
                                               daysleft=daysleft)
                            addssl.save()
                        else:
                            daysleft = dom_expiry - date_now
                            addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=0,
                                               daysleft=daysleft)
                            addssl.save()

                        query_set = sslDomain2.objects.all()
                        log = "{} : ({}) - Successfully added {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,get_domain)
                        print(log)
                        logsave = logsTable(logs_field=log)
                        logsave.save()
                        query_log = logsTable.objects.all()
                        args = {
                            "object_list"   : query_set,
                            "query_log"     : query_log,
                        }
                        messages.success(request, '({}) Successfully Added!'.format(get_domain))
                    else:
                        query_log = logsTable.objects.all()
                        query_set = sslDomain2.objects.all()
                        messages.warning(request, '({}) already Exist!'.format(get_domain))
                        args = {
                            "object_list"   : query_set,
                            "query_log"     : query_log,
                        }

                except Exception as e:
                    query_log = logsTable.objects.all()
                    query_set = sslDomain2.objects.all()
                    messages.warning(request, '({}) ERROR! - Invalid Domain | Certificate Expired.'.format(get_domain))
                    args = {
                        "object_list"   : query_set,
                        "query_log"     : query_log,
                    }
            return render(request, 'SSLDOMAINS/home.html', args)


def toDelete(request):
    if request.method == 'POST':
        get_id = request.POST["get_id"]
        #to_delete = sslDomain.objects.get(id=get_id)
        to_delete = sslDomain2.objects.get(id=get_id)
        to_delete.delete()
    messages.warning(request, '({}) has been Deleted!'.format(to_delete))
    user = request.user
    log = "{} : ({}) - Successfully deleted {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,to_delete)
    print(log)
    logsave = logsTable(logs_field=log)
    logsave.save()
    return redirect(pageDisplay)
