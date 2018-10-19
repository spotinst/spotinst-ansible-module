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
          * [Rancher](#[rancher](examples/elastigroup-rancher.yml))
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
The mechanism in which the module looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials. 
The order in which the sdk searches for credentials is:
  1. Fetching the account and token from environment variables under `SPOTINST_ACCOUNT` & `SPOTINST_TOKEN`

If you choose to not pass your credentials directly you configure a credentials file, this file should be a valid `.yml` file.
The default shared credential file location is `~/.spotinst/credentials` and the default profile is `default`
- example

```yaml
default: #profile
  token: $defaul_spotinst_token
  account: $default_spotinst-account-id
my_profle:
  token: $my_spotinst_token
  account: $my_spotinst-account-id
```
  
  2. You can overwrite the credentials file location and the profile used as parameters `credentials_path` and/or `profile` inside the playbook
- example
  
```yaml
- hosts: localhost
  tasks:
    - name: example elastigroup
      spotinst_aws_elastigroup:
          name: ansible_test_group
          state: present
          credentials_path: /path/to/file
          profile: my_profile
...
```

  3. You can overwrite the credentials file location and the profile used as environment variables `SPOTINST_PROFILE` and/or `SPOTINST_SHARED_CREDENTIALS_FILE`
  4. Fetching from the default location with the default profile

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
          target_tracking_policies:
            - policy_name: test-target-tracking-1
              namespace: AWS/EC2
              metric_name: CPUUtilization
              statistic: average
              unit: percent
              target: 50
              cooldown: 120
              source: cloudWatch
          up_scaling_policies:
            - policy_name: test-scaling-policies-1
              namespace: AWS/EC2
              metric_name: CPUUtilization
              statistic: average
              unit: percent
              cooldown: 120
              threshold: 50
              source: cloudWatch
              dimensions:
                - name: InstanceId
              evaluation_periods: 5
              period: 300
              action_type: adjustment
              adjustment: 1
            - policy_name: test-scaling-policies-2
              namespace: AWS/EC2
              metric_name: CPUUtilization
              statistic: average
              unit: percent
              cooldown: 120
              threshold: 50
              source: cloudWatch
              dimensions:
                - name: InstanceType
              evaluation_periods: 5
              period: 300
              action_type: updateCapacity
              target: 10
              maximum: 15
              minimum: 5
          down_scaling_policies:
            - policy_name: test-scaling-policies-1
              namespace: AWS/EC2
              metric_name: CPUUtilization
              statistic: average
              unit: percent
              cooldown: 120
              threshold: 50
              source: cloudWatch
              dimensions:
                - name: InstanceId
              evaluation_periods: 5
              period: 300
              action_type: percentageAdjustment
              adjustment: 20
          tags:
            - Name: ansible_test_group
            - Environment: dev
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
#### Stateful
- Persist your mounted root & data volumes along with connected ip addresses
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
          persistence:
            should_persist_root_device: false
            should_persist_block_devices: true
            should_persist_private_ip: false
            block_devices_mode: reattach
          private_ips:
            - 1.2.3.4
            - 2.3.4.5
          tags:
            - Name: ansible_test_group
            - Environment: dev
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
#### Scheduling
- Perform scheduled actions on your elastigroup such as scale, instance count adjustments etc.
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
          scheduled_tasks:
            - task_type: scale
              start_time: "2019-05-25T10:55:09Z"
              scale_target_capacity: 3
              scale_min_capacity: 3
              scale_max_capacity: 3
            - task_type: backup_ami
              frequency: hourly
            - task_type: roll
              cron_expression: "00 17 * * 3"
              batch_size_percentage: 30
            - task_type: scaleDown
              cron_expression: "00 22 * * 3"
              adjustment: 1
          tags:
            - Name: ansible_test_group
            - Environment: dev
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
#### Load Balancing
- Integrate and connect your instances AWS's ELB and ALB along with Spotinst's MLB
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
          load_balancers:
            - test_classic_elb
          target_group_arns:
            - "arn:aws:elasticloadbalancing:us-west-2:922761411234:targetgroup/TestTargetGroup/123abc"
          mlb_load_balancers:
            - target_set_id: "ts-123456789"
              balancer_id: "lb-123456789"
              auto_weight: true
              az_awareness: false
          tags:
            - Name: ansible_test_group
            - Environment: dev
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
#### Variable usage & output
- In this example, we create an elastigroup and wait 600 seconds to retrieve the instances, and use their instance ids
```yaml
- hosts: localhost
  tasks:
    - name: create elastigroup
      spotinst_aws_elastigroup:
          profile: ci
          name: ansible_test_group
          state: present
          risk: 100
          availability_vs_cost: balanced
          availability_zones:
            - name: us-east-2c
              subnet_id: subnet-39e2d574 #stg-subnet1  (az1)
            - name: us-east-2b
              subnet_id: subnet-a9f008d3 #stg-subnet2 (az2)
            - name: us-east-2a
              subnet_id: subnet-50c24238 #stg-subnet3 (az3)
          image_id: test-ami
          key_pair: spotinst_ci
          max_size: 2
          min_size: 0
          target: 2
          unit: instance
          monitoring: False
          on_demand_instance_type: m4.large
          product: Linux/UNIX
          tags:
            - Name: ansible_test_group
          security_group_ids:
            - sg-8ad2bbe1
          spot_instance_types:
            - m4.xlarge
            - m5.xlarge
          do_not_update:
            - image_id
            - target
            - user_data
          wait_for_instances: True
          wait_timeout: 600
      register: result

    - name: Store instance ids to file
      shell: echo {{ item.instance_id }}\\n >> list_of_instance_ids
      with_items: "{{ result.instances }}"
    - debug: var=result
```

### Third Party Integrations
- ##### [ecs](examples/elastigroup-ecs.yml)
- ##### [kubernetes](examples/elastigroup-kubernetes.yml)
- ##### [nomad](examples/elastigroup-nomad.yml)
- ##### [docker swarm](examples/elastigroup-docker-swarm.yml)
- ##### [code-deploy](examples/elastigroup-code-deploy.yml)
- ##### [route53](examples/elastigroup-route53.yml)
- ##### [elastic-beanstalk](examples/elastigroup-elastic-beanstalk.yml)
- ##### [rancher](examples/elastigroup-rancher.yml)
