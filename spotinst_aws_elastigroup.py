#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

import os

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}
DOCUMENTATION = """
---
module: spotinst_aws_elastigroup
version_added: 2.5
short_description: Create, update or delete Spotinst AWS Elastigroups
author: Spotinst
description:
  - Can create, update, or delete Spotinst AWS Elastigroups
    Launch configuration is part of the elastigroup configuration,
    no additional modules are necessary for handling the launch configuration.
    The credentials file should be in this location: ~/.spotinst/credentials
    The file must be a valid .yml file and contain the following fields
    default: #profile
        token: <YOUR TOKEN>
        account: <YOUR ACCOUNT>
    Full documentation available at 
    https://help.spotinst.com/hc/en-us/articles/115003530285-Ansible-
requirements:
  - spotinst-sdk >= 1.0.29
  - python >= 2.7
  - python >= 3.6
options:
  credentials_path:
    description:
      - credentials file path.
    default: ~/.spotinst/credentials
    type: str

  profile:
    description:
      - credentials profile to use
    default: default
    type: str

  account_id:
    description:
      - account id to authenticate with
    default: taken from credentials file
    type: str

  availability_vs_cost:
    description:
      - The strategy orientation
    required: true
    choices:
      - availabilityOriented
      - costOriented
      - balanced

  availability_zones:
    description:
      - availability zone configuration
    required: true
    supoptions:
      name:
        description: availability zone name
        type: str
      subnet_id:
        description: subnet id
        type: str
      placement_group_name:
        description: placement group name
        type: str

  block_device_mappings:
    description:
      - EBS configurations for elastigroup
    suboptions:
      device_name:
        description: ebs device name
        type: str
      virtual_name:
        description: ebs device virtual name
        type: str
      no_device:
        description: unmap a defined device
        type: bool
        default: ""
      ebs:
        description: ebs configuration
        suboptions:
          delete_on_termination:
            description: delete the volume when instance is terminated
            type: bool
          encrypted:
            description: ebs device encryption
            type: bool
          iops:
            description: ebs device iops
            type: int
          snapshot_id:
            description: snapshot id
            type: str
          volume_type:
            description: volume type
            default: standard
            choices:
              - standard
              - io1
              - gp2
              - st1
              - sc1
          volume_size:
            description: volume size
            type: int
          kms_key_id:
            description: kms key id
            type: str

  chef:
    description:
      - chef integration configuration
    suboptions:
        user:
          description: user name
          type: str
        pem_key:
          description: pem key
          type: str
        chef_version:
          description: version
          type: str

  code_deploy:
    description:
      - code deploy integration configuration
    suboptions:
      deployment_groups:
        description: deployment groups configurations
        type: list
        suboptions:
          application_name:
            description: application name
            type: str
          deployment_group_name:
            description: deployment group name
            type: str
      clean_up_on_failure:
        description: clean up on failure
        type: bool
      terminate_instance_on_failure:
        description: terminate instance on failure
        type: bool

  docker_swarm:
    description:
      - (Object) The Docker Swarm integration configuration.;
        Expects the following keys -
        master_host (String),
        master_port (Integer),
        auto_scale (Object expects the following keys -
        is_enabled (Boolean),
        cooldown (Integer),
        headroom (Object expects the following keys -
        cpu_per_unit (Integer),
        memory_per_unit (Integer),
        num_of_units (Integer)),
        key (String),
        value (String)),
        down (Object expecting the following key -
        down_evaluation_periods (Integer)))

  draining_timeout:
    description:
      - (Integer) Time for instance to be drained 
      from incoming requests and deregistered from ELB before termination.

  ebs_optimized:
    description:
      - (Boolean) Enable EBS optimization for supported instances which are not enabled by default.;
        Note - additional charges will be applied.

  ecs:
    description:
      - (Object) The ECS integration configuration.;
        Expects the following keys -
        cluster_name (String),
        auto_scale (Object expects the following keys -
        is_enabled (Boolean),
        is_auto_config (Boolean),
        cooldown (Integer),
        headroom (Object expects the following keys -
        cpu_per_unit (Integer),
        memory_per_unit (Integer),
        num_of_units (Integer)),
        attributes (List of Objects expecting the following keys -
        key (String),
        value (String)),
        down (Object expecting the following key -
        down_evaluation_periods (Integer)))

  elastic_beanstalk:
    description:
      - (Object) The ElasticBeanstalk integration configuration.;
      Expects the following keys -
      environment_id (String),
      deployment_preferences (Object expects the following keys -
      automatic_roll (Boolean),
      batch_size_percentage (Integer),
      grace_period (Integer),
      strategy (Object expects the following keys -
      action (String),
      should_drain_instances (Boolean)))

  elastic_ips:
    description:
      - (List of Strings) List of ElasticIps Allocation Ids to associate to the group instances

  fallback_to_od:
    description:
      - (Boolean) In case of no spots available, Elastigroup will launch an On-demand instance instead

  health_check_grace_period:
    description:
      - (Integer) The amount of time, in seconds, after the instance has launched to start and check its health.
    default: 300

  health_check_unhealthy_duration_before_replacement:
    description:
      - (Integer) Minimal mount of time instance should be unhealthy for us to consider it unhealthy.

  health_check_type:
    choices:
      - ELB
      - HCS
      - TARGET_GROUP
      - MLB
      - EC2
    description:
      - (String) The service to use for the health check.

  iam_role_name:
    description:
      - (String) The instance profile iamRole name
      - Only use iam_role_arn, or iam_role_name

  iam_role_arn:
    description:
      - (String) The instance profile iamRole arn
      - Only use iam_role_arn, or iam_role_name

  id:
    description:
      - (String) The group id if it already exists and you want to update, or delete it.
        This will not work unless the uniqueness_by field is set to id.
        When this is set, and the uniqueness_by field is set, the group will either be updated or deleted,
        but not created.

  ignore_changes:
    choices:
      - image_id
      - target
    description:
      - (List of Strings) list of fields on which changes should be ignored when updating

  image_id:
    description:
      - (String) The image Id used to launch the instance.;
        In case of conflict between Instance type and image type, an error will be returned
    required: true

  key_pair:
    description:
      - (String) Specify a Key Pair to attach to the instances
    required: true

  kubernetes:
    description:
      - (Object) The Kubernetes integration configuration.;
        Expects the following keys -
        api_server (String),
        token (String),
        integration_mode (String),
        cluster_identifier (String),
        auto_scale (Object expects the following keys -
        is_enabled (Boolean),
        is_auto_config (Boolean),
        cooldown (Integer),
        headroom (Object expects the following keys -
        cpu_per_unit (Integer),
        memory_per_unit (Integer),
        num_of_units (Integer)),
        labels (List of Objects expecting the following keys -
        key (String),
        value (String)),
        down (Object expecting the following key -
        down_evaluation_periods (Integer)))

  lifetime_period:
    description:
      - (String) lifetime period

  load_balancers:
    description:
      - (List of Strings) List of classic ELB names

  max_size:
    description:
      - (Integer) The upper limit number of instances that you can scale up to
    required: true

  mesosphere:
    description:
      - (Object) The Mesosphere integration configuration.
        Expects the following key -
        api_server (String)

  min_size:
    description:
      - (Integer) The lower limit number of instances that you can scale down to
    required: true

  mlb_load_balancers:
    description:
      - (List of Objects representing mlb's expecting the following keys -
      target_set_id (String)
      balancer_id (String)
      auto_weight (String)
      az_awareness (String)
      type (String) MULTAI_TARGET_SET

  mlb_runtime:
    description:
      - (Object) The Spotinst MLB Runtime integration configuration.;
      deployment_id (String) The runtime's deployment id

  monitoring:
    description:
      - (Boolean) Describes whether instance Enhanced Monitoring is enabled
    required: true

  name:
    description:
      - (String) Unique name for elastigroup to be created, updated or deleted
    required: true

  network_interfaces:
    description:
      - (List of Objects) a list of hash/dictionaries of network interfaces to add to the elastigroup;
        '[{"key":"value", "key":"value"}]';
        keys allowed are -
        description (String),
        device_index (Integer),
        secondary_private_ip_address_count (Integer),
        associate_public_ip_address (Boolean),
        delete_on_termination (Boolean),
        groups (List of Strings),
        network_interface_id (String),
        private_ip_address (String),
        subnet_id (String),
        associate_ipv6_address (Boolean),
        private_ip_addresses (List of Objects, Keys are privateIpAddress (String, required) and primary (Boolean))

  nomad:
    description:
      - (Object) The Nomad integration configuration.;
        Expects the following keys-
        master_host (String),
        master_port (Integer),
        acl_token (String),
        auto_scale (Object expects the following keys -
        is_enabled (Boolean),
        cooldown (Integer),
        headroom (Object expects the following keys -
        cpu_per_unit (Integer),
        memory_per_unit (Integer),
        num_of_units (Integer)),
        constraints (List of Objects expecting the following keys -
        key (String),
        value (String)),
        down (Object expecting the following key -
        down_evaluation_periods (Integer)))


  on_demand_count:
    description:
      - (Integer) Required if risk is not set
      - Number of on demand instances to launch. All other instances will be spot instances.;
        Either set this parameter or the risk parameter

  on_demand_instance_type:
    description:
      - (String) On-demand instance type that will be provisioned
    required: true

  opsworks:
    description:
      - (Object) The elastigroup OpsWorks integration configration.;
        Expects the following key -
        layer_id (String),
        stark_type (String)

  persistence:
    description:
      - (Object) The Stateful elastigroup configration.;
        Accepts the following keys -
        should_persist_root_device (Boolean),
        should_persist_block_devices (Boolean),
        should_persist_private_ip (Boolean),
        block_devices_mode (String)

  preferred_availability_zones:
    description:
      - (List) The preferred availability zones instance should spin instances in.;

  preferred_spot_instance_types:
    description:
      - (List) The preferred spot instance types.;

  private_ips:
    description:
      - (List) List of Private IPs to associate to the group instances.;

  product:
    choices:
      - Linux/UNIX
      - SUSE Linux
      - Windows
      - Linux/UNIX (Amazon VPC)
      - SUSE Linux (Amazon VPC)
      - Windows
    description:
      - (String) Operation system type._
    required: true

  rancher:
    description:
      - (Object) The Rancher integration configuration.;
        Expects the following keys -
        access_key (String),
        secret_key (String),
        master_host (String)

  revert_to_spot:
    description:
      - (Object) Hold settings for strategy correction - replacing On-Demand for Spot instances.;
        Expects the following keys -
        perform_at (String),
        time_windows (List of Strings representing the time windows)

  right_scale:
    description:
      - (Object) The Rightscale integration configuration.;
        Expects the following keys -
        account_id (String),
        refresh_token (String)
        region (String)

  risk:
    description:
      - (Integer) required if on demand is not set. The percentage of Spot instances to launch (0 - 100).

  route53:
    description:
      - (Object) The Route53 integration configuration.;
        Expects the following key -
        domains (List of Objects expecting the following keys -
        hosted_zone_id (String),
        record_sets (List of Objects expecting the following keys -
        name (String)
        use_public_ip (Boolean)))

  roll_config:
    description:
      - (Object) Roll configuration.;
        If you would like the group to roll after updating, please use this feature.
        Accepts the following keys -
        batch_size_percentage(Integer, Required),
        grace_period - (Integer, Required),
        health_check_type(String, Optional)

  scheduled_tasks:
    description:
      - (List of Objects) a list of hash/dictionaries of scheduled tasks to configure in the elastigroup;
        '[{"key":"value", "key":"value"}]';
        keys allowed are -
        adjustment (Integer),
        scale_target_capacity (Integer),
        scale_min_capacity (Integer),
        scale_max_capacity (Integer),
        adjustment_percentage (Integer),
        batch_size_percentage (Integer),
        cron_expression (String),
        frequency (String),
        grace_period (Integer),
        task_type (String, required),
        is_enabled (Boolean),
        start_time (String)

  security_group_ids:
    description:
      - (List of Strings) One or more security group IDs. ;
        In case of update it will override the existing Security Group with the new given array
    required: true

  shut_down_script:
    description:
      - (String) The Base64-encoded shutdown script that executes prior to instance termination.
        Encode before setting.

  signals:
    description:
      - (List of Objects) a list of hash/dictionaries of signals to configure in the elastigroup;
        keys allowed are -
        name (String, required),
        timeout (Integer)

  spin_up_time:
    description:
      - (Integer) spin up time, in seconds, for the instance

  spot_instance_types:
    description:
      - (List of Strings) Spot instance type that will be provisioned.
    required: true

  state:
    choices:
      - present
      - absent
    description:
      - (String) create or delete the elastigroup

  stateful_deallocation_should_delete_network_interfaces:
    description:
      - (Boolean) Enable deletion of network interfaces on stateful group deletion

  stateful_deallocation_should_delete_snapshots:
    description:
      - (Boolean) Enable deletion of snapshots on stateful group deletion

  stateful_deallocation_should_delete_images:
    description:
      - (Boolean) Enable deletion of images on stateful group deletion

  stateful_deallocation_should_delete_volumes:
    description:
      - (Boolean) Enable deletion of volumes on stateful group deletion

  subnet_ids:
    description:
      - (List) A comma-separated list of subnet identifiers for your group

  tags:
    description:
      - (List of tagKey:tagValue paris) a list of tags to configure in the elastigroup. Please specify list of keys
      and values (key colon value);

  target:
    description:
      - (Integer) The number of instances to launch
    required: true

  target_group_arns:
    description:
      - (List of Strings) List of target group arns instances should be registered to

  tenancy:
    choices:
      - default
      - dedicated
    description:
      - (String) dedicated vs shared tenancy

  terminate_at_end_of_billing_hour:
    description:
      - (Boolean) terminate at the end of billing hour

  unit:
    choices:
      - instance
      - weight
    description:
      - (String) The capacity unit to launch instances by.
    required: true

  up_scaling_policies:
    description:
      - (List of Objects) a list of hash/dictionaries of scaling policies to configure in the elastigroup;
        '[{"key":"value", "key":"value"}]';
        keys allowed are -
        policy_name (String, required),
        namespace (String, required),
        metric_name (String, required),
        dimensions (List of Objects, Keys allowed are name (String, required) and value (String)),
        statistic (String, required),
        extended_statistic (String),
        evaluation_periods (String, required),
        period (String, required),
        threshold (String, required),
        cooldown (String, required),
        unit (String, required),
        operator (String, required),
        action_type (String, required),
        adjustment (String),
        min_target_capacity (String),
        target (String),
        maximum (String),
        minimum (String),
        source (String)


  down_scaling_policies:
    description:
      - (List of Objects) a list of hash/dictionaries of scaling policies to configure in the elastigroup;
        '[{"key":"value", "key":"value"}]';
        keys allowed are -
        policy_name (String, required),
        namespace (String, required),
        metric_name (String, required),
        dimensions ((List of Objects), Keys allowed are name (String, required) and value (String)),
        statistic (String, required),
        extended_statistic (String),
        evaluation_periods (String, required),
        period (String, required),
        threshold (String, required),
        cooldown (String, required),
        unit (String, required),
        operator (String, required),
        action_type (String, required),
        adjustment (String),
        max_target_capacity (String),
        target (String),
        maximum (String),
        minimum (String),
        source (String)

  target_tracking_policies:
    description:
      - (List of Objects) a list of hash/dictionaries of target tracking policies to configure in the elastigroup;
        '[{"key":"value", "key":"value"}]';
        keys allowed are -
        policy_name (String, required),
        namespace (String, required),
        source (String, required),
        metric_name (String, required),
        statistic (String, required),
        unit (String, required),
        cooldown (String, required),
        target (String, required)

  uniqueness_by:
    choices:
      - id
      - name
    description:
      - (String) If your group names are not unique, you may use this feature to update or delete a specific group.
        Whenever this property is set, you must set a group_id in order to update or delete a group, otherwise a
        group will be created.


  user_data:
    description:
      - (String) Base64-encoded MIME user data. Encode before setting the value.


  utilize_reserved_instances:
    description:
      - (Boolean) In case of any available Reserved Instances,
         Elastigroup will utilize your reservations before purchasing Spot instances.


  wait_for_instances:
    description:
      - (Boolean) Whether or not the elastigroup creation / update actions should wait for the instances to spin


  wait_timeout:
    description:
      - (Integer) How long the module should wait
      for instances before failing the action.;
        Only works if wait_for_instances is True.

"""
EXAMPLES = '''
#In this basic example, we create a simple elastigroup

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

#In this advanced example, we create an elastigroup with
#  - user data and shutdown script
#  - multiple EBS device mappings for the instances in this group
#  - network interfaces configuration for the instances in this group
#  - revert to spot configuration,
which is the time frame at which Spotinst tries to spin spots instead of on-demands
#  - preferred availability zones in which to spin instances
#  - preferred spot instance types to launch

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

#In this example, we create an elastigroup and wait 600 seconds
to retrieve the instances, and use their instance ids

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
              subnet_id: subnet-123c
            - name: us-east-2b
              subnet_id: subnet-123b
            - name: us-east-2a
              subnet_id: subnet-123a
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

#Integrate and connect your instances
AWS's ELB and ALB along with Spotinst's MLB

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
            - "arn:aws:elb:us-west-2:123:targetgroup/TestTargetGroup/123abc"
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

#Perform scheduled actions on your elastigroup
such as scale, instance count adjustments etc.

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

#Persist your mounted root & data volumes along with connected ip addresses

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

#Scale your elastigroup using up/down and
target tracking scaling policies with a variety of adjustment operations

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

#Integrate and Spotinst elastigroup with AWS's CodeDeploy

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
          code_deploy:
            deployment_groups:
              - application_name: test-app-1
                deployment_group_name: test-deployment-1
              - application_name: test-app-1
                deployment_group_name: test-deployment-2
            clean_up_on_failure: false
            terminate_instance_on_failure: true
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

#Integrate and Spotinst elastigroup with Docker Swarm

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
          docker_swarm:
            master_host: test-domain.com
            master_port: 80
            auto_scale:
              is_enabled: true
              cooldown: 300
              headroom:
                cpu_per_unit: 100
                memory_per_unit: 100
                num_of_units: 100
              down:
                 evaluation_periods: 3
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

#Integrate and Spotinst elastigroup with AWS's ECS

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
          ecs:
            cluster_name: test-cluster-name
            auto_scale:
              is_enabled: true
              is_auto_config: false
              cooldown: 300
              headroom:
                cpu_per_unit: 100
                memory_per_unit: 100
                num_of_units: 100
              attributes:
                - key: test_key
                  value: test_value
                - key: test_key1
                  value: test_value1
              down:
            evaluation_periods: 3
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


#Integrate and Spotinst elastigroup with AWS's ElasticBeanstalk

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
          elastic_beanstalk:
            environment_id: test-environment
            deployment_preferences:
              automatic_roll: true
              batch_size_percentage: 50
              grace_period: 600
              strategy:
                action: REPLACE_SERVER
                should_drain_instances: true
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

#Integrate and Spotinst elastigroup with Kubernetes

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
          kubernetes:
            cluster_identifier: test-cluster-id
            api-server: 127.0.0.1
            token: test-secret
            integration_mode: pod
            auto_scale:
              is_enabled: true
              is_auto_config: false
              cooldown: 300
              headroom:
                cpu_per_unit: 100
                memory_per_unit: 100
                num_of_units: 100
              labels:
                - key: test_key
                  value: test_value
                - key: test_key1
                  value: test_value1
              down:
                evaluation_periods: 3
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

#Integrate and Spotinst elastigroup with Hashicorp's Nomad

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
          nomad:
            master_host: test-domain.com
            master_port: 80
            acl_token: test-secret
            auto_scale:
              is_enabled: true
              cooldown: 300
              headroom:
                cpu_per_unit: 100
                memory_per_unit: 100
                num_of_units: 100
              constraints:
                - key: ${test.test}
                  value: test_value
                - key: ${test.test1}
                  value: test_value1
              down:
                 evaluation_periods: 3
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

#Integrate and Spotinst elastigroup with AWS's Route53

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
          route53:
            domains:
              - hosted_zone_id: abc234
                record_sets:
                  - name: test-hosted-zone1
                    use_public_ip: true
                  - name: test1
                    use_public_ip: false
              - hosted_zone_id: abc123
                record_sets:
                  - name: test-hosted-zone2
                    use_public_ip: false
                  - name: test2
                    use_public_ip: true
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

'''
RETURN = '''
---
instances:
    description: List of active elastigroup instances and their details.
    returned: success
    type: dict
    sample: [
         {
            "spotInstanceRequestId": "sir-regs25zp",
            "instanceId": "i-09640ad8678234c",
            "instanceType": "m4.large",
            "product": "Linux/UNIX",
            "availabilityZone": "us-west-2b",
            "privateIp": "180.0.2.244",
            "createdAt": "2017-07-17T12:46:18.000Z",
            "status": "fulfilled"
        }
    ]
group_id:
    description: Created / Updated group's ID.
    returned: success
    type: string
    sample: "sig-12345"

'''

