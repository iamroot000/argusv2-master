import requests, logging, datetime, json, sqlite3, time, pytz, mysql.connector, os






class MYSQLquery():
    def __init__(self):
        self.mydb_host = "localhost"
        self.mydb_db = "argus"
        self.mydb_user = "root"
        self.mydb_pass = "VA1913wm"
        self.mydb_table1 = "domains_domain"
        self.mydb_table2 = "domains_account"
        self.mydb_t1_c1 = "account_id"
        self.mydb_t1_c2 = "domain"
        self.mydb_t2_c1 = "business_id"
        self.mydb_t2_c2 = "username"
        self.mydb_conn = mysql.connector.connect(host=self.mydb_host, database=self.mydb_db, user=self.mydb_user, passwd=self.mydb_pass)
        self.cursor = self.mydb_conn.cursor()

    def domain_list(self):
        params = ("CDN",)
        self.cursor.execute(
            "SELECT {0}.{1},{2}.{3} FROM {0} INNER JOIN {2} ON {0}.{4} = {2}.{5} WHERE {2}.{3}=%s".format(self.mydb_table1, self.mydb_t1_c2,
                                                                                         self.mydb_table2, self.mydb_t2_c1,
                                                                                         self.mydb_t1_c1, self.mydb_t2_c2), params)
        mydb_out = self.cursor.fetchall()
        return mydb_out



    def domain_product(self):
        self.cursor.execute("SELECT {} FROM {}".format(self.mydb_t2_c1, self.mydb_table2))
        mydb_out = self.cursor.fetchall()
        product_list = []
        for product in mydb_out:
            product_list.append(product[0])
        return product_list


class DomainSystem():
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sqldir = os.path.join(BASE_DIR, 'CDNCHECKER/CDNdomain.sqlite3')
        self.db_table = "CDNCHECKER_domainchecker"
        self.db_columid = "id"
        self.db_columnp = "product"
        self.db_column1 = "domains"
        self.db_column2 = "status"
        self.db_column3 = "lastcheck"
        self.db_column4 = "forcecheck"
        self.db_conn = sqlite3.connect(sqldir)
        self.cursor = self.db_conn.cursor()


    def loggingFile(self,log_debug=None,log_info=None,log_warning=None,log_error=None,log_critical=None):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logdir = os.path.join(BASE_DIR, 'CDNCHECKER/logs/')
        os.popen("find {0} -type f -name '*.log' -mtime +7 -exec rm {1} \;".format(logdir,''))
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(
                filename='{}domainchecker-{}.log'.format(logdir, datetime.datetime.now().strftime("%Y-%m-%d-%H")),
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


    def domain_status(self,specific_domain, domain_timeout=10, domain_delay=5):
        try:
            r = requests.get(
            "http://v.juhe.cn/siteTools/app/NewDomain/query.php?key=0066ee95da11143ef165f348ccd105a8&domainName={0}".format(
               specific_domain), timeout=domain_timeout)
            r = json.loads(r.text)
            self.loggingFile(log_debug="{}".format("#####"*len(r)))
            self.loggingFile(log_debug="DOMAIN STATUS",log_info=r)
            time.sleep(domain_delay)
            if not r["result"]:
                msg = "ERROR"
                self.loggingFile(log_error="{} - The result is null.".format(msg))
                return msg
            else:
                msg = "OK"
                return msg
        except Exception as e:
            msg = "TIMEOUT"
            self.loggingFile(log_debug="{}".format("#####" * len(str(e))))
            self.loggingFile(log_debug="DOMAIN STATUS", log_info=str(e), log_critical="{} - Connection Timeout.".format(str(e)))
            return msg



    def domain_store(self):
        try:
            mysql_q = MYSQLquery()
            self.db_conn.execute("CREATE TABLE {}({} INTEGER PRIMARY KEY, {}, {} TEXT, {} TEXT, {} TEXT, {} TEXT)".format(self.db_table, self.db_columid, self.db_columnp, self.db_column1, self.db_column2, self.db_column3, self.db_column4))
            self.loggingFile(log_debug="DOMAIN STORE",log_info="Database has been created. TABLE={}, FIELD={},{},{},{},{},{}".format(self.db_table,self.db_columid,self.db_columnp,self.db_column1,self.db_column2,self.db_column3,self.db_column4))
            self.db_conn.commit()
            for domain, product in mysql_q.domain_list():
                d_status = self.domain_status(domain, domain_timeout=10, domain_delay=4)
#                params = (product, domain, d_status, str(datetime.datetime.now(pytz.timezone('Asia/Manila')).strftime("%Y-%m-%d %H:%M:%S.%f")).split('+')[0],"---")
                params = (product, domain, d_status, str(datetime.datetime.now()).split('+')[0],"---")
                self.db_conn.execute("INSERT INTO {0}({1},{2},{3},{4},{5}) VALUES (?, ?, ?, ?, ?)".format(self.db_table,self.db_columnp,self.db_column1,self.db_column2,self.db_column3,self.db_column4), params)
                self.loggingFile(log_info="{} has been included to the database - PARAMS={}".format(domain,params))
                self.db_conn.commit()
            self.db_conn.close()
            return "Successfully created database and adding data."
        except Exception as e:
            self.loggingFile(log_warning=str(e))
            self.cursor.execute("SELECT {0} FROM {1}".format(self.db_column1,self.db_table))
            d_list_tuple = self.cursor.fetchall()
            for d_list in d_list_tuple:
                d_status = self.domain_status(d_list[0], domain_timeout=10, domain_delay=4)
                params = (str(d_status), str(datetime.datetime.now(pytz.timezone('Asia/Manila'))).split('+')[0],"---",str(d_list[0]))
                self.cursor.execute("UPDATE {0} SET {1}=?, {2}=?, {3}=? WHERE {4}=? ".format(self.db_table,self.db_column2,self.db_column3,self.db_column4,self.db_column1), params)
                self.loggingFile(log_info="{} has been updated to the database - PARAMS={}".format(d_list,params))
                self.db_conn.commit()
            self.db_conn.close()
            return "{}. Updating database done".format(e)


    def domain_forcecheckID(self,f_ID,f_domain_columnid="id",f_table="CDNCHECKER_domainchecker",f_domain_column4="forcecheck"):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sqldir = os.path.join(BASE_DIR, 'CDNCHECKER/CDNdomain.sqlite3')
        self.loggingFile(log_debug="==================================")
        self.loggingFile(log_debug="FORCE CHECK")
        db_conn = sqlite3.connect(sqldir)
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM {} WHERE {}=?".format(f_table,f_domain_columnid), (int(f_ID),))
        d_list_tuple = cursor.fetchall()[0]
        f_check_str = self.domain_status(d_list_tuple[0]) + " - " + str(datetime.datetime.now(pytz.timezone('Asia/Manila'))).split('+')[0]
        cursor.execute("UPDATE {0} SET {1}=? WHERE {2}=? ".format(f_table, f_domain_column4, f_domain_columnid),(f_check_str, int(f_ID)))
        self.loggingFile(log_info="ID-{} has been updated to the database - OUTPUT=({})".format(f_ID,f_check_str))
        db_conn.commit()
        db_conn.close()
        return f_check_str







if __name__ == "__main__":
    test = DomainSystem()
    test.domain_store()
    












