ansible-playbook -i hosts_v2ray main.yml --extra-vars ansible_become_pass="Aom@9876Wm" --become-method=su --limit v2ray_init --tags initialization_v2ray
