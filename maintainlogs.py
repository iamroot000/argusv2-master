import os, sqlite3, logging, datetime, mysql.connector,sys,json, time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from  argus.defs.datasources import *

class DeleteHistory():
    def __init__(self, db_table="SSRCHECKER", db_file="SSRchecker.sqlite3", db_max_del=1, db_max_limit=1, db_field=["SSRhomehistoryModel"]):
        self.mydb_host = DATABASES["argus_v2_db"]["HOST"]
        self.mydb_db = DATABASES["argus_v2_db"]["NAME"]
        self.mydb_user = DATABASES["argus_v2_db"]["USER"]
        self.mydb_pass = DATABASES["argus_v2_db"]["PASSWORD"]
        self.db_table = db_table
        self.db_field = db_field
        self.db_file = os.path.join(BASE_DIR, '{}/{}'.format(self.db_table, db_file))
        self.db_max_del = db_max_del
        self.db_max_limit = db_max_limit
        # self.db_table = "SSRCHECKER"
        # self.db_field = ["SSRinithistoryModel", "SSRconfighistoryModel", "SSRmasterconfighistoryModel","SSRhomehistoryModel"]
        # self.db_file = os.path.join(BASE_DIR, '{}/SSRchecker.sqlite3'.format(self.db_table))
        # self.db_max_del = 1
        # self.db_max_limit = 1



    def loggingFile(self, log_debug=None, log_info=None, log_warning=None, log_error=None, log_critical=None, log_close=False):
        logdir = os.path.join(BASE_DIR, '{}/logs/'.format(self.db_table))
        check_dir = os.path.exists(logdir)
        if not check_dir: 
            os.popen("mkdir {}".format(logdir))
        os.popen("find {0} -type f -name '*.log' -mtime +30 -exec rm {1} \;".format(logdir, '{}'))
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        # logging.basicConfig(
        #     filename='{}{}-{}.log'.format(logdir, self.db_table ,datetime.datetime.now().strftime("%Y-%m-%d-%H")),
        #     format=LOG_FORMAT, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename='{}{}-{}.log'.format(logdir, self.db_table ,datetime.datetime.now().strftime("%Y-%m-%d-%H")))
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt=LOG_FORMAT
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)


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
        # if log_close:
        logger.removeHandler(fh)
        del logger, fh


    def db_connection(self, conn_sql=False):
        conn = None
        for del_data in self.db_field:
            db_table_f = "{}_{}".format(self.db_table, del_data.lower())
            if conn_sql is True or conn_sql == "True":
                todelete = "DELETE FROM {0} ORDER BY id ASC limit {1}".format(db_table_f, self.db_max_del)
            else:
                todelete = "DELETE from {0} where id IN (SELECT id from {0} order by id asc limit {1})".format(db_table_f, self.db_max_del)

            try:
                if conn_sql is True or conn_sql == "True":
                    conn = mysql.connector.connect(host=self.mydb_host, database=self.mydb_db, user=self.mydb_user, passwd=self.mydb_pass)
                    self.loggingFile(log_debug="{}".format("#####" * 5))
                    self.loggingFile(log_debug="{} STATUS".format(self.db_table), log_info="connected to mysql")
                else:
                    conn = sqlite3.connect(self.db_file)
                    self.loggingFile(log_debug="{}".format("#####" * 5))
                    self.loggingFile(log_debug="{} STATUS".format(self.db_table), log_info="connected to sqlite3")
                self.loggingFile(log_info="table_name = {}".format(db_table_f))
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM {}".format(db_table_f))
                count = cur.fetchone()
#                print(count)

                if count[0] >= int(self.db_max_limit):
                    cur.execute(todelete)
                    conn.commit()
                    self.loggingFile(log_info="db_count = {}".format(count[0]))
                    self.loggingFile(log_info="db_count_limit = {}".format(self.db_max_limit))
                    self.loggingFile(log_info="db_count_delete = {}".format(self.db_max_del))
                else:
                    self.loggingFile(log_info="ignore = db_count({}) less than db_count_limit({})".format(count[0], self.db_max_limit))
            except Exception as e:
                self.loggingFile(log_error="{}".format(str(e)))
        cur.close()
        self.loggingFile(log_close=True)
        return conn

if __name__=="__main__":
    data_file = open(os.path.join(BASE_DIR, 'maintainlogs.json'), 'r')
    data = json.load(data_file)
    for key, value in data.items():
        DeleteHistory(db_table=key,db_file=value["db_file"],db_max_del=value["db_max_del"],db_max_limit=value["db_max_limit"],db_field=value["db_field"]).db_connection(conn_sql=value["db_conn"])


