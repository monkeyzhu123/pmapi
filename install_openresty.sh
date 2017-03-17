#!/bin/bash

cat  <<EOF >/etc/yum.repos.d/OpenResty.repo 
[openresty]
name=Official OpenResty Repository
baseurl=https://openresty.org/yum/openresty/openresty/epel-$releasever-$basearch/
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/openresty/openresty/pubkey.gpg
enabled=1
enabled_metadata=1
EOF
yum --disablerepo="*" --enablerepo="openresty" list available
yum -y install openresty
