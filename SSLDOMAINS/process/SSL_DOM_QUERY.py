# import json, sqlite3

# class SslMonitor():

#     def toQueryDom(self):
#         conn = sqlite3.connect('db.sqlite3')
#         cur = conn.cursor()
#         cur.execute("SELECT domain FROM SSLDOMAINS_ssldomain")
#         b = cur.fetchall()
#         d = {
#             "data": [

#             ]
#         }
#         for new_b in b:
#             d["data"].append({"{#DOMAINS}": new_b[0]})
#         return d


# if __name__=="__main__":
#     a = SslMonitor()
#     print(json.dumps(a.toQueryDom(), indent=4))

