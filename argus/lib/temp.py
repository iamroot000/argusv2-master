from celery.result import AsyncResult;
from celery.app import base
from celery.exceptions import TimeoutError;

from multiprocessing import Queue, Process
orig = AsyncResult.get;
orig_sendtask = base.Celery.send_task;

def failthread2(*args,**kwargs):
    q = Queue();
    def __run(*args,**kwargs):
        q.put(orig(*args,**kwargs));
    p = Process(target=__run,args=args,kwargs=kwargs);
    p.start();

    rVal = q.get();
    del p;
    return rVal;

def failthread25(*args,**kwargs):
    q = Queue();
    def __run(*args,**kwargs):
        q.put(orig_sendtask(*args,**kwargs));
    p = Process(target=__run,args=args,kwargs=kwargs);
    p.start();

    rVal = q.get();
    del p;
    return rVal;

AsyncResult.get = failthread2;
base.Celery.send_task = failthread25;