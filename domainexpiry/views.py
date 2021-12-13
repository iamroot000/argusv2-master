from django.shortcuts import render, redirect
from .domainexpiry import domainchecker_notA
from .models import *
from django.contrib import messages
import datetime
from datetime import timedelta
import logging, os

# Create your views here.

def loggingFile(log_debug=None, log_info=None, log_warning=None, log_error=None, log_critical=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logdir = os.path.join(BASE_DIR, 'domainexpiry/logs/')
    os.popen("find {0} -type f -name '*.log' -mtime +7 -exec rm {1} \;".format(logdir,''))
    LOG_FORMAT = "%(asctime)s %(levelname)s - %(message)s"
    logging.basicConfig(
            filename='{}domainexpiry-{}.log'.format(logdir, datetime.datetime.now().strftime("%Y-%m-%d-%H")),
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
    query_set = domainExpiry.objects.all()
    date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_now = datetime.datetime.strptime(date_now_fmt, '%Y-%m-%d %H:%M:%S')



    user = request.user

    query_log = logsTable.objects.all()
    args = {
        "object_list"   : query_set,
        "query_log"     : query_log
    }
    return render(request, 'domainexpiry/home.html', args)


def bulkAddDomain(request):
    # try:
        if request.method == 'POST':
            get_domain_split = request.POST["get_bulk"]
            get_tag = request.POST["get_tag"]
            get_domains = get_domain_split.splitlines()
            get_domains = [str(i) for i in get_domains]
            
            print get_domains
            for get_domain in get_domains:
                user = request.user

                try:
                    domainexpiry_fmt = str(domainchecker_notA(get_domain))
                    dom_expiry = datetime.datetime.strptime(domainexpiry_fmt, "%Y-%m-%d %H:%M:%S")
                    date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    date_now = datetime.datetime.strptime(date_now_fmt, "%Y-%m-%d %H:%M:%S")
                    calc_date = dom_expiry - date_now
                    dom_list = []


                    for check_dom in domainExpiry.objects.all():
                        dom_list.append(check_dom.domain)

                    if get_domain not in dom_list:

                        if calc_date < timedelta(days=0):
                            daysleft = dom_expiry - date_now
                            adddomain = domainExpiry(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=2,
                                            daysleft=daysleft,renewal=1,tag=get_tag)
                            adddomain.save()
                        elif calc_date <= timedelta(days=30):
                            daysleft = dom_expiry - date_now
                            adddomain = domainExpiry(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=1,
                                            daysleft=daysleft,renewal=1,tag=get_tag)
                            adddomain.save()
                        else:
                            daysleft = dom_expiry - date_now
                            adddomain = domainExpiry(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=0,
                                            daysleft=daysleft,renewal=1,tag=get_tag)
                            adddomain.save()

                        query_set = domainExpiry.objects.all()
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
                        query_set = domainExpiry.objects.all()
                        messages.warning(request, '({}) already Exist!'.format(get_domain))
                        args = {
                            "object_list"   : query_set,
                            "query_log"     : query_log,
                        }

                except Exception as e:
                    print e
                    query_log = logsTable.objects.all()
                    query_set = domainExpiry.objects.all()
                    messages.warning(request, '({}) ERROR! - Invalid Domain'.format(get_domain))
                    args = {
                        "object_list"   : query_set,
                        "query_log"     : query_log,
                    }
            return render(request, 'domainexpiry/home.html', args)

def toDeleteDomain(request):
    if request.method == 'POST':
        get_id = request.POST["get_id"]
        to_delete = domainExpiry.objects.get(id=get_id)
        to_delete.delete()
    messages.warning(request, '({}) has been Deleted!'.format(to_delete))
    user = request.user
    log = "{} : ({}) - Successfully deleted {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,to_delete)
    print(log)
    logsave = logsTable(logs_field=log)
    logsave.save()
    return redirect(pageDisplay)


def toRenew(request):
    if request.method == 'POST':
        get_id = request.POST["get_id"]
        to_renew = domainExpiry.objects.get(id=get_id)
        user = request.user
        if to_renew.renewal == 1:
            to_renew.renewal = 0
            to_renew.save()

            query_set = domainExpiry.objects.all()
            log = "{} : ({}) - Successfully updated {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,to_renew)
            logsave = logsTable(logs_field=log)
            logsave.save()
            query_log = logsTable.objects.all()
            args = {
                "object_list"   : query_set,
                "query_log"     : query_log,
            }
            messages.success(request, '({}) Successfully Updated!'.format(get_id))
            return render(request, 'domainexpiry/home.html', args)

        else:
            to_renew.renewal = 1
            to_renew.save()

            query_set = domainExpiry.objects.all()
            log = "{} : ({}) - Successfully updated {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user,to_renew)
            print(log)
            logsave = logsTable(logs_field=log)
            logsave.save()
            query_log = logsTable.objects.all()
            args = {
                "object_list"   : query_set,
                "query_log"     : query_log,
            }
            messages.success(request, '({}) Successfully Updated!'.format(get_id))
            return render(request, 'domainexpiry/home.html', args)
    
    return redirect(pageDisplay)