version = '1.0.3'

HAS_SPOTINST_SDK = False
DEFAULT_CREDENTIALS_FILE = os.path.join(
    os.path.expanduser("~"), '.spotinst', 'credentials')
__metaclass__ = type

import time
from ansible.module_utils.basic import AnsibleModule

try:
    import spotinst_sdk
    from spotinst_sdk import SpotinstClientException

    HAS_SPOTINST_SDK = True

except ImportError:
    pass

eni_fields = ('description',
              'device_index',
              'secondary_private_ip_address_count',
              'associate_public_ip_address',
              'delete_on_termination',
              'groups',
              'network_interface_id',
              'private_ip_address',
              'subnet_id',
              'associate_ipv6_address')

private_ip_fields = ('private_ip_address',
                     'primary')

capacity_fields = (dict(ansible_field_name='min_size',
                        spotinst_field_name='minimum'),
                   dict(ansible_field_name='max_size',
                        spotinst_field_name='maximum'),
                   'target',
                   'unit')

lspec_fields = ('user_data',
                'key_pair',
                'tenancy',
                'shutdown_script',
                'monitoring',
                'ebs_optimized',
                'image_id',
                'health_check_type',
                'health_check_grace_period',
                'health_check_unhealthy_duration_before_replacement',
                'security_group_ids')

