[defaults]
inventory = ./ansible/inventory
remote_user = ${username}
private_key_file = ~/.ssh/id_rsa.pub
host_key_checking = False
nocows = 1

[privilege_escalation]
become=True
become_method=sudo
become_user=root
become_ask_pass=False