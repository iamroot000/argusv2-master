#!/bin/bash
#created by: Yroll Jay-R Macalino
source /home/`whoami`/aom/config
function banner(){
	clear
	echo -en $cred
	figlet -c AOM Tools
	echo -en "\n\n"
	echo -en "${cred}1.) ${cnormal}CentOS7 Forwarding Intialization\n\n"
	echo -en "${cred}2.) ${cnormal}CentOS7 Forwarding Intialization with puppet\n\n"
	echo -en "${cred}3.) ${cnormal}SSR Initialization and Configuration\n\n"
	echo -en "${cred}4.) ${cnormal}Adding SSH Pubkey on VPN\n\n"
	echo -en "${cred}5.) ${cnormal}Domain Checking\n\n"
	echo -en "\n\n"
	echo -en "${cwhite}Num]$cred "
	read number
	echo -en $cnormal
	
	case $number in
		1)
		bash ${location}initialization-centOS7-forwarding-2018-aom.sh
		;;
		2)
		bash ${location}initialization-centOS7-forwarding-with-puppet-2018-aom.sh
#		echo -en "\n\n$cred This script is not yet finished\n\n"
#		echo -en $cnormal
		;;
                3)
		echo -en "\n\n$cred This script is not yet finished\n\n"
		echo -en $cnormal
                ;;
		4)
		bash ${location}sshpubkey.sh
		;;
                5)
                bash ${location}domainchecking.sh
		;;
	esac
		
	
}
clear
for intl in xterm sshpass
do
apt list --installed | grep -qi $intl
if [[ `echo $?` != 0  ]]
then
        clear
        sudo apt-get install $intl -y
fi
done
#apt list --installed | grep -qi sshpass
#if [[ `echo $?` != 0  ]]
#then
#        clear
#	sudo apt-get install sshpass -y
#fi
#clear
apt list --installed | grep -qi figlet
if [[ `echo $?` != 0  ]]
then
        clear
	sudo apt-get install figlet 
	sudo apt-get install sshpass -y
elif [[ `apt list --installed | grep -qi ansible && echo $?` != 0 ]]
then
       	sudo apt-get update
    	sudo apt install software-properties-common
        sudo apt-add-repository ppa:ansible/ansible
        sudo apt update
	sudo apt-get install ansible -y && sudo apt-get install sshpass -y
        banner
	
else
        banner
fi

