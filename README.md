# spotinst-ansible-module
An Ansible Module for creating or deleting Spotinst Elastigroups

## Table of contents
<!--ts-->
   * [Requirements](#requirements)
   * [Installation](#installation)
   * [Configuring Credentials](#configuring-credentials)
   * [Usage](#usage)
      * [Elastigroup](#elastigroup)
        * [Getting Started With Elastigroup](#getting-started-with-elastigroup)
        * [Elastigroup Advanced](#elastigroup-advanced)
        * [Elastigroup Additional Configurations](#elastigroup-additional-configurations)
          * [Scaling](#scaling-policies)
          * [Stateful](#stateful)
          * [Scheduling](#scheduling)
          * [Load Balancing](#load-balancing)
        * [Third Party Integrations](#third-party-integrations)
          * [ECS](#[ecs](examples/elastigroup-ecs.yml))
          * [Kubernetes](#[kubernetes](examples/elastigroup-kubernetes.yml))
          * [Nomad](#[nomad](examples/elastigroup-nomad.yml))
          * [Docker Swarm](#[docker-swarm](examples/elastigroup-docker-swarm.yml))
          * [CodeDeploy](#[code-deploy](examples/elastigroup-code-deploy.yml))
          * [Route53](#[route53](examples/elastigroup-route53.yml))
          * [ElasticBeanstalk](#[elastic-beanstalk](examples/elastigroup-elastic-beanstalk.yml))
<!--te-->

## Requirements
- [spotinst-sdk-python](https://github.com/spotinst/spotinst-sdk-python) >= `v1.0.29`

## Installation
If you'd like to work with this version of the module and not the supplied version that is packaged with Ansible,
you can copy the module into your Ansible module directory. 
```bash
git clone https://github.com/spotinst/spotinst-ansible-module
cp spotinst-ansible-module/spotinst_aws_elastigroup.py /lib/ansible/modules/cloud/spotinst/spotinst_aws_elastigroup.py
```
Otherwise the module comes pre-installed with the latest [Ansible](https://github.com/ansible/ansible) release.

## Configuring Credentials
The mechanism in which the module looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials. The order in which the module searches for credentials is:
  - The keys; `credentials_path` and `profile` inside the playbook itself  
  - Environment variables in `SPOTINST_ACCOUNT` & `SPOTINST_TOKEN`
  - Environment variables in `SPOTINST_PROFILE` & `SPOTINST_SHARED_CREDENTIALS_FILE`
  - Shared credential file `~/.spotinst/credentials`
  
>- example credentials file
 ```yaml
 default:
   token: token
   account: account
 ```

## Usage
```bash
ansible-playbook elastigroup-basic.yml
```

### Argument Reference
- [spotinst_aws_elastigroup](docs/argument_reference.yml)  

More information can be found in the official Ansible [documentation](https://docs.ansible.com/ansible/latest/modules/spotinst_aws_elastigroup_module.html#spotinst-aws-elastigroup-module) 
page as well as in the spotinst [documentation](https://help.spotinst.com/hc/en-us/articles/115003530285-Ansible-).

## Elastigroup

### Getting Started With Elastigroup
In this basic example, we create a simple elastigroup
```yaml
- hosts: localhost
  tasks:
    - name: create elastigroup
      spotinst_aws_elastigroup:
          name: ansible_test_group
          state: present
          risk: 100
          availability_vs_cost: balanced
          availability_zones:
            - name: us-east-2c
              subnet_id: subnet-123c
          image_id: test-ami
          key_pair: test-key-pair
          max_size: 2
          min_size: 0
          target: 0
          unit: instance
          monitoring: False
          on_demand_instance_type: m4.large
          product: Linux/UNIX
          tags:
            - Name: ansible_test_group
          security_group_ids:
            - sg-default
          spot_instance_types:
            - m4.xlarge
            - m5.xlarge
          do_not_update:
            - image_id
            - target
            - user_data
      register: result
    - debug: var=result

```

### Elastigroup Advanced
In this advanced example, we create an elastigroup with
- user data and shutdown script 
- multiple EBS device mappings for the instances in this group 
- network interfaces configuration for the instances in this group
- revert to spot configuration, which is the time frame at which Spotinst tries to spin spots instead of on-demands
- preferred availability zones in which to spin instances
- preferred spot instance types to launch

```yaml
- hosts: localhost
  tasks:
    - name: create elastigroup
      spotinst_aws_elastigroup:
          name: ansible_test_group
          state: present
          risk: 100
          availability_vs_cost: balanced
          revert_to_spot:
            perform_at: timeWindow
            time_windows:
              - "Sun:11:00-Mon:12:00"
              - "Mon:03:00-Wed:02:30"
          availability_zones:
            - name: us-east-2c
              subnet_id: subnet-123c
            - name: us-east-2b
              subnet_id: subnet-123b
            - name: us-east-2a
              subnet_id: subnet-123a
          image_id: test-ami
          key_pair: test-key-pair
          max_size: 2
          min_size: 0
          target: 0
          unit: instance
          monitoring: False
          on_demand_instance_type: m4.large
          product: Linux/UNIX
          user_data: IyEvdXNyL2Jpbi9lbnYgYmFzaA==
          shutdown_script: IyEvdXNyL2Jpbi9lbnYgYmFzaA==
          preferred_availability_zones:
            - us-east-2c
          block_device_mappings:
            - device_name: '/dev/xvda'
              ebs:
                volume_size: 60
                volume_type: gp2
            - device_name: '/dev/xvdb'
              ebs:
                volume_size: 120
                volume_type: gp2
            - device_name: '/dev/xvdc'
              virtual_name: ephemeral0
          network_interfaces:
            - description: test-eni
              device_index: 0
              associate_public_ip_address: true
              delete_on_termination: true
              associate_ipv6_address: false
            - description: test-eni
              device_index: 1
              associate_public_ip_address: false
              delete_on_termination: true
              associate_ipv6_address: false
          tags:
            - Name: ansible_test_group
            - Environment: dev
          security_group_ids:
            - sg-default
          spot_instance_types:
            - m4.xlarge
            - m5.xlarge
          preferred_spot_instance_types:
            - m4.xlarge
          do_not_update:
            - image_id
            - target
            - user_data
      register: result
    - debug: var=result
```

### Elastigroup Additional Configurations
#### Scaling Policies
- Scale your elastigroup using up/down and target tracking scaling policies with a variety of adjustment operations 
>- example: [elastigroup-scaling-policies.yml](examples/elastigroup-scaling-policies.yml)
#### Stateful
- Persist your mounted root & data volumes along with connected ip addresses
>- example: [elastigroup-stateful.yml](examples/elastigroup-stateful.yml)
#### Scheduling
- Perform scheduled actions on your elastigroup such as scale, instance count adjustments etc.
>- example: [elastigroup-scheduling.yml](examples/elastigroup-scheduling.yml)
#### Load Balancing
- Integrate and connect your instances AWS's ELB and ALB along with Spotinst's MLB
>- example: [elastigroup-load-balancers.yml](examples/elastigroup-load-balancers.yml)
#### Variable usage & output
- In this example, we create an elastigroup and wait 600 seconds to retrieve the instances, and use their instance ids
>- example: [elastigroup-variable-retrieval](examples/elastigroup-variable-retrieval.yml)

### Third Party Integrations
- ##### [ecs](examples/elastigroup-ecs.yml)
- ##### [kubernetes](examples/elastigroup-kubernetes.yml)
- ##### [nomad](examples/elastigroup-nomad.yml)
- ##### [docker swarm](examples/elastigroup-docker-swarm.yml)
- ##### [code-deploy](examples/elastigroup-code-deploy.yml)
- ##### [route53](examples/elastigroup-route53.yml)
- ##### [elastic-beanstalk](examples/elastigroup-elastic-beanstalk.yml)
