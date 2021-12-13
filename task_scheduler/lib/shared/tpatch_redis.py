from celery.result import AsyncResult;
from celery.app import base
from celery.exceptions import TimeoutError;

from multiprocessing import Queue, Process
import traceback
orig = AsyncResult.get;
orig_sendtask = base.Celery.send_task;

class exceptionobj(object):
    def __init__(self,msg):
        self.__str = msg;

    def getstr(self):
        return self.__str

def hookAsyncResultGet(*args, **kwargs):
    q = Queue();
    def __run(qwewe, *args,**kwargs):
        try:
            res = orig(*args,**kwargs);
        except:
            res = exceptionobj(traceback.format_exc())
        qwewe.put(res);
        qwewe.close()
    p = Process(target=__run,args=(q,) + args,kwargs=kwargs);
    p.start();

    rVal = q.get();
    q.close()
    del q
    if type(rVal) == exceptionobj:
        print rVal.getstr()
        return None
    del p;
    return rVal;


def hookSendTask(*args, **kwargs):
    q = Queue();
    def __run(qwewe, *args,**kwargs):
        try:
            res = orig_sendtask(*args,**kwargs);
        except:
            res = exceptionobj(traceback.format_exc())
        qwewe.put(res);
        qwewe.close()
    p = Process(target=__run,args=(q,) + args,kwargs=kwargs);
    p.start();

    rVal = q.get();
    q.close()
    del q
    if type(rVal) == exceptionobj:
        print rVal.getstr()
        return None;
    del p;
    return rVal;

AsyncResult.get = hookAsyncResultGet;
base.Celery.send_task = hookSendTask;