iam_fields = (dict(ansible_field_name='iam_role_name',
                   spotinst_field_name='name'),
              dict(ansible_field_name='iam_role_arn',
                   spotinst_field_name='arn'))

scheduled_task_fields = ('adjustment',
                         'adjustment_percentage',
                         'batch_size_percentage',
                         'cron_expression',
                         'frequency',
                         'grace_period',
                         'task_type',
                         'is_enabled',
                         'scale_target_capacity',
                         'scale_min_capacity',
                         'scale_max_capacity',
                         'start_time')

scaling_policy_fields = ('policy_name',
                         'namespace',
                         'metric_name',
                         'dimensions',
                         'statistic',
                         'evaluation_periods',
                         'period',
                         'threshold',
                         'cooldown',
                         'unit',
                         'operator',
                         'source',
                         'extended_statistic')

tracking_policy_fields = ('policy_name',
                          'namespace',
                          'source',
                          'metric_name',
                          'statistic',
                          'unit',
                          'cooldown',
                          'target',
                          'threshold')

action_fields = (dict(ansible_field_name='action_type',
                      spotinst_field_name='type'),
                 'adjustment',
                 'min_target_capacity',
                 'max_target_capacity',
                 'target',
                 'minimum',
                 'maximum')

signal_fields = ('name',
                 'timeout')

