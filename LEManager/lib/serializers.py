import json
from pprint import pprint
import datetime
import pytz
tz = pytz.timezone('Asia/Hong_Kong')

def overview_s(data,activity):
    rVal = []
    temp = []
    store ={}


    for i in activity:

        if i['domain'] not in store:
            store[i['domain']]={
                'created_on':i['created_on']
            }

        else:
            if store[i['domain']]['created_on'] < i['created_on']:
                store[i['domain']]={
                    'created_on': i['created_on']
                }


    for i in data:

        if i[0] not in temp:
            temp.append(i[0])

            la = ''

            if i[0] in store:
                la = '{0}'.format((store[i[0]]['created_on']+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))

            rVal.append(
                {
                    'CN':i[0],
                    'alt':[i[1]],
                    'updated': i[2].strftime("%Y-%m-%d"),
                    'last_activity':la

                }
            )
        else:
            for t,p in enumerate(rVal):
                if p['CN'] == i[0]:
                    rVal[t]['alt'].append(i[1])


    return rVal

def pending_s(data):
    rVal=[]

    if data:
        for i in list(data):

            rVal.append({
                'domain':i['domain'],
                'activity': i['activity'],
                'created_on':i['created_on'].astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            })
        return rVal
    return None