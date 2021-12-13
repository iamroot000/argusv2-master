import nginx
import re


def parse_standard_config(config):  # for front end elements

    NGINX_INCLUDE_LOC = '/usr/local/nginx/conf.d/include/'
    rConfig = nginx.loads(config).as_dict
    print(rConfig)

    for i in rConfig['conf']:
        for c, e in enumerate(i['server']):

            for k, v in e.items():
                if 'include' in v:
                    e['include'] = re.sub(NGINX_INCLUDE_LOC, '', e['include'])

                if 'if' in k and 'http_host' in k:
                    o = re.match(r'if\s*\(\s*\$(http_host)\s*=\s*(\'|\")(.+)(\'|\")\)', k)
                    d = re.match(r'(.+)(\s+)(https*:\/\/[a-zA-Z0-9\.\-]+)(.*)', v[0]['rewrite'])
                    if o and d:
                        e['redirect'] = {
                            'http_host': o.group(3),
                            'to': d.group(3),
                            'redirect_uri': True if d.group(4) else False
                        }
                        del e[k]

    return rConfig


if __name__ == "__main__":
    config = """
    server {
    listen 80;
    server_name .xbet29.com www.xbet29.com;
    #rewrite ^(.*)$ https://$http_host$1 redirect;
    return      301 https://$http_host$1;


    }

    server {
        listen 80;
        server_name 58202.vip www.58202.vip;
        # rewrite ^(.*)$ https://www.58202.vip$1 permanent;
    }
    
    server {
        listen 443;listen 8188;
        server_name 58202.vip www.58202.vip;
        ssl on;
        ssl_certificate /usr/local/nginx/conf.d/ssl/58202.vip/fullchain.pem;
        ssl_certificate_key /usr/local/nginx/conf.d/ssl/58202.vip/privkey.pem;
    
        if ($http_host !~* 'www') {
            rewrite ^(.*)$ https://www.$http_host$1 permanent;
        }
    
        include /usr/local/nginx/conf.d/include/xbet_official_masterconfig.include;
    }

    """

    print(parse_standard_config(config))
