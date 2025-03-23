# inventory.tpl

[main]
main ansible_host=${main_ip} ansible_user=ubuntu

[storage]
%{ for index, ip in storage_ips ~}
storage${index} ansible_host=${ip} ansible_user=ubuntu
%{ endfor ~}


[all:vars]
ansible_ssh_private_key_file=~/.ssh/id_rsa
ansible_ssh_common_args='-o StrictHostKeyChecking=no'