multai_lb_fields = ('balancer_id',
                    'project_id',
                    'target_set_id',
                    'az_awareness',
                    'auto_weight')

persistence_fields = ('should_persist_root_device',
                      'should_persist_block_devices',
                      'should_persist_private_ip',
                      'block_devices_mode')

revert_to_spot_fields = ('perform_at',)

strategy_fields = ('risk',
                   'utilize_reserved_instances',
                   'fallback_to_od',
                   'on_demand_count',
                   'availability_vs_cost',
                   'draining_timeout',
                   'spin_up_time',
                   'lifetime_period')

ebs_fields = ('delete_on_termination',
              'encrypted',
              'iops',
              'snapshot_id',
              'volume_type',
              'volume_size')

bdm_fields = ('device_name',
              'virtual_name',
              'no_device')

kubernetes_fields = ('api_server',
                     'token',
                     'integration_mode',
                     'cluster_identifier')

kubernetes_auto_scale_fields = ('is_enabled', 'is_auto_config', 'cooldown')

kubernetes_headroom_fields = (
    'cpu_per_unit',
    'memory_per_unit',
    'num_of_units')

kubernetes_labels_fields = ('key', 'value')

kubernetes_down_fields = ('evaluation_periods',)

nomad_fields = ('master_host', 'master_port', 'acl_token')

nomad_auto_scale_fields = ('is_enabled', 'is_auto_config', 'cooldown')

nomad_headroom_fields = ('cpu_per_unit', 'memory_per_unit', 'num_of_units')

nomad_constraints_fields = ('key', 'value')

nomad_down_fields = ('evaluation_periods',)

docker_swarm_fields = ('master_host', 'master_port')

docker_swarm_auto_scale_fields = ('is_enabled', 'cooldown')

docker_swarm_headroom_fields = (
    'cpu_per_unit',
    'memory_per_unit',
    'num_of_units')

docker_swarm_down_fields = ('evaluation_periods',)

route53_domain_fields = ('hosted_zone_id',)

route53_record_set_fields = ('name', 'use_public_ip')

right_scale_fields = ('account_id',
                      'refresh_token',
                      'region')

code_deploy_fields = ('clean_up_on_failure', 'terminate_instance_on_failure')

code_deploy_deployment_fields = ('application_name', 'deployment_group_name')

mlb_runtime_fields = ('deployment_id',)

mlb_load_balancers_fields = (
    'type',
    'target_set_id',
    'balancer_id',
    'auto_weight',
    'az_awareness')

elastic_beanstalk_fields = ('environment_id',)

elastic_beanstalk_deployment_fields = ('automatic_roll',
                                       'batch_size_percentage',
                                       'grace_period')

elastic_beanstalk_strategy_fields = ('action', 'should_drain_instances')

rancher_fields = ('access_key',
                  'secret_key',
                  'master_host')

chef_fields = ('chef_server',
               'organization',
               'user',
               'pem_key',
               'chef_version')

az_fields = ('name',
             'subnet_id',
             'placement_group_name')

stateful_deallocation_fields = (
    dict(
        ansible_field_name='stateful_deallocation_should_delete_images',
        spotinst_field_name='should_delete_images'),
    dict(
        ansible_field_name='stateful_deallocation_should_delete_snapshots',
        spotinst_field_name='should_delete_snapshots'),
    dict(
        ansible_field_name='stateful_deallocation_should_delete_network_interfaces',
        spotinst_field_name='should_delete_network_interfaces'),
    dict(
        ansible_field_name='stateful_deallocation_should_delete_volumes',
        spotinst_field_name='should_delete_volumes'))

opsworks_fields = ('layer_id', 'stack_type')

scaling_strategy_fields = ('terminate_at_end_of_billing_hour',)

mesosphere_fields = ('api_server',)

ecs_fields = ('cluster_name',)

ecs_auto_scale_fields = ('is_enabled', 'is_auto_config', 'cooldown')

ecs_headroom_fields = ('cpu_per_unit', 'memory_per_unit', 'num_of_units')

ecs_attributes_fields = ('key', 'value')

ecs_down_fields = ('evaluation_periods',)

multai_fields = ('multai_token',)


