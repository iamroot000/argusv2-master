#!/bin/bash
#created by: Yroll Jay-R Macalino
source /home/`whoami`/aom/config
clear
echo -en "${ccyan}Have you added IP? [y/n]? "
read add
echo -en "$cnormal\n\n"
function rterminal() {
for i in `cat ${location}initialization-centOS7-forwarding-2018-config.list`
do
	xterm -title "$i" -hold -e "sshpass -p S24e@310 ssh root@$i -o StrictHostKeyChecking=no" &
done
}
function rterminal2() {
echo -en "${ccyan}Access the server using port 2556? [y/n]? "
read port
case $port in 
	y|Y|$key)
	for i in `cat ${location}initialization-centOS7-forwarding-2018-config.list`
	do
		xterm -title "$i Accessing" -hold -e "ssh -vp2556 ommgr@$i -o StrictHostKeyChecking=no" &
	done
	echo -en "$cnormal\n\n"
	;;
esac
echo -en "$cnormal\n\n"
}
case $add in
	n|N|$key)
		mv ${location}initialization-centOS7-forwarding-2018-config ${location}initialization-centOS7-forwarding-2018-config.bak 2>/dev/null
		cat /dev/null > ${location}initialization-centOS7-forwarding-2018-config
		vi ${location}initialization-centOS7-forwarding-2018-config
		cp ${location}initialization-centOS7-forwarding-2018-config ${location}initialization-centOS7-forwarding-2018-config.list
#		rterminal
		sed -i '1i [init-centOS7-forwarding-2018]' ${location}initialization-centOS7-forwarding-2018-config
		echo -en "\n\n\n[multi:children]\ninit-centOS7-forwarding-2018\n\n\n[init-centOS7-forwarding-2018:vars]\nansible_ssh_user=root\nansible_ssh_port=22\nansible_ssh_pass=S24e@310\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n\n\n" >> ${location}initialization-centOS7-forwarding-2018-config
		export ANSIBLE_HOST_KEY_CHECKING=False
		ansible-playbook -i ${location}initialization-centOS7-forwarding-2018-config ${location}initialization-centOS7-forwarding-2018.yml --ssh-common-args='-o StrictHostKeyChecking=no'
		rterminal2
		;;
	y|Y)
		mv ${location}initialization-centOS7-forwarding-2018-config ${location}initialization-centOS7-forwarding-2018-config.bak 2>/dev/null
#		rterminal
		export ANSIBLE_HOST_KEY_CHECKING=False
		ansible-playbook -i ${location}initialization-centOS7-forwarding-2018-config.bak ${location}initialization-centOS7-forwarding-2018.yml --ssh-common-args='-o StrictHostKeyChecking=no'
		rterminal2
		;;
esac

