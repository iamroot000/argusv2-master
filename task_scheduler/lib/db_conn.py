import mysql.connector
from defs import DATABASES

dbkwakwa = {
        "host": DATABASES['HOST'],
        "database": DATABASES['NAME'],
        "user": DATABASES['USER'],
        "password": DATABASES['PASSWORD'],
        "charset": "utf8",
    }

SELECT_BUSINESS_UNITS_DOMAIN_CHECK = \
'''
SELECT business_unit
FROM core_business_unit
WHERE domain_status_check = 1
'''

SELECT_BUSINESS_UNITS_PMS = \
'''
SELECT business_unit
FROM core_business_unit
WHERE pms_product_code != NULL
'''

SELECT_DOMAIN_BY_BUSINESS_UNIT = \
'''
SELECT domain, tag,tag_type
FROM domainmngr_domain_tag
WHERE tag_type = "BU"
AND
tag=%s
'''


SELECT_DOMAIN_BY_DOMAIN_FILTER_BUSINESS_UNIT = \
'''
SELECT domain, tag,tag_type
FROM domainmngr_domain_tag
WHERE tag_type = "DTYPE"
AND
domain IN (%s)
'''

SELECT_DOMAIN_BY_DOMAIN_FILTER_BUSINESS_UNIT = \
'''
SELECT domain, tag,tag_type
FROM domainmngr_domain_tag
WHERE tag_type = "DTYPE"
AND
domain IN (%s)
'''
SELECT_CHANNELS_PROXYCONTROLLER  = \
'''
SELECT celery_queue
FROM proxycontroller_channel
'''


class conn(object):

    def getbusinessunits(self):
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        c.execute(SELECT_BUSINESS_UNITS_DOMAIN_CHECK);
        rVal = c.fetchall();
        conn.commit()
        conn.close();
        business_unit = []
        for b in rVal:
            business_unit.append({'business_unit': b[0]})
        return business_unit;

    def getbusinessunits_midpay(self):
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        c.execute(SELECT_BUSINESS_UNITS_PMS);
        rVal = c.fetchall();
        conn.commit()
        conn.close();
        business_unit = []
        for b in rVal:
            business_unit.append({'business_unit': b[0]})
        return business_unit;
    def getDomainTags(self,business_unit):
        ret = []
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        c.execute(SELECT_DOMAIN_BY_BUSINESS_UNIT,(business_unit['business_unit'],));
        bu = c.fetchall();
        conn.commit()

        t = None
        for i in bu:
            ret.append({
                'domain':i[0],
                'tag': i[1],
                'tag_type':i[2]
            })

            if not t:
                t = '%s'
            else:
                t = t + ' ,%s'
        c.execute(SELECT_DOMAIN_BY_DOMAIN_FILTER_BUSINESS_UNIT % t,tuple([i[0] for i in bu]));
        dtype = c.fetchall();

        for i in dtype:
            ret.append({
                'domain': i[0],
                'tag': i[1],
                'tag_type': i[2]
            })

        conn.close();
        return ret;

    def getProxyControllerChannels(self):
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        c.execute(SELECT_CHANNELS_PROXYCONTROLLER);
        rVal = c.fetchall();
        conn.commit()
        conn.close();
        channels = []
        for b in rVal:
            channels.append( b[0])
        return channels;