def handle_elastigroup(client, module):
    has_changed = False
    should_create = False
    group_id = None
    message = 'None'

    name = module.params.get('name')
    state = module.params.get('state')
    uniqueness_by = module.params.get('uniqueness_by')
    external_group_id = module.params.get('id')

    if uniqueness_by == 'id':
        if external_group_id is None:
            should_create = True
        else:
            should_create = False
            group_id = external_group_id
    else:
        groups = client.get_elastigroups()
        should_create, group_id = find_group_with_same_name(groups, name)

    if should_create is True:
        if state == 'present':
            eg = expand_elastigroup(module, is_update=False)
            module.debug(str(" [INFO] " + message + "\n"))
            group = client.create_elastigroup(group=eg)
            group_id = group['id']
            message = 'Created group Successfully.'
            has_changed = True

        elif state == 'absent':
            message = 'Cannot delete non-existent group.'
            has_changed = False
    else:
        eg = expand_elastigroup(module, is_update=True)

        if state == 'present':
            group = client.update_elastigroup(
                group_update=eg, group_id=group_id)
            message = 'Updated group successfully.'

            try:
                roll_config = module.params.get('roll_config')
                if roll_config:
                    eg_roll = spotinst_sdk.aws_elastigroup.Roll(
                        batch_size_percentage=roll_config.get(
                            'batch_size_percentage'),
                        grace_period=roll_config.get('grace_period'),
                        health_check_type=roll_config.get('health_check_type'))
                    roll_response = client.roll_group(
                        group_roll=eg_roll, group_id=group_id)
                    message = \
                        'Updated and started rolling the group successfully.'
            except SpotinstClientException as exc:
                message = 'Updated group successfully, ' \
                          'but failed to perform roll. Error:' + \
                          str(exc)
            has_changed = True

        elif state == 'absent':
            try:
                stfl_dealloc_request = expand_fields(
                    stateful_deallocation_fields,
                    module.params, 'StatefulDeallocation')
                if stfl_dealloc_request. \
                        should_delete_network_interfaces is True or \
                        stfl_dealloc_request.should_delete_images is True or \
                        stfl_dealloc_request.should_delete_volumes is True or \
                        stfl_dealloc_request.should_delete_snapshots is True:
                    client.delete_elastigroup_with_deallocation(
                        group_id=group_id,
                        stateful_deallocation=stfl_dealloc_request)
                else:
                    client.delete_elastigroup(group_id=group_id)
            except SpotinstClientException as exc:
                if "GROUP_DOESNT_EXIST" in exc.message:
                    pass
                else:
                    module.fail_json(
                        msg="Error while attempting to delete group :"
                            " " + exc.message)

            message = 'Deleted group successfully.'
            has_changed = True

    return group_id, message, has_changed


def retrieve_group_instances(client, module, group_id):
    wait_timeout = module.params.get('wait_timeout')
    wait_for_instances = module.params.get('wait_for_instances')

    if wait_timeout is None:
        wait_timeout = 300

    wait_timeout = time.time() + wait_timeout
    target = module.params.get('target')
    state = module.params.get('state')
    instances = list()

    if state == 'present' and \
            group_id is not None and \
            wait_for_instances is True:

        is_amount_fulfilled = False
        while is_amount_fulfilled is False and wait_timeout > time.time():
            instances = list()
            amount_of_fulfilled_instances = 0
            active_instances = client.get_elastigroup_active_instances(
                group_id=group_id)

            for active_instance in active_instances:
                if active_instance.get('private_ip') is not None:
                    amount_of_fulfilled_instances += 1
                    instances.append(active_instance)

            if amount_of_fulfilled_instances >= target:
                is_amount_fulfilled = True

            time.sleep(10)

    return instances


def find_group_with_same_name(groups, name):
    for group in groups:
        if group['name'] == name:
            return False, group.get('id')

    return True, None


def expand_elastigroup(module, is_update):
    do_not_update = module.params['do_not_update']
    name = module.params.get('name')

    eg = spotinst_sdk.aws_elastigroup.Elastigroup()
    description = module.params.get('description')

    if name is not None:
        eg.name = name
    if description is not None:
        eg.description = description

    # Capacity
    expand_capacity(eg, module, is_update, do_not_update)
    # Strategy
    expand_strategy(eg, module)
    # Scaling
    expand_scaling(eg, module)
    # Third party integrations
    expand_integrations(eg, module)
    # Compute
    expand_compute(eg, module, is_update, do_not_update)
    # Scheduling
    expand_scheduled_tasks(eg, module)

    return eg


def expand_compute(eg, module, is_update, do_not_update):
    elastic_ips = module.params['elastic_ips']
    on_demand_instance_type = module.params.get('on_demand_instance_type')
    spot_instance_types = module.params['spot_instance_types']
    availability_zones_list = module.params['availability_zones']
    product = module.params.get('product')
    preferred_availability_zones = module.params.get(
        'preferred_availability_zones')
    private_ips = module.params.get('private_ips')
    subnet_ids = module.params.get('subnet_ids')
    preferred_spot_instance_types = module.params.get(
        'preferred_spot_instance_types')

    eg_compute = spotinst_sdk.aws_elastigroup.Compute()

    if product is not None:
        # Only put product on group creation
        if is_update is not True:
            eg_compute.product = product

    if elastic_ips is not None:
        eg_compute.elastic_ips = elastic_ips

    if private_ips:
        eg_compute.private_ips = private_ips

    if subnet_ids:
        eg_compute.subnet_ids = subnet_ids

    if on_demand_instance_type or spot_instance_types is not None:
        eg_instance_types = spotinst_sdk.aws_elastigroup.InstanceTypes()

        if on_demand_instance_type is not None:
            eg_instance_types.spot = spot_instance_types

        if spot_instance_types is not None:
            eg_instance_types.ondemand = on_demand_instance_type

        if preferred_spot_instance_types:
            eg_instance_types.preferred_spot = preferred_spot_instance_types

        if eg_instance_types.spot is not None \
                or eg_instance_types.ondemand is not None:
            eg_compute.instance_types = eg_instance_types

    if preferred_availability_zones:
        eg_compute.preferred_availability_zones = preferred_availability_zones

    eg_compute.availability_zones = expand_list(
        availability_zones_list, az_fields, 'AvailabilityZone')
    expand_launch_spec(eg_compute, module, is_update, do_not_update)

    eg.compute = eg_compute


def expand_launch_spec(eg_compute, module, is_update, do_not_update):
    eg_launch_spec = expand_fields(
        lspec_fields,
        module.params,
        'LaunchSpecification')

    if module.params['iam_role_arn'] is not None \
            or module.params['iam_role_name'] is not None:
        eg_launch_spec.iam_role = expand_fields(
            iam_fields, module.params, 'IamRole')

    tags = module.params['tags']
    load_balancers = module.params['load_balancers']
    mlb_load_balancers = module.params['mlb_load_balancers']
    target_group_arns = module.params['target_group_arns']
    block_device_mappings = module.params['block_device_mappings']
    network_interfaces = module.params['network_interfaces']

    if is_update is True:
        if 'image_id' in do_not_update:
            delattr(eg_launch_spec, 'image_id')

    expand_tags(eg_launch_spec, tags)

    expand_load_balancers(
        eg_launch_spec,
        load_balancers,
        target_group_arns,
        mlb_load_balancers)

    expand_block_device_mappings(eg_launch_spec, block_device_mappings)

    expand_network_interfaces(eg_launch_spec, network_interfaces)

    eg_compute.launch_specification = eg_launch_spec


