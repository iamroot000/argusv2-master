import mysql.connector
from argus.defs.datasources import LEmoria_DB
from dbtokens import *


dbkwakwa = {
    "host" : LEmoria_DB['DB_HOST'],
    "database" : LEmoria_DB['DB_NAME'],
    "user" : LEmoria_DB['DB_USER'],
    "password" : LEmoria_DB['DB_PASS'],
    "charset" : "utf8",
}

class conn(object):

    def getDomainCompleteList(self):
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        try:
            c.execute(SELECT_PRIMARY_DOMAIN_JOIN_SECONDARY_DOMAINS);
            rVal = c.fetchall();
            conn.commit();
        except Exception as e:
            print "getDomainCompleteList: %s" % e;
            conn.rollback();
            rVal = None;
        conn.close();
        return rVal;

    def getDomain(self,domain):
        conn = mysql.connector.connect(**dbkwakwa);
        c = conn.cursor();

        try:
            c.execute(SELECT_PRIMARY_DOMAIN_JOIN_SECONDARY_DOMAINS_BY_DOMAIN,(domain,));
            rVal = c.fetchall();
            conn.commit();
        except Exception as e:
            print "getDomain: %s" % e;
            conn.rollback();
            rVal = None;
        conn.close();
        return rVal;