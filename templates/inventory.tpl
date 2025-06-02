# inventory.tpl

[main]
${instances.tags.Name} ansible_host=${instances.public_dns}
