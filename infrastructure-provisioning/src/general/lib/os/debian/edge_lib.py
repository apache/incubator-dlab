#!/usr/bin/python

# *****************************************************************************
#
# Copyright (c) 2016, EPAM SYSTEMS INC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ******************************************************************************

import os
import sys
from fabric.api import *
from fabric.contrib.files import exists
import ipaddress


def validate_ip_address(ip_address):
    try:
        ipaddress.ip_address(u'{}'.format(ip_address))
        return True
    except ValueError:
        return False


def validate_ip_network(ip_network):
    try:
        ipaddress.ip_network(u'{}'.format(ip_network))
        return True
    except ValueError:
        return False


def configure_http_proxy_server(config):
    try:
        if not exists('/tmp/http_proxy_ensured'):
            sudo('apt-get -y install squid')
            template_file = config['template_file']
            proxy_subnet = config['exploratory_subnet']
            put(template_file, '/tmp/squid.conf')
            sudo('\cp /tmp/squid.conf /etc/squid/squid.conf')
            sudo('sed -i "s|PROXY_SUBNET|{}|g" /etc/squid/squid.conf'.format(proxy_subnet))
            sudo('sed -i "s|EDGE_USER_NAME|{}|g" /etc/squid/squid.conf'.format(config['edge_user_name']))
            sudo('sed -i "s|LDAP_HOST|{}|g" /etc/squid/squid.conf'.format(config['ldap_host']))
            sudo('sed -i "s|LDAP_DN|{}|g" /etc/squid/squid.conf'.format(config['ldap_dn']))
            sudo('sed -i "s|LDAP_SERVICE_USERNAME|{}|g" /etc/squid/squid.conf'.format(config['ldap_user']))
            sudo('sed -i "s|LDAP_SERVICE_PASSWORD|{}|g" /etc/squid/squid.conf'.format(config['ldap_password']))
            sudo('sed -i "s|LDAP_AUTH_PATH|{}|g" /etc/squid/squid.conf'.format('/usr/lib/squid/basic_ldap_auth'))
            replace_string = ''
            if os.environ['local_repository_enabled'] == 'True':
                if validate_ip_address(os.environ['local_repository_host']):
                    config['vpc_cidrs'].append('{}/32'.format(os.environ['local_repository_host']))
                else:
                    config['vpc_cidrs'].append(os.environ['local_repository_host'])
                if validate_ip_address(os.environ['local_repository_parent_proxy_host']):
                    config['vpc_cidrs'].append('{}/32'.format(os.environ['local_repository_parent_proxy_host']))
                else:
                    config['vpc_cidrs'].append(os.environ['local_repository_parent_proxy_host'])
                if validate_ip_address(os.environ['local_repository_nginx_proxy_host']):
                    config['vpc_cidrs'].append('{}/32'.format(os.environ['local_repository_nginx_proxy_host']))
                else:
                    config['vpc_cidrs'].append(os.environ['local_repository_nginx_proxy_host'])
            config['vpc_cidrs'] = set(config['vpc_cidrs'])
            for cidr in config['vpc_cidrs']:
                if validate_ip_network(cidr):
                    replace_string += 'acl AWS_VPC_CIDR dst {}\\n'.format(cidr)
                else:
                    replace_string += 'acl AllowedDomains dstdomain {}\\n'.format(cidr)
            sudo('sed -i "s|VPC_CIDRS|{}|g" /etc/squid/squid.conf'.format(replace_string))
            replace_string = ''
            for cidr in config['allowed_ip_cidr']:
                replace_string += 'acl AllowedCIDRS src {}\\n'.format(cidr)
            sudo('sed -i "s|ALLOWED_CIDRS|{}|g" /etc/squid/squid.conf'.format(replace_string))
            if 'local_repository_parent_proxy_host' in os.environ:
                replace_string = 'acl META dst 169.254.169.254/32\\nalways_direct allow META\\ncache_peer {0} ' \
                                 'parent {1} 0 no-query default\\nnever_direct allow all'.format(
                                  os.environ['local_repository_parent_proxy_host'],
                                  os.environ['local_repository_parent_proxy_port'])
            else:
                replace_string = ''
            sudo('sed -i "s|CHILD_PROXY|{}|g" /etc/squid/squid.conf'.format(replace_string))
            sudo('service squid reload')
            sudo('sysv-rc-conf squid on')
            sudo('touch /tmp/http_proxy_ensured')
    except Exception as err:
        print("Failed to install and configure squid: " + str(err))
        sys.exit(1)


