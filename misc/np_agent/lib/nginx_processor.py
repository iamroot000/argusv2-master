
import nginx

def server_block(port,hostname,rewrite=None,include=None,SSL=None):
    '''
    :param port: Listening Port Number
    :param host: LIST of hostnames
    :param rewrite: LIST[0] hostname for condition ,LIST[1] Destination rewrite FULL URL
    :param https_cn: DICT['dir'] DICT['certpem'] DICT['privkeypem']
    :return: LIST conf for host
    '''
    server = nginx.Server()
    params = []
    params.append(nginx.Key('listen',str(port)))
    params.append(nginx.Key('server_name',hostname))

    if SSL is not None and port == 443:
        params.append(nginx.Key('ssl','on'))

        if not 'certpem' in SSL or not 'privkeypem' in SSL:
            raise Exception('Missing params in SSL')


        params.append(nginx.Key('ssl_certificate','/usr/local/nginx/conf.d/ssl/{certpem}'.format(**SSL)))
        params.append(nginx.Key('ssl_certificate_key', '/usr/local/nginx/conf.d/ssl/{privkeypem}'.format(**SSL)))

    if rewrite is not None:
        if rewrite[0] is None:
            params.append(nginx.Key('rewrite','^(.*)$ {0}$1'.format(rewrite[1])))
        else:
            if rewrite[0] == hostname:
                params.append(nginx.If("$http_host = '{0}'".format(rewrite[0]),nginx.Key('rewrite','^(.*)$ {0}$1'.format(rewrite[1]))))

    if include is not None:
        params.append(nginx.Key('include','/usr/local/nginx/conf.d/include/{0}'.format(include)))

    for param in params:
        server.add(param)
    return server.as_strings