def expand_integrations(eg, module):
    rancher = module.params.get('rancher')
    mesosphere = module.params.get('mesosphere')
    ecs = module.params.get('ecs')
    kubernetes = module.params.get('kubernetes')
    right_scale = module.params.get('right_scale')
    opsworks = module.params.get('opsworks')
    chef = module.params.get('chef')
    nomad = module.params.get('nomad')
    docker_swarm = module.params.get('docker_swarm')
    route53 = module.params.get('route53')
    code_deploy = module.params.get('code_deploy')
    mlb_runtime = module.params.get('mlb_runtime')
    elastic_beanstalk = module.params.get('elastic_beanstalk')

    integration_exists = False

    eg_integrations = spotinst_sdk.aws_elastigroup.ThirdPartyIntegrations()

    if mesosphere is not None:
        eg_integrations.mesosphere = expand_fields(
            mesosphere_fields, mesosphere, 'Mesosphere')
        integration_exists = True

    if ecs is not None:
        expand_ecs(eg_integrations, ecs)
        integration_exists = True

    if nomad is not None:
        expand_nomad(eg_integrations, nomad)
        integration_exists = True

    if docker_swarm is not None:
        expand_docker_swarm(eg_integrations, docker_swarm)
        integration_exists = True

    if kubernetes is not None:
        expand_kubernetes(eg_integrations, kubernetes)
        integration_exists = True

    if route53 is not None:
        expand_route53(eg_integrations, route53)
        integration_exists = True

    if code_deploy is not None:
        expand_code_deploy(eg_integrations, code_deploy)
        integration_exists = True

    if mlb_runtime:
        eg_integrations.mlb_runtime = expand_fields(
            mlb_runtime_fields, mlb_runtime, 'MlbRuntimeConfiguration')
        integration_exists = True

    if right_scale is not None:
        eg_integrations.right_scale = expand_fields(
            right_scale_fields, right_scale, 'RightScaleConfiguration')
        integration_exists = True

    if opsworks is not None:
        eg_integrations.opsworks = expand_fields(
            opsworks_fields, opsworks, 'OpsWorksConfiguration')
        integration_exists = True

    if rancher is not None:
        eg_integrations.rancher = expand_fields(
            rancher_fields, rancher, 'Rancher')
        integration_exists = True

    if chef is not None:
        eg_integrations.chef = expand_fields(
            chef_fields, chef, 'ChefConfiguration')
        integration_exists = True

    if elastic_beanstalk:
        expand_elastic_beanstalk(eg_integrations, elastic_beanstalk)
        integration_exists = True

    if integration_exists:
        eg.third_parties_integration = eg_integrations


def expand_capacity(eg, module, is_update, do_not_update):
    eg_capacity = expand_fields(capacity_fields, module.params, 'Capacity')

    if is_update is True:
        delattr(eg_capacity, 'unit')

        if 'target' in do_not_update:
            delattr(eg_capacity, 'target')

    eg.capacity = eg_capacity


def expand_strategy(eg, module):
    persistence = module.params.get('persistence')
    signals = module.params.get('signals')
    revert_to_spot = module.params.get('revert_to_spot')

    eg_strategy = expand_fields(strategy_fields, module.params, 'Strategy')

    terminate_at_end_of_billing_hour = module.params.get(
        'terminate_at_end_of_billing_hour')

    if terminate_at_end_of_billing_hour is not None:
        eg_strategy.eg_scaling_strategy = expand_fields(
            scaling_strategy_fields, module.params, 'ScalingStrategy')

    if persistence is not None:
        eg_strategy.persistence = expand_fields(
            persistence_fields, persistence, 'Persistence')

    if signals is not None:
        eg_signals = expand_list(signals, signal_fields, 'Signal')

        if len(eg_signals) > 0:
            eg_strategy.signals = eg_signals

    if revert_to_spot:
        eg_strategy.revert_to_spot = expand_fields(
            revert_to_spot_fields, revert_to_spot, 'RevertToSpot')
        eg_strategy.revert_to_spot.time_windows = \
            revert_to_spot['time_windows']

    eg.strategy = eg_strategy


def expand_scheduled_tasks(eg, module):
    scheduled_tasks = module.params.get('scheduled_tasks')

    if scheduled_tasks is not None:
        eg_scheduling = spotinst_sdk.aws_elastigroup.Scheduling()

        eg_tasks = expand_list(
            scheduled_tasks,
            scheduled_task_fields,
            'ScheduledTask')

        if len(eg_tasks) > 0:
            eg_scheduling.tasks = eg_tasks
            eg.scheduling = eg_scheduling


def expand_load_balancers(
        eg_launchspec,
        load_balancers,
        target_group_arns,
        mlb_load_balancers):
    if load_balancers is not None or target_group_arns is not None:
        eg_load_balancers_config = \
            spotinst_sdk.aws_elastigroup.LoadBalancersConfig()
        eg_total_lbs = []

        if load_balancers is not None:
            for elb_name in load_balancers:
                eg_elb = spotinst_sdk.aws_elastigroup.LoadBalancer()
                if elb_name is not None:
                    eg_elb.name = elb_name
                    eg_elb.type = 'CLASSIC'
                    eg_total_lbs.append(eg_elb)

        if target_group_arns is not None:
            for target_arn in target_group_arns:
                eg_elb = spotinst_sdk.aws_elastigroup.LoadBalancer()
                if target_arn is not None:
                    eg_elb.arn = target_arn
                    eg_elb.type = 'TARGET_GROUP'
                    split_arn = target_arn.split("/")
                    target_group_name = split_arn[-2]
                    eg_elb.name = target_group_name

                    eg_total_lbs.append(eg_elb)

        if mlb_load_balancers:
            mlbs = expand_list(
                mlb_load_balancers,
                mlb_load_balancers_fields,
                'LoadBalancer')

            for mlb in mlbs:
                mlb.type = "MULTAI_TARGET_SET"

            eg_total_lbs.extend(mlbs)

        if len(eg_total_lbs) > 0:
            eg_load_balancers_config.load_balancers = eg_total_lbs
            eg_launchspec.load_balancers_config = eg_load_balancers_config


def expand_tags(eg_launchspec, tags):
    if tags is not None:
        eg_tags = []

        for tag in tags:
            eg_tag = spotinst_sdk.aws_elastigroup.Tag()
            keys = list(tag.keys())
            if keys:
                eg_tag.tag_key = keys[0]
            values = list(tag.values())
            if values:
                eg_tag.tag_value = values[0]

            eg_tags.append(eg_tag)

        if len(eg_tags) > 0:
            eg_launchspec.tags = eg_tags


def expand_block_device_mappings(eg_launchspec, bdms):
    if bdms is not None:
        eg_bdms = []

        for bdm in bdms:
            eg_bdm = expand_fields(bdm_fields, bdm, 'BlockDeviceMapping')

            if bdm.get('ebs') is not None:
                eg_bdm.ebs = expand_fields(ebs_fields, bdm.get('ebs'), 'EBS')

            eg_bdms.append(eg_bdm)

        if len(eg_bdms) > 0:
            eg_launchspec.block_device_mappings = eg_bdms


def expand_network_interfaces(eg_launchspec, enis):
    if enis is not None:
        eg_enis = []

        for eni in enis:
            eg_eni = expand_fields(eni_fields, eni, 'NetworkInterface')

            eg_pias = expand_list(
                eni.get('private_ip_addresses'),
                private_ip_fields,
                'PrivateIpAddress')

            if eg_pias is not None:
                eg_eni.private_ip_addresses = eg_pias

            eg_enis.append(eg_eni)

        if len(eg_enis) > 0:
            eg_launchspec.network_interfaces = eg_enis


