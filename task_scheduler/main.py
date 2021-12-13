from lib.scheduler import SCHEDULER
from lib.defs import *
#
#import gevent.monkey

#gevent.monkey.patch_thread()

#monkeypatch print
def log():
    import sys
    from lib.shared import log
    log.flush = sys.stdout.flush
    log.write = log.info
    sys.stdout = log;

log()

if __name__ == '__main__':
    SCHEDULER = SCHEDULER()
