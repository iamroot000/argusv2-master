#!/bin/bash
#created by: Yroll Jay-R Macalino
source /home/`whoami`/aom/config
clear
echo -en "${ccyan}Have you added IP? [y/n]? "
read add
echo -en "$cnormal\n\n"
case $add in
	n|N|$key)
		mv ${location}ssrhost ${location}ssrhost.bak 2>/dev/null
		cat /dev/null > ${location}ssrhost
		vi ${location}ssrhost
		sed -i '1i [ssr2556]' ${location}ssrhost
	        echo -en "\n[ssr22]\n\n\n[multi:children]\nssr2556\nssr22\n\n\n[ssr2556:vars]\nansible_ssh_user=ommgr\nansible_ssh_port=2556\nAUTH_BASIC_ENABLED=False\nhost_key_checking=False\n\n\n[ssr22:vars]\nansible_ssh_user=root\nhost_key_checking=False\nANSIBLE_HOST_KEY_CHECKING=False\nansible_ssh_port=22\n" >> ${location}ssrhost
		export ANSIBLE_HOST_KEY_CHECKING=False
		ansible-playbook -i ${location}ssrhost ${location}sshpubkey.yml --ssh-common-args='-o StrictHostKeyChecking=no'
		;;
	y|Y)
		mv ${location}ssrhost ${location}ssrhost.bak 2>/dev/null
		ansible-playbook -i ${location}ssrhost.bak ${location}sshpubkey.yml
		;;
esac
