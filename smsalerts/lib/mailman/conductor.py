
import mysql.connector
from conductor_h import *

import datetime




isBitSet = lambda a,b: True if (a & b) else False

'''
flags:
64 - goodbye message, counted as inactive and instantly deleted on retrieve


'''

class operator(object):
    def __init__(self,dbkwakwa):
        self.__dbconf = dbkwakwa;
        conn = mysql.connector.connect(**dbkwakwa);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL)
        c = conn.cursor();
        #c.execute(CREATE_TABLE_CONTACT);
        #c.execute(CREATE_TABLE_GROUP);
        #c.execute(CREATE_TABLE_MEMBERSHIP);
        #c.execute(CREATE_TABLE_MESSAGEQUEUE);
        #conn.commit();
        conn.close();

    def getGroupMembers(self,group_name):

        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_GROUP_MEMBERS,(group_name,));
            #rVal = [i[0] for i in c.fetchall()];
            rVal = c.fetchall();
            conn.commit();
            return rVal;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def getGroups(self):

        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_GROUP_NAMES_LIST);
            rVal = [i[0] for i in c.fetchall()];
            conn.commit();
            return rVal;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def getContactNumber(self,contact_id):

        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_PHONE_NUMBER_BY_ID, (contact_id,));
            rVal = c.fetchone();
            conn.commit();
            return rVal;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def addAnnouncement(self,group_name,message,frequency=10,flags=0):

        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_GROUP_ID,(group_name,));
            group_id = c.fetchone()
            c.execute(INSERT_ANNOUNCEMENT,(group_id[0],message,"1990-01-01 00:00:00",frequency,flags));#datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.commit();
            return True;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def retrievePendingAnnouncements(self): #flag 64 is delete on retrieve.
        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_PENDING_ANNOUNCEMENTS);
            rVal = c.fetchall(); #MessageQueue.id, Groups.id, Groups.name, MessageQueue.message, MessageQueue.freq_minutes, MessageQueue.flags
            #refresh awkwardly, todo: update instead
            for i in rVal:
                c.execute(DELETE_ANNOUNCEMENT_BY_ID,(i[0],));
                if not isBitSet(int(i[5]),64):
                    c.execute(INSERT_ANNOUNCEMENT,(i[1],i[3],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),i[4],i[5]));
            conn.commit();
            return rVal;
        except Exception as e:
            import traceback
            print traceback.format_exc()
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def showActiveAnnouncements(self):
        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_ANNOUNCEMENTS);
            rVal = c.fetchall();
            #MessageQueue.id, Groups.name, MessageQueue.message, MessageQueue.lastSent, MessageQueue.freq_minutes, MessageQueue.flags
            rVal = [(i[0],i[1],i[2],i[3].strftime("%Y-%m-%d %H:%M:%S"),i[4]) for i in rVal if not isBitSet(i[5],64)]
            conn.commit();
            return rVal;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();

    def endAnnouncement(self,announcement_id):
        conn = mysql.connector.connect(**self.__dbconf);
        conn.start_transaction(isolation_level=DEFAULT_ISOLATION_LEVEL);
        c = conn.cursor();
        try:
            c.execute(SELECT_ANNOUNCEMENTS_BY_ID,(announcement_id,));
            rVal = c.fetchone();
            c.execute(DELETE_ANNOUNCEMENT_BY_ID,(announcement_id,));
            conn.commit();
            return rVal;
        except Exception as e:
            print "Failure: %s" % e;
            conn.rollback();
        finally:
            conn.close();



