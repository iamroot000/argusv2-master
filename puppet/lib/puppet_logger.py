import datetime
import os
import time
def nonstandard_puppet_log(hostgroup, user, activity, activity_type=''):

    t= datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S%f")

    dirt = "logs/puppet_logger/{0}/".format(hostgroup)

    if not os.path.exists(dirt):
        os.makedirs(dirt)

    filename = 'logs/puppet_logger/{0}/{1}.{2}-{3}.log'.format(hostgroup,user,t,activity_type)
    f = open(filename,'w')



    if isinstance(activity,list):
        for i in activity:
            f.write(i)
            f.write('\n')
    else:
        f.write(activity)

    f.close()


def standard_puppet_log(hostgroup,user,context,activity_type=''):
    t = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S%f")

    dirt = "logs/puppet_logger/{0}/".format(hostgroup)

    if not os.path.exists(dirt):
        os.makedirs(dirt)

    filename = 'logs/puppet_logger/{0}/{1}.{2}-{3}.log'.format(hostgroup, user, t,activity_type)
    f = open(filename, 'w')

    for path in context['code']:
        f.write('FILENAME: '+path+'\n')
        for rem in context['code'][path]['remove'].split('\n'):
            f.write('-  '+rem+'\n')

        for add in context['code'][path]['add'].split('\n'):
            f.write('+  '+add+'\n')

        for remain in context['code'][path]['remain'].split('\n'):
            f.write(remain+'\n')


    f.close()

def command_logger(hostgroup,user,key,RW,etype="NULL"):
    t = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S%f")

    dirt = "logs/puppet_logger/{0}/".format(hostgroup)

    if not os.path.exists(dirt):
        os.makedirs(dirt)

    filename = 'logs/puppet_logger/{0}/{1}.{2}-{3}.log'.format(hostgroup, user, t, etype)


    context = None
    RETRY = 0

    routine_from = 0
    routine_to = 0

    line = ''
    while line != 'PUPPET_COMMAND_END':
        line = RW.get_routine_line(key, routine_from, routine_to)

        if not line:
            RETRY += 1
            time.sleep(.3)
        else:
            f = open(filename, 'a')
            f.write(line[0]+'\n')
            routine_to +=1
            routine_from +=1

        if RETRY == 500:
            f.write( 'MAX RETRIES EXECUTED, COMMAND NOT RESPONDING')
            break


    f.close()


