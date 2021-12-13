from argus.celery import app
import time


ANSIBLE_WORKER = "initiald_worker"
logFile = "cloud_standard_16.162.191.217-2021-09-06-10.log"
CELERY_HOSTNAME = "ansible-207-initializer"
def servertasks():
    test = app.send_task('{0}.ansibleReadlog'.format(ANSIBLE_WORKER),
                  args=(logFile,),
                  # kwargs={
                  #     'start': int(offset)
                  # },
                  queue='{0}-q'.format(CELERY_HOSTNAME))
    # test = app.send_task('celery_test.testing', args=['/home/ubuntu/Desktop/'], kwargs={})
    data = test.get()
    test.forget()
    return data

if __name__ == "__main__":
    print(servertasks())
