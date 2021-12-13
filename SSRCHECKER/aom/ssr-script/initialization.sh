#!/bin/bash
#Linux Initialization Automation
#v1.5


if [[ `egrep -o 'CentOS release 5' /etc/redhat-release` ]]; then
	if [[ `uname -p|grep x86_64` ]]; then
	        rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
	else
        	rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm
	fi	
else
	if [[ `uname -p|grep x86_64` ]]; then
		rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
	else
		rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
	fi
fi

sed -i "s/mirrorlist=https/mirrorlist=http/" /etc/yum.repos.d/epel.repo
yum clean all


IP_ALIAS=/etc/sysconfig/network-scripts
###test if machine is a real server or a virtual machine
yum install pciutils which -y
if [[ -z `lspci` ]]
then
echo "This is a Xen Virtual Machine"
elif [[ -n `lspci |grep -i VMware` ]]
then
echo "this is a VMware machine"
else
echo "this is a real server"
fi


#step 1: Change the default hostname.
echo "Please enter hostname for this server:"
read HNAME
echo -e "changing default hostname \n"
hostname $HNAME
sed -i s/localhost.localdomain/$HNAME'    localhost.localdomain'/ /etc/hosts
sed -i s/HOSTNAME=.*/HOSTNAME=$HNAME/ /etc/sysconfig/network


yum install -y iptables openssl-devel openssl gcc net-snmp net-snmp-utils net-snmp-devel pcre-devel zlib-devel apr apr-devel openssl-devel gd-devel gd vim-enhanced ntp xinetd make iptables sudo cronie vixie-cron wget elinks perl perl-CPAN perl-YAML zip unzip cmake libaio* nc openssl-devel


#step 2: Add generic usernames.
useradd ommgr
COMMON='ommgr'
#step 3: Create .ssh directory for common user
        mkdir /home/$COMMON/.ssh 
        chown $COMMON.$COMMON -R /home/$COMMON/.ssh
        chmod 700 /home/$COMMON/.ssh 
        echo -e "finished creating .ssh directory. \n "

#        echo -e "adding ebo user \n"
#        useradd ebo -u498 -g500 -M -s /sbin/nologin


#step 5: Change default ssh port
SSHPORT='2556'
echo "Changing default ssh configuration"
sed -i s/'#Port 22'/"Port $SSHPORT"/ /etc/ssh/sshd_config
sed -i s/'#PermitRootLogin yes'/'PermitRootLogin no'/ /etc/ssh/sshd_config
sed -i s/'#PermitUserEnvironment no'/'PermitUserEnvironment yes'/ /etc/ssh/sshd_config
sed -i s/'#PermitEmptyPasswords no'/'PermitEmptyPasswords no'/ /etc/ssh/sshd_config
sed -i s/'PasswordAuthentication yes'/'PasswordAuthentication no'/ /etc/ssh/sshd_config
sed -i s/'GSSAPIAuthentication yes'/'GSSAPIAuthentication no'/ /etc/ssh/sshd_config
sed -i s/'#LoginGraceTime 2m'/'LoginGraceTime 1m'/ /etc/ssh/sshd_config
echo 'AllowUsers ommgr' >> /etc/ssh/sshd_config

#step 6: Check if script for DDOS attack exist    
if [ -f netstat-statistics.sh ]
    then   
        cp netstat-statistics.sh /home/$COMMON/
        chown $COMMON.$COMMON -R /home/$COMMON/
        echo "netstat-statistics copied to /home/$COMMON"
    else
        echo "file does not exist"
fi

#step 7: Check/Install/Configure vim-enhanced
rpm -qa |grep vim-enhanced
if [ $? != 0 ]
       then
    echo -e "installing vim-enhanced"
       yum -y install vim-enhanced
       else
       echo "vim-enhanced already installed"
fi
cat .bashrc |grep -e "alias vi=vim"
if [ $? != 0 ]
       then
       echo "alias vi=vim" >> .bashrc
       else
       echo "vim already configured"
fi
source /root/.bashrc
echo
#step 8: Check run level
runlevel | cut -d" " -f2 |grep 3 >/dev/null
if [ $? != 0 ]
       then
       echo "Change runlevel to runlevel 3"
    sed -i s/id:./id:3/ /etc/inittab   
       else
       echo "running on runlevel 3"
fi
echo
#step 9: Disable unwanted services
for svc in `chkconfig --list |awk '{print $1}'`
do
case $svc in

    cpuspeed )
               chkconfig --level 345 $svc on ;;
       crond )
               chkconfig --level 345 $svc on ;;
       iptables )
               chkconfig --level 345 $svc on ;;
       irqbalance )
               chkconfig --level 345 $svc on ;;
       kudzu )
               chkconfig --level 345 $svc on ;;
       messagebus )
               chkconfig --level 345 $svc on ;;
       network )
               chkconfig --level 345 $svc on ;;
       readahead_early )
               chkconfig --level 345 $svc on ;;
       smartd )
               chkconfig --level 345 $svc on ;;
       sshd )
               chkconfig --level 345 $svc on ;;
       syslog )
               chkconfig --level 345 $svc on ;;
       * )
               chkconfig --level 345 $svc off ;;
esac

done

#step 10: Disable selinux
sed -i s/=enforcing/=disabled/ /etc/selinux/config
sed -i s/=enforcing/=disabled/ /etc/sysconfig/selinux
setenforce 0

#step 11: Change default limits

echo "*          soft          nofile          51200" >> /etc/security/limits.conf
echo "*          hard          nofile          65536" >> /etc/security/limits.conf

bit=`uname -a | grep -oE x86_64 | head -1`
if [[ -z $bit ]]; then
	echo "Server is 32bit"
	echo "session   required    /lib/security/pam_limits.so" >> /etc/pam.d/login
else
	echo "Server is 64bit"
	echo "session   required    /lib64/security/pam_limits.so" >> /etc/pam.d/login
fi



wget -O /home/ommgr/.ssh/authorized_keys http://omadmin:S18B300@office.pc-setting.info/cyrus/authorized_keys
if [[ $? -eq 0 ]]; then
chown -R ommgr. /home/ommgr/.ssh
chmod 600 /home/ommgr/.ssh/authorized_keys
/etc/init.d/sshd reload
fi

echo -e "Linux initilization done \n"
echo -e "IMPORTANT: \n"
echo -e "          Check sshd config and iptables before restarting this server! \n" 

