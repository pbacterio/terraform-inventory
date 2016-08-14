#!/usr/bin/env python

# Terraform dynamic inventory for Ansible
# Copyright (c) 2016, German moya <pbacterio@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

VERSION = '1.0'

import json
from argparse import ArgumentParser
from os import getenv


def parse_args():
    parser = ArgumentParser('Terraform dynamic inventory for Ansible')
    parser.add_argument('--list', action='store_true', default=True, help='List nodes (default: True)')
    parser.add_argument('--host', help='Get all the variables about a specific node')
    parser.add_argument('--tfstate', '-t', help='Terraform state file (terraform.tfstate default)')
    parser.add_argument('--version', '-v', help='Show version')
    args = parser.parse_args()
    if not args.tfstate:
        args.tfstate = getenv('TF_STATE', 'terraform.state')
    return args


def parse_tfstate(filename):
    return json.load(open(filename))


def find_value(dictionary, keys):
    values = [dictionary[k] for k in keys if k in dictionary]  # get values for existing keys
    values = [v for v in values if v]  # filter empty values
    if values:
        return values[0]


class TerraformInventory:
    def __init__(self):
        self.args = parse_args()
        if self.args.version:
            print(VERSION)
        elif self.args.host:
            print(self.get_host(self.args.host))
        elif self.args.list:
            print(self.get_list())

    def get_list(self):
        hosts = []
        hosts_vars = {}
        for address, vars in self.get_instances():
            hosts.append(address)
            hosts_vars[address] = vars
        return json.dumps({'all': {'hosts': hosts}, '_meta': {'hostvars': hosts_vars}}, indent=2)

    def get_host(self, host):
        for address, vars in self.get_instances():
            if address == host:
                return json.dumps(vars, indent=2)

    def get_instances(self):
        tfstate = parse_tfstate(self.args.tfstate)
        for module in tfstate['modules']:
            for resource in module['resources'].values():
                if resource['type'] not in ('aws_instance', 'openstack_compute_instance_v2'):
                    continue
                if resource['type'] == 'aws_instance':
                    provider = 'aws'
                    address = find_value(resource['primary']['attributes'],
                                         ('public_dns', 'public_ip', 'private_dns', 'private_ip'))
                elif resource['type'] == 'openstack_compute_instance_v2':
                    provider = 'openstack'
                    address = find_value(resource['primary']['attributes'],
                                         ('floating_ip', 'access_ip_v4', 'access_ip_v6'))
                else:
                    continue
                vars = resource['primary']['attributes']
                vars['provider'] = provider
                yield address, vars


if __name__ == '__main__':
    TerraformInventory()