def expand_scaling(eg, module):
    up_scaling_policies = module.params['up_scaling_policies']
    down_scaling_policies = module.params['down_scaling_policies']
    target_tracking_policies = module.params['target_tracking_policies']

    eg_scaling = spotinst_sdk.aws_elastigroup.Scaling()

    if up_scaling_policies is not None:
        eg_up_scaling_policies = expand_scaling_policies(up_scaling_policies)
        if len(eg_up_scaling_policies) > 0:
            eg_scaling.up = eg_up_scaling_policies

    if down_scaling_policies is not None:
        eg_down_scaling_policies = expand_scaling_policies(
            down_scaling_policies)
        if len(eg_down_scaling_policies) > 0:
            eg_scaling.down = eg_down_scaling_policies

    if target_tracking_policies is not None:
        eg_target_tracking_policies = expand_target_tracking_policies(
            target_tracking_policies)
        if len(eg_target_tracking_policies) > 0:
            eg_scaling.target = eg_target_tracking_policies

    if eg_scaling.down is not None \
            or eg_scaling.up is not None \
            or eg_scaling.target is not None:
        eg.scaling = eg_scaling


def expand_list(items, fields, class_name):
    if items is not None:
        new_objects_list = []
        for item in items:
            new_obj = expand_fields(fields, item, class_name)
            new_objects_list.append(new_obj)

        return new_objects_list


def expand_fields(fields, item, class_name):
    class_ = getattr(spotinst_sdk.aws_elastigroup, class_name)
    new_obj = class_()

    # Handle primitive fields
    if item is not None:
        for field in fields:
            if isinstance(field, dict):
                ansible_field_name = field['ansible_field_name']
                spotinst_field_name = field['spotinst_field_name']
            else:
                ansible_field_name = field
                spotinst_field_name = field
            if item.get(ansible_field_name) is not None:
                setattr(
                    new_obj,
                    spotinst_field_name,
                    item.get(ansible_field_name))

    return new_obj


def expand_scaling_policies(scaling_policies):
    eg_scaling_policies = []

    for policy in scaling_policies:
        eg_policy = expand_fields(
            scaling_policy_fields, policy, 'ScalingPolicy')
        eg_policy.action = expand_fields(
            action_fields, policy, 'ScalingPolicyAction')
        eg_scaling_policies.append(eg_policy)

    return eg_scaling_policies


def expand_target_tracking_policies(tracking_policies):
    eg_tracking_policies = []

    for policy in tracking_policies:
        eg_policy = expand_fields(
            tracking_policy_fields,
            policy,
            'TargetTrackingPolicy')
        eg_tracking_policies.append(eg_policy)

    return eg_tracking_policies


def expand_ecs(eg_integrations, ecs_config):
    ecs = expand_fields(ecs_fields, ecs_config, 'EcsConfiguration')
    ecs_auto_scale_config = ecs_config.get('auto_scale', None)

    if ecs_auto_scale_config:
        ecs.auto_scale = expand_fields(
            ecs_auto_scale_fields,
            ecs_auto_scale_config,
            'EcsAutoScaleConfiguration')

        ecs_headroom_config = ecs_auto_scale_config.get('headroom', None)
        if ecs_headroom_config:
            ecs.auto_scale.headroom = expand_fields(
                ecs_headroom_fields,
                ecs_headroom_config,
                'EcsAutoScalerHeadroomConfiguration')

        ecs_attributes_config = ecs_auto_scale_config.get('attributes', None)
        if ecs_attributes_config:
            ecs.auto_scale.attributes = expand_list(
                ecs_attributes_config,
                ecs_attributes_fields,
                'EcsAutoScalerAttributeConfiguration')

        ecs_down_config = ecs_auto_scale_config.get('down', None)
        if ecs_down_config:
            ecs.auto_scale.down = expand_fields(
                ecs_down_fields, ecs_down_config,
                'EcsAutoScalerDownConfiguration')
    eg_integrations.ecs = ecs


def expand_kubernetes(eg_integrations, kubernetes_config):
    kubernetes = expand_fields(
        kubernetes_fields,
        kubernetes_config,
        'KubernetesConfiguration')
    kubernetes_auto_scale_config = kubernetes_config.get('auto_scale', None)

    if kubernetes_auto_scale_config:
        kubernetes.auto_scale = expand_fields(
            kubernetes_auto_scale_fields,
            kubernetes_auto_scale_config,
            'KubernetesAutoScalerConfiguration')

        kubernetes_headroom_config = kubernetes_auto_scale_config.get(
            'auto_scale', None)
        if kubernetes_headroom_config:
            kubernetes.auto_scale.headroom = expand_fields(
                kubernetes_headroom_fields,
                kubernetes_headroom_config,
                'KubernetesAutoScalerHeadroomConfiguration')

        kubernetes_labels_config = kubernetes_auto_scale_config.get(
            'labels', None)
        if kubernetes_labels_config:
            kubernetes.auto_scale.labels = expand_list(
                kubernetes_labels_config,
                kubernetes_labels_fields,
                'KubernetesAutoScalerLabelsConfiguration')

        kubernetes_down_config = kubernetes_auto_scale_config.get('down', None)
        if kubernetes_down_config:
            kubernetes.auto_scale.down = expand_fields(
                kubernetes_down_fields,
                kubernetes_down_config,
                'KubernetesAutoScalerDownConfiguration')

    eg_integrations.kubernetes = kubernetes


def expand_nomad(eg_integrations, nomad_config):
    nomad = expand_fields(nomad_fields, nomad_config, 'NomadConfiguration')
    nomad_auto_scale_config = nomad_config.get('auto_scale', None)

    if nomad_auto_scale_config:
        nomad.auto_scale = expand_fields(
            nomad_auto_scale_fields,
            nomad_auto_scale_config,
            'NomadAutoScalerConfiguration')

        nomad_headroom_config = nomad_auto_scale_config.get('headroom', None)
        if nomad_headroom_config:
            nomad.auto_scale.headroom = expand_fields(
                nomad_headroom_fields,
                nomad_headroom_config,
                'NomadAutoScalerHeadroomConfiguration')

        nomad_constraints_config = nomad_auto_scale_config.get(
            'constraints', None)
        if nomad_constraints_config:
            nomad.auto_scale.constraints = expand_list(
                nomad_constraints_config,
                nomad_constraints_fields,
                'NomadAutoScalerConstraintsConfiguration')

        nomad_down_config = nomad_auto_scale_config.get('down', None)
        if nomad_down_config:
            nomad.auto_scale.down = expand_fields(
                nomad_down_fields,
                nomad_down_config,
                'NomadAutoScalerDownConfiguration')

    eg_integrations.nomad = nomad


def expand_docker_swarm(eg_integrations, docker_swarm_config):
    docker_swarm = expand_fields(
        docker_swarm_fields,
        docker_swarm_config,
        'DockerSwarmConfiguration')
    docker_swarm_auto_scale_config = docker_swarm_config.get(
        'auto_scale', None)

    if docker_swarm_auto_scale_config:
        docker_swarm.auto_scale = expand_fields(
            docker_swarm_auto_scale_fields,
            docker_swarm_auto_scale_config,
            'DockerSwarmAutoScalerConfiguration')

        docker_swarm_headroom_config = docker_swarm_auto_scale_config.get(
            'headroom', None)
        if docker_swarm_headroom_config:
            docker_swarm.auto_scale.headroom = expand_fields(
                docker_swarm_headroom_fields,
                docker_swarm_headroom_config,
                'DockerSwarmAutoScalerHeadroomConfiguration')

        docker_swarm_down_config = docker_swarm_auto_scale_config.get(
            'down', None)
        if docker_swarm_down_config:
            docker_swarm.auto_scale.down = expand_fields(
                docker_swarm_down_fields,
                docker_swarm_down_config,
                'DockerSwarmAutoScalerDownConfiguration')

    eg_integrations.docker_swarm = docker_swarm


