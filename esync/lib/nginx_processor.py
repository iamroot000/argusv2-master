import nginx
import re

from pprint import pprint

### MOVE TO CONFIG FILE
NGINX_INCLUDE_LOC = '/usr/local/nginx/conf.d/include/'


def parse_standard_config(config): #for front end elements
    rConfig = nginx.loads(config).as_dict
    trei = ''

    for i in rConfig['conf']:
        for c,e in enumerate(i['server']):

            for k,v in e.items():
                if 'include' in v:
                    e['include']=re.sub(NGINX_INCLUDE_LOC,'',e['include'])

                if 'rewrite' in v[0]:
                    trei = v[0]['rewrite']
                    
                if 'if' in k and 'http_host' in k:
                    o = re.match(r'if\s*\(\s*\$(http_host)\s*=\s*(\'|\")(.+)(\'|\")\)',k)
                    try:
                        d = re.match(r'(.+)(\s+)(https*:\/\/[a-zA-Z0-9\.\-]+)(.*)',v[0]['rewrite'])
                    except:
                        d = re.match(r'(.+)(\s+)(https*:\/\/[a-zA-Z0-9\.\-]+)(.*)',trei)
                    if o and d:
                        e['redirect'] = {
                            'http_host':o.group(3),
                            'to':d.group(3),
                            'redirect_uri': True if d.group(4) else False
                        }
                        del e[k]

    return rConfig

def create_standard_config(listen,server_name,include_file,redirect_http_host=None,redirect_to=None,certificate=None,privkey=None,redirect_scheme='http'):
    server = nginx.Server()
    params = []
    params.append(nginx.Key('listen', str(listen)))
    params.append(nginx.Key('server_name', server_name))
    rConfig = ''

    if certificate is not None and privkey is not None:
        params.append(nginx.Key('ssl', 'on'))

        #check symbolic links before creating standard config on caller, todo
        params.append(nginx.Key('ssl_certificate', '/usr/local/nginx/conf.d/{0}'.format(certificate)))
        params.append(nginx.Key('ssl_certificate_key', '/usr/local/nginx/conf.d/{0}'.format(privkey)))

    if redirect_to is not None:
        rewrite = '^(.*)$ {0}://'.format(redirect_scheme)

    if redirect_http_host == 'www':
        params.append(nginx.If("($http_host !~* 'www')", nginx.Key('rewrite', '^(.*)$ {0}://www.$http_host$1 permanent'.format(redirect_scheme))))
    elif redirect_http_host is not None:
        params.append(nginx.Key('rewrite', rewrite + redirect_http_host+'$1 permanent'))

    if include_file is not None:
        params.append(nginx.Key('include', '/usr/local/nginx/conf.d/include/{0}'.format(include_file)))

    for param in params:
        server.add(param)
    for i in server.as_strings:
        rConfig += i

    return rConfig

def check_server_block(current_block, http_hosts,listen):
    listen_flag = False
    server_name_flag = False

    for i in re.split(r'server\s+{\s*\n',current_block):
        if i != '':
            for p in i.split('\n'):
                if 'server_name' in p:
                    match = re.match(r'\s+server_name\s+(.+);',p)
                    if match:
                        for a in match.group(1).split(' '):
                            if a in http_hosts:
                                server_name_flag = True

                if 'listen' in p:
                    match = re.match(r'\s+listen\s+(.+);', p)
                    if match:
                        if isinstance(listen, list):
                            if match.group(1) in listen:
                                listen_flag = True
                        else:
                            if listen == match.group(1):
                                listen_flag = True

    if listen_flag == True and server_name_flag == True:
        return True
    return False

def rewrite_server_block(current_block, http_hosts,listen):
    remove = ''
    remain = ''
    for i in re.split(r'server\s+{\s*\n',current_block):
        listen_flag = False
        server_name_flag = False

        if i != '':
            bl = 'server {'
            for p in i.split('\n'):
                if 'server_name' in p:
                    match = re.match(r'\s+server_name\s+(.+);', p)
                    if match:
                        for a in match.group(1).split(' '):
                            if a in http_hosts:
                                server_name_flag = True
                if 'listen' in p:
                    match = re.match(r'\s+listen\s+(.+);', p)
                    if match:
                        if isinstance(listen, list):
                            if match.group(1) in listen:
                                listen_flag = True
                        else:
                            if listen == match.group(1):
                                listen_flag = True
                bl += '\n' + p

            if listen_flag and server_name_flag:
                remove += bl
            else:
                remain += bl

    return remove,remain


def list_server_block(block,multiple80443=False):
    rVal=[]
    server_names = []
    blocks ={}
    if multiple80443:
        for i in re.split(r'server\s+{\s*\n', block):
            if i != '':
                '''print i
                match = re.match(r'server_name\s+(.+);',i)
                if match:
                    if match.group(1) not in server_names:
                        server_names.append(match.group(1))'''

                rx_sequence = re.compile(r"server_name\s+(.+);", re.MULTILINE)

                for match in rx_sequence.finditer(i):
                    print match.group(1)
    else:
        for i in re.split(r'server\s+{\s*\n', block):
            if i != '':
                bl = 'server {'
                for p in i.split('\n'):
                    bl += '\n' + p

                rVal.append(bl)
    return rVal

