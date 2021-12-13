#!/bin/bash
#created by: Yroll Jay-R Macalino
source /home/`whoami`/aom/config
clear
echo -en "${ccyan}Have you added IP? [y/n]? "
read add
echo -en "$cnormal\n\n"
function rterminal() {
for i in `cat ${location}SSR-init-config.list`
do
	xterm -title "$i" -hold -e "sshpass -p VA1913wm ssh root@$i -o StrictHostKeyChecking=no" &
done
}
function rterminal2() {
echo -en "${ccyan}Access the server using port 2556? [y/n]? "
read port
case $port in 
	y|Y|$key)
	for i in `cat ${location}SSR-init-config.list`
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
		mv ${location}SSR-init-config ${location}SSR-init-config.bak 2>/dev/null
		cat /dev/null > ${location}SSR-init-config
		vi ${location}SSR-init-config
		cp ${location}SSR-init-config ${location}SSR-init-config.list
#		rterminal
		sed -i '1i [init-SSR]' ${location}SSR-init-config
		echo -en "\n\n\n[multi:children]\ninit-SSR\n\n\n[init-SSR:vars]\nansible_ssh_user=root\nansible_ssh_port=22\nansible_ssh_pass=VA1913wm\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n\n\n" >> ${location}SSR-init-config
		export ANSIBLE_HOST_KEY_CHECKING=False
		ansible-playbook -i ${location}SSR-init-config ${location}SSR-init.yml --ssh-common-args='-o StrictHostKeyChecking=no'
		rterminal2
		;;
	y|Y)
		mv ${location}SSR-init-config ${location}SSR-init-config.bak 2>/dev/null
#		rterminal
		export ANSIBLE_HOST_KEY_CHECKING=False
		ansible-playbook -i ${location}SSR-init-config.bak ${location}SSR-init.yml --ssh-common-args='-o StrictHostKeyChecking=no'
		rterminal2
		;;
esac

