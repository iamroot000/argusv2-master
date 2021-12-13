from celery import Celery

from lib.defs import *
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL
app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

from lib.eye_data import EYE_DATA

EYE_DATA = EYE_DATA(REDIS_HOST,
                    REDIS_PORT,
                    REDIS_DBINDEX,
                    password=REDIS_PASSWORD,
                    pmscredentials = PMSCREDENTIALS)

@app.task
def resolve_domains(orm_data,cmdb_data,business_unit):
    return EYE_DATA.domainPerServerCheck(orm_data, cmdb_data, business_unit=business_unit.upper())

@app.task
def acquire_domain_config(business_unit,task_res):
    return EYE_DATA.domainPerConfigCheck(business_unit,task_res)

@app.task
def midpay_domain_check(business_units):
    return EYE_DATA.midpayDomainCheck(business_units)