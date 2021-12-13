#!/bin/bash
#created by: Yroll Jay-R Macalino
source /home/`whoami`/aom/config
clear
echo -en "${ccyan}Have you added Domain? [y/n]? "
read add
echo -en "$cnormal\n\n"
case $add in
        n|N|$key)
                mv ${location}domainchecking.yml ${location}domainchecking.bak.yml 2>/dev/null
                cat /dev/null > ${location}domainchecking.yml
                cat /dev/null > ${location}domainchecking.list
                vi ${location}domainchecking.list
                sed -i 's/^/      - /gi' ${location}domainchecking.list
                echo -en "---\n- hosts: 127.0.0.1\n  gather_facts: no\n\n  tasks:\n  - name: Check that you can connect (GET) to a page and it returns a status 200\n    uri:\n     url: http://{{ item }}\n    with_items:\n" >> ${location}domainchecking.yml
		cat ${location}domainchecking.list >> ${location}domainchecking.yml
		echo -en "    ignore_errors: yes\n" >> ${location}domainchecking.yml
        
	        echo -en "\n  - name: A record (IPV4 address) lookup\n    debug: msg='{{ lookup('dig', '{{ item }}')}}'\n    with_items:\n" >> ${location}domainchecking.yml
		cat ${location}domainchecking.list >> ${location}domainchecking.yml
		echo -en "    ignore_errors: yes\n" >> ${location}domainchecking.yml



                ansible-playbook ${location}domainchecking.yml
                ;;
        y|Y)
                mv ${location}domainchecking.yml ${location}domainchecking.bak.yml 2>/dev/null
                ansible-playbook ${location}domainchecking.bak.yml
                ;;
esac

