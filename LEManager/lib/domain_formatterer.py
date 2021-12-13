

def subdomain_formatter(domain,subdomains):
    '''
    :param subdomains: '\n' delimited subdomains STR
    :return: Validated list of Subdomains LIST
    '''
    sub = [line for line in subdomains.split('\n') if line.strip() != '']
    for i in sub:
        if i != domain and not i.endswith('.{0}'.format(domain)):
            return False,i

    return True,sub