def expand_route53(eg_integrations, route53_config):
    route53 = spotinst_sdk.aws_elastigroup.Route53Configuration()
    domains_configuration = route53_config.get('domains', None)

    if domains_configuration:
        route53.domains = expand_list(
            domains_configuration,
            route53_domain_fields,
            'Route53DomainsConfiguration')

        for i in range(len(route53.domains)):
            expanded_domain = route53.domains[i]
            raw_domain = domains_configuration[i]
            expanded_domain.record_sets = expand_list(
                raw_domain['record_sets'],
                route53_record_set_fields,
                'Route53RecordSetsConfiguration')

    eg_integrations.route53 = route53


def expand_code_deploy(eg_integrations, code_deploy_config):
    code_deploy = expand_fields(
        code_deploy_fields,
        code_deploy_config,
        'CodeDeployConfiguration')
    code_deploy_deployment_config = code_deploy_config.get(
        'deployment_groups', None)

    if code_deploy_deployment_config:
        code_deploy.deployment_groups = expand_list(
            code_deploy_deployment_config,
            code_deploy_deployment_fields,
            'CodeDeployDeploymentGroupsConfiguration')

    eg_integrations.code_deploy = code_deploy


def expand_elastic_beanstalk(eg_integrations, elastic_beanstalk_config):
    elastic_beanstalk = expand_fields(
        elastic_beanstalk_fields,
        elastic_beanstalk_config,
        'ElasticBeanstalk')
    elastic_beanstalk_deployment = elastic_beanstalk_config.get(
        'deployment_preferences', None)

    if elastic_beanstalk_deployment:
        elastic_beanstalk.deployment_preferences = expand_fields(
            elastic_beanstalk_deployment_fields,
            elastic_beanstalk_deployment,
            'DeploymentPreferences')
        if elastic_beanstalk.deployment_preferences:
            elastic_beanstalk.deployment_preferences.strategy = \
                expand_fields(elastic_beanstalk_strategy_fields,
                              elastic_beanstalk_deployment['strategy'],
                              'BeanstalkDeploymentStrategy')

    eg_integrations.elastic_beanstalk = elastic_beanstalk


def main():
    fields = dict(
        account_id=dict(type='str'),
        availability_vs_cost=dict(type='str', required=True),
        availability_zones=dict(type='list', required=True),
        block_device_mappings=dict(type='list'),
        chef=dict(type='dict'),
        credentials_path=dict(type='path', default="~/.spotinst/credentials"),
        do_not_update=dict(default=[], type='list'),
        down_scaling_policies=dict(type='list'),
        draining_timeout=dict(type='int'),
        ebs_optimized=dict(type='bool'),
        ecs=dict(type='dict'),
        elastic_beanstalk=dict(type='dict'),
        elastic_ips=dict(type='list'),
        fallback_to_od=dict(type='bool'),
        id=dict(type='str'),
        health_check_grace_period=dict(type='int'),
        health_check_type=dict(type='str'),
        health_check_unhealthy_duration_before_replacement=dict(type='int'),
        iam_role_arn=dict(type='str'),
        iam_role_name=dict(type='str'),
        image_id=dict(type='str', required=True),
        key_pair=dict(type='str'),
        kubernetes=dict(type='dict'),
        lifetime_period=dict(type='int'),
        load_balancers=dict(type='list'),
        max_size=dict(type='int', required=True),
        mesosphere=dict(type='dict'),
        min_size=dict(type='int', required=True),
        monitoring=dict(type='str'),
        multai_load_balancers=dict(type='list'),
        multai_token=dict(type='str'),
        name=dict(type='str', required=True),
        network_interfaces=dict(type='list'),
        on_demand_count=dict(type='int'),
        on_demand_instance_type=dict(type='str'),
        opsworks=dict(type='dict'),
        persistence=dict(type='dict'),
        product=dict(type='str', required=True),
        rancher=dict(type='dict'),
        right_scale=dict(type='dict'),
        risk=dict(type='int'),
        roll_config=dict(type='dict'),
        scheduled_tasks=dict(type='list'),
        security_group_ids=dict(type='list', required=True),
        shutdown_script=dict(type='str'),
        signals=dict(type='list'),
        spin_up_time=dict(type='int'),
        spot_instance_types=dict(type='list', required=True),
        state=dict(default='present',
                   choices=['present', 'absent']),
        stateful_deallocation_should_delete_images=dict(type='bool'),
        stateful_deallocation_should_delete_network_interfaces=dict(
            type='bool'),
        stateful_deallocation_should_delete_snapshots=dict(type='bool'),
        stateful_deallocation_should_delete_volumes=dict(type='bool'),
        tags=dict(type='list'),
        target=dict(type='int', required=True),
        target_group_arns=dict(type='list'),
        tenancy=dict(type='str'),
        terminate_at_end_of_billing_hour=dict(type='bool'),
        token=dict(type='str'),
        unit=dict(type='str'),
        user_data=dict(type='str'),
        utilize_reserved_instances=dict(type='bool'),
        uniqueness_by=dict(default='name', choices=['name', 'id']),
        up_scaling_policies=dict(type='list'),
        target_tracking_policies=dict(type='list'),
        wait_for_instances=dict(type='bool', default=False),
        wait_timeout=dict(type='int'),
        preferred_availability_zones=dict(type='list'),
        nomad=dict(type='dict'),
        docker_swarm=dict(type='dict'),
        route53=dict(type='dict'),
        code_deploy=dict(type='dict'),
        mlb_runtime=dict(type='dict'),
        mlb_load_balancers=dict(type='list'),
        private_ips=dict(type='list'),
        preferred_spot_instance_types=dict(type='list'),
        revert_to_spot=dict(type='dict'),
        profile=dict(type='str')
    )

    module = AnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(
            msg="the Spotinst SDK library is required. "
                "(pip install spotinst-sdk)")

    spotinst_user_agent = '{}/{}'.format('spotinst-ansible', version)

    # Retrieve creds file variables
    creds_file_loaded_vars = dict()

    try:
        credentials_path = module.params.get(
            'credentials_path', DEFAULT_CREDENTIALS_FILE)
        with open(credentials_path, "r") as creds:
            for line in creds:
                eq_index = line.find('=')
                var_name = line[:eq_index].strip()
                string_value = line[eq_index + 1:].strip()
                creds_file_loaded_vars[var_name] = string_value
    except IOError:
        pass
    # End of creds file retrieval

    token = module.params.get('token', None)
    if not token:
        token = creds_file_loaded_vars.get("token", None)

    account = module.params.get('account_id', None)
    if not account:
        account = creds_file_loaded_vars.get("account", None)

    profile = module.params.get('profile', None)

    client = spotinst_sdk.SpotinstClient(auth_token=token,
                                         account_id=account,
                                         profile=profile,
                                         credentials_file=credentials_path,
                                         print_output=False,
                                         user_agent=spotinst_user_agent)

    group_id, message, has_changed = handle_elastigroup(
        client=client, module=module)

    instances = retrieve_group_instances(
        client=client, module=module, group_id=group_id)

    module.exit_json(
        changed=has_changed,
        group_id=group_id,
        message=message,
        instances=instances)


if __name__ == '__main__':
    main()
