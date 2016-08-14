Terraform dynamic inventory for Ansible
=======================================

This is a little script wich generates a dynamic Ansible inventory from a Terraform state file.
Actually supported: AWS and Openstack instances.

All the attributes of Terraform instances, are passed to Ansible as host vars.


Installation
------------

Just download the file script `terraform.py` from https://raw.githubusercontent.com/pbacterio/terraform-inventory/master/terraform.py
and ensure that has executable permissions.

    wget https://raw.githubusercontent.com/pbacterio/terraform-inventory/master/terraform.py
    chmod +x terraform.my


Usage
-----

Use `terraform.py` as the inventory file in your invocation of ansible

    ansible -i terraform.py -m ping all
    
By default, the `terraform.py` script read the terraform state from the file `terraform.tfstate` in the current directory.

You can use the`TF_STATE` environment var to specify another terraform state file.

    TF_STATE="../provision/dev.tfstate" ansible -i terraform.py -m ping all
    
