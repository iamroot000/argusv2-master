from celery import Celery
from ssObject import socketFactory



REDIS_HOST = '10.168.11.216'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL
app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

CHANNEL_NAME = 'ssrpc1'

SF = socketFactory(CHANNEL_NAME)

@app.task(name='proxycontroller.get_ports')
def get_ports(**kwargs): return SF.get_ports(**kwargs)

@app.task(name='proxycontroller.create_port')
def create_port(*args,**kwargs): return SF.create_port(*args,**kwargs)

@app.task(name='proxycontroller.restart_port')
def restart_port(*args): return SF.restart_port(*args)

@app.task(name='proxycontroller.stop_port')
def stop_port(*args): return SF.stop_port(*args)

@app.task(name='proxycontroller.get_logs')
def get_logs(*args): return SF.get_logs(*args)

@app.task(name='proxycontroller.get_isp')
def get_isp(): return SF.get_isp()


if __name__ == '__main__':
    from celery.bin import worker
    werker = worker.worker(app=app);

    options = {
        "loglevel" : "DEBUG",
        "traceback" : True,
        "queues" : CHANNEL_NAME,
        "concurrency" : 4,
        "hostname" : 'PROXY_CONTROLLER_WORKER'
    }
    werker.run(**options)