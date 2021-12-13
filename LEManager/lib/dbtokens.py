SELECT_PRIMARY_DOMAIN_JOIN_SECONDARY_DOMAINS = \
'''
SELECT domains.domain,secondarydomains.domain,domains.lastRenewalDate
FROM domains
LEFT JOIN secondarydomains
ON domains.id = secondarydomains.id
'''

SELECT_PRIMARY_DOMAIN_JOIN_SECONDARY_DOMAINS_BY_DOMAIN = \
'''
SELECT domains.domain,secondarydomains.domain,domains.lastRenewalDate
FROM domains
LEFT JOIN secondarydomains
ON domains.id = secondarydomains.id
WHERE domains.domain = %s
'''