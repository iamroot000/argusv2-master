import sqlite3


def create_connection():
    conn = None
    db_file = 'ssl_db.sqlite3'
    todelete = "DELETE from SSLDOMAINS_logstable where id IN (SELECT id from SSLDOMAINS_logstable order by id asc limit 50)"
    try:
        conn = sqlite3.connect(db_file)
        print('connected')

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM SSLDOMAINS_logstable")
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
