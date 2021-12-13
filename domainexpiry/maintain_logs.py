import sqlite3


def create_connection():
    conn = None
    db_file = 'domain_db.sqlite3'
    todelete = "DELETE from DOMAINEXPIRY where id IN (SELECT id from DOMAINEXPIRY_logstable order by id asc limit 50)"
    try:
        conn = sqlite3.connect(db_file)
        print('connected')

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM DOMAINEXPIRY_logstable")
        count = cur.fetchone()
        # print(count)
        if count[0] > 500:
            cur.execute(todelete)
            conn.commit()
            # print("deleted 10 rows")
            cur.close()
    except sqlite3.Error as e:
        print(e)
    return conn

if __name__=="__main__":
    create_connection()