def install_nginx_ldap(edge_ip, nginx_version, ldap_ip, ldap_dn, ldap_ou, ldap_service_pass, ldap_service_username,
                       ldap_user):
    try:
        if not os.path.exists('/tmp/nginx_installed'):
            sudo('apt-get install -y wget')
            sudo('apt-get -y install gcc build-essential make zlib1g-dev libpcre++-dev libssl-dev git libldap2-dev')
            sudo('mkdir -p /tmp/nginx_auth_ldap')
            if 'local_repository_parent_proxy_host' in os.environ:
                sudo('git config --global http.proxy http://{0}:{1}'.format(
                    os.environ['local_repository_parent_proxy_host'], os.environ['local_repository_parent_proxy_port']))
                sudo('git config --global https.proxy http://{0}:{1}'.format(
                    os.environ['local_repository_parent_proxy_host'], os.environ['local_repository_parent_proxy_port']))
            with cd('/tmp/nginx_auth_ldap'):
                sudo('git clone https://github.com/kvspb/nginx-auth-ldap.git')
            sudo('mkdir -p /tmp/src')
            with cd('/tmp/src/'):
                if os.environ['local_repository_enabled'] == 'True':
                    sudo('wget {0}/nginx-{1}.tar.gz'.format(
                        os.environ['local_repository_packages_repo'], nginx_version))
                else:
                    sudo('wget http://nginx.org/download/nginx-{}.tar.gz'.format(nginx_version))
                sudo('tar -xzf nginx-{}.tar.gz'.format(nginx_version))
                sudo('ln -sf nginx-{} nginx'.format(nginx_version))
            with cd('/tmp/src/nginx/'):
                sudo('./configure --user=nginx --group=nginx --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx \
                              --conf-path=/etc/nginx/nginx.conf --pid-path=/run/nginx.pid --lock-path=/run/lock/subsys/nginx \
                              --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log \
                              --with-http_gzip_static_module --with-http_stub_status_module --with-http_ssl_module --with-pcre \
                              --with-http_realip_module --with-file-aio --with-ipv6 --with-http_v2_module --with-debug \
                              --without-http_scgi_module --without-http_uwsgi_module --without-http_fastcgi_module --with-http_sub_module \
                              --add-module=/tmp/nginx_auth_ldap/nginx-auth-ldap/')
                sudo('make')
                sudo('make install')
            sudo('useradd -r nginx')
            sudo('rm -f /etc/nginx/nginx.conf')
            sudo('mkdir -p /opt/dlab/templates')
            put('/root/templates', '/opt/dlab', use_sudo=True)
            sudo('sed -i \'s/LDAP_IP/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_ip))
            sudo('sed -i \'s/LDAP_DN/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_dn))
            sudo('sed -i \'s/LDAP_OU/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_ou))
            sudo('sed -i \'s/LDAP_SERVICE_PASSWORD/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_service_pass))
            sudo('sed -i \'s/LDAP_SERVICE_USERNAME/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_service_username))
            sudo('sed -i \'s/LDAP_USERNAME/{}/g\' /opt/dlab/templates/nginx.conf'.format(ldap_user))
            sudo('sed -i \'s/EDGE_IP/{}/g\' /opt/dlab/templates/conf.d/proxy.conf'.format(edge_ip))
            sudo('cp /opt/dlab/templates/nginx.conf /etc/nginx/')
            sudo('mkdir /etc/nginx/conf.d')
            sudo('cp /opt/dlab/templates/conf.d/proxy.conf /etc/nginx/conf.d/')
            sudo('mkdir /etc/nginx/locations')
            sudo('cp /opt/dlab/templates/nginx_debian /etc/init.d/nginx')
            sudo('chmod +x /etc/init.d/nginx')
            sudo('systemctl daemon-reload')
            sudo('systemctl enable nginx')
            sudo('/etc/init.d/nginx start')
            sudo('touch /tmp/nginx_installed')
    except Exception as err:
        print("Failed install nginx with ldap: " + str(err))
        sys.exit(1)
