# import socket, ssl, datetime, sys

# def sslcheckerOut(dom, port=443, timeout=None):
#     try:
#         with socket.create_connection((dom, port), timeout=timeout) as sock:
#             context = ssl.create_default_context()
#             with context.wrap_socket(sock, server_hostname=dom) as sslsock:
#                 getssl = sslsock.getpeercert()
#                 changedt_format = getssl['notAfter']
#                 to_format = ssl.cert_time_to_seconds(changedt_format)
#                 new_ssldt_format = datetime.datetime.fromtimestamp(to_format)
#                 dom_exp = new_ssldt_format
#                 date_now = datetime.datetime.now()

#                 if dom_exp <= date_now:
#                     return 1
#                 else:
#                     return 0
#     except Exception as e:
#         return e

# try:
#     print(sslcheckerOut(sys.argv[1]))
# except Exception as e:
#     print(e)