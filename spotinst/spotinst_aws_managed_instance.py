#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: spotinst_aws_managed_instance
version_added: 2.5
short_description: Create, update or delete Spot AWS Managed Instances
author: Spot
description: >
    Create, update, delete or perform actions (pause, resume, recyce) on Spot AWS Managed Instances.
    You will have to have a credentials file in this location - <home>/.spotinst/credentials
    The credentials file must contain a row that looks like this
    token = <YOUR TOKEN>
    Full documentation available at [our docs site](https://docs.spot.io/)
requirements:
    - python >= 3.6
    - spotinst_sdk2 >= 2.0.0
options:
    token:
        type: str
        description:
            - Optional parameter that allows to set an token inside the module configuration. By default this is retrieved from the credentials path

    credentials_path:
        type: str
        default: "/root/.spotinst/credentials"
        description:
          - Optional parameter that allows to set a non-default credentials path.

    state:
        type: str
        choices:
            - present
            - absent
        default: present
        description:
            - create update or delete

    account_id:
        type: str
        description:
            - Optional parameter that allows to set an account-id inside the module configuration. By default this is retrieved from the credentials path

    id:
        type: str
        description:
            - The managed instance ID if it already exists and you want to update or delete it.
            - This will have no effect unless the `uniqueness_by` field is set to ID.
            - When this is set, and the `uniqueness_by` field is set, the group will either be updated or deleted, but not created.

    uniqueness_by:
        type: str
        choices:
            - id
            - name
        description:
            - If your managed instance names are not unique, you may use this feature to update or delete a specific group.
            - Whenever this property is set, you must set a an `id` in order to update or delete a group, otherwise a group will be created.


    do_not_update:
        type: list
        description:
            - A list of dotted paths to attributes that you don't wish to update during an update operation.
            - Example: Specifying `compute.product` will make sure that this attribute is never updated.

    action:
        type: str
        choices:
            - pause
            - resume
            - recycle
        description: 
            - Perform the desired action on the managed instance. This has no effect on delete operations.
   
    managed_instance_config:
        type: dict
        description: various configurations related to the managed instance
        suboptions:
            deletion_config:
                type: dict
                description: configurations related to the deletion of the managed instance
                suboptions:
                deallocation_config:
                    type: dict
                    suboptions:
                        deallocate_network_interfaces:
                          type: bool
                          description: 
                            - Whether to deallocate the MI's network interfaces upon deletion
                        deallocate_volumes:
                          type: bool
                          description: 
                            - Whether to deallocate the MI's volumes upon deletion
                        deallocate_snapshots:
                          type: bool
                          description: 
                            - Whether to deallocate the MI's snapshots upon deletion
                        deallocate_amis:
                          type: bool
                          description: 
                            - Whether to deallocate the AMIs upon deletion
                        should_terminate_instance:
                          type: bool
                          description: 
                            - Choose whether to detach the MI without terminating it on AWS side.
                  
                ami_backup:
                    type: dict
                    suboptions:
                        should_delete_images:
                            type: bool
                            description: 
                                - Mark if images collected during AMI Auto Backup should be deleted during instance deletion.
                    
    managed_instance:
        type: dict
        description: describe the desired properties of the managed instance under this object.
        suboptions:
            name:
                type: str
                description: 
                    - The managed instance's name.
            region:
                type: str
                description: 
                    - The AWS region for the managed instance.
            description:
                type: str
                description: 
                    - optional description for the managed instance.
            persistence:
                type: dict
                suboptions:
            health_check:
                type: dict
                suboptions:
                    type:
                        type: str
                        description: 
                            - The health check type.
                    auto_healing:
                        type: bool
                        description: 
                            - Auto healing replaces the instance automatically in case the health check fails
                    grace_period:
                        type: int
                        description: 
                            - Number of seconds to wait after the instance had launched before starting health checks.
                    unhealthy_duration:
                        type: int
                        description: 
                            - Number of seconds to keep the instance active it had become unhealthy.        
            scheduling:
                type: dict
                description: Scheduling options for the managed instance
                suboptions:
                    tasks:
                        description: 
                            - A list of task objects to perform
                        type: list
                        elements: dict
                        suboptions:
                            task_type:
                                type: str
                                description: 
                                    - The task type to run
                            start_time:
                                type: str
                                description: 
                                    - `DATETIME` in `ISO-8601` format. Sets a start time for scheduled actions. If frequency or cronExpression are not used - the task will run only once at the start time and will then be deleted from the group configuration
                            cron_expression:
                                type: str
                                description:
                                    - A valid cron expression. For example : ` * * * * * `. The cron is running in UTC time zone and is in Unix cron format Cron Expression Validator Script. Only one of ‘frequency' or ‘cronExpression' should be used at a time.
                            is_enabled:
                                type: bool
                                description:
                                    - Describes whether the task is enabled. When true the task should run when false it should not run.
                            frequency:
                                type: str
                                description:
                                    - The recurrence frequency to run this task. Only one of `frequency` or `cronExpression` should be used at a time
            strategy:
                type: dict
                suboptions:
                    life_cycle: 
                        type: str
                        description: 
                            - Set lifecycle, valid values: `spot`, `on_demand`
                    orientation:
                        type: str
                        description:
                            - The strategy orientation. valid values: `costOriented`, `availabilityOriented`, `balanced`, `cheapest`.
                    draining_timeout:
                        type: int
                        description:
                            - The time in seconds to allow the instance be drained from incoming TCP connections and detached from ELB before terminating it during a scale down operation
                    fallback_to_od:
                        type: bool
                        description:
                            - In case of no spots available, Managed Instance will launch an On-demand instance instead Default: true
                    utilize_reserved_instances:
                        type: bool
                        description: 
                            - In case of any available Reserved Instances, Managed Instance will utilize them before purchasing Spot instances.
                    utilize_commitments:
                        type: bool
                        description: 
                            - In case of any available commitments, Managed Instance will utilize them before purchasing Spot instances.
                    optimization_windows:
                        type: list
                        elements: str
                        description:
                            - When performAt is 'timeWindow': must specify a list of 'timeWindows' with at least one time window Each string is in the format of - `ddd:hh:mm-ddd:hh:mm ddd` = day of week = Sun | Mon | Tue | Wed | Thu | Fri | Sat hh = hour 24 = 0 -23 mm = minute = 0 - 59
                    minimum_instance_lifetime:
                        type: int
                        description:
                            - Defines the preferred minimum instance lifetime in hours. Markets which comply with this preference will be prioritized. Optional values: 1, 3, 6, 12, 24.
                    revert_to_spot:
                        type: dict
                        suboptions:
                            perform_at:
                                type: str
                                description:
                                    - Valid values: `always`, `never`, `timeWindow`
            compute:
                type: dict
                description: Managed Instance compute object
                suboptions:
                    subnet_ids:
                        type: list
                        elements: str
                        description: 
                            - A list of subnet identifiers for your instance.
                    vpc_id:
                        type: str
                        description:
                            - VPC ID for the managed instance.
                    elastic_ip:
                        type: str
                        description:
                            - Elastic IP Allocation ID to associate to the instance
                    private_ip:
                        type: str
                        description:
                            - Private IP Allocation ID to associate to the instance
                    product:
                        type: str
                        description:
                            - Operation system type. 
                            - Possible values: `Linux/UNIX`, `SUSE Linux`, `Windows`, `Red Hat Enterprise Linux` 
                            - In case of EC2 classic: Linux/UNIX (Amazon VPC), SUSE Linux (Amazon VPC), Windows (Amazon VPC), Red Hat Enterprise Linux (Amazon VPC)
                    launch_specification:
                        type: dict
                        description: 
                            - launch specification object
                        suboptions:
                            instance_types:
                                type: dict
                                suboptions:
                                    preferred_type:
                                        type: str
                                        description:
                                            - The preferred instance type
                                    types: 
                                        type: list
                                        elements: str
                                        description: 
                                            - Comma separated list of available instance types for instance
                            ebs_optimized:
                                type: bool
                                description:
                                    - Enable EBS optimization for supported instance which is not enabled by default. Note - additional charges will be applied. Default: false
                            monitoring:
                                type: bool
                                description:
                                    - Describes whether instance Enhanced Monitoring is enabled. Default: false
                            tenancy:
                                type: str
                                description:
                                    - 'Valid values: "default", "dedicated" Default: default'
                            iam_role:
                                type: dict
                                suboptions:
                                    name:
                                        type: str
                                    arn:
                                        type: str
                            security_group_ids:
                                type: list
                                elements: str
                                description:
                                    - The security-group IDs for the managed instance
                            image_id:
                                type: str
                                description:
                                    - The AMI for the managed instance
                            key_pair:
                                type: str
                                description:
                                    - The SSH key-pair for access to the managed instance
                            tags:
                                type: list
                                elements: dict
                                suboptions:
                                    tag_key: 
                                        type: str
                                    tag_value:
                                        type: str
                            resource_tag_specification:
                                type: dict
                                description:
                                    - Which resources should be tagged with group tags.
                                suboptions:
                                    volumes:
                                        type: dict
                                        suboptions:
                                            should_tag:
                                                type: bool
                                    snapshots:
                                        type: dict
                                        suboptions:
                                            should_tag:
                                                type: bool
                                    enis:
                                        type: dict
                                        suboptions:
                                            should_tag:
                                                type: bool
                                    amis:
                                        type: dict
                                        suboptions:
                                            should_tag:
                                                type: bool
                            user_data:
                                type: str
                            shutdown_script:
                                type: str
                            credit_specification:
                                type: dict
                                description:
                                    - a creditSpecification object
                                suboptions:
                                    cpu_credits:
                                        type: str
                            network_interfaces:
                                description: 
                                    - List of network interfaces in an EC2 instance. 
                                type: list
                                elements: dict
                                suboptions:
                                    device_index:
                                        type: int
                                    associate_ipv6_address:
                                        type: bool
                                        description:
                                            - Indicates whether to assign an IPv6 address. 
                                            - Amazon EC2 chooses the IPv6 addresses from the subnet's range.
                                    associate_public_ip_address:
                                        type: bool
                                        description:
                                            - Indicates whether to assign a public IPv4 address to an instance you launch in a VPC. 
                                            - The public IP address can only be assigned to a network interface for `eth0`
                                            - Can only be assigned to a new network interface, not an existing one. 
                                            - You cannot specify more than one network interface in the request. 
                                            - If launching into a default subnet, the default value is true.
                            block_device_mappings:
                                type: list
                                elements: dict
                                suboptions:
                                    device_name:
                                        type: str
                                    no_device: 
                                        type: str
                                    virtual_name:
                                        type: str
                                    ebs:
                                        type: dict
                                        suboptions:
                                            delete_on_termination:
                                                type: bool
                                            encrypted:
                                                type: bool
                                            iops:
                                                type: int
                                            throughput:
                                                type: float
                                            volume_size:
                                                type: int
                                            volume_type:
                                                type: str
                                            kms_key_id:
                                                type: str
                                            snapshot_id:
                                                type: str
            integrations:
                type: dict
                suboptions:
                    route53:
                        type: dict
                        suboptions:
                            domains:
                                type: list
                                elements: dict
                                suboptions:
                                    hosted_zone_id:
                                        type: str
                                    spotinst_account_id:
                                        type: str
                                    record_set_type:
                                        type: str
                                    record_sets:
                                        type: list
                                        elements: dict
                                        suboptions:
                                            name:
                                                type: str
                                            use_public_ip:
                                                type: bool
                                            use_public_dns:
                                                type: bool
                    load_balancers_config:
                        type: dict
                        suboptions:
                            load_balancers:
                                type: list
                                elements: dict
                                suboptions:
                                    name:
                                        type: str
                                    arn:
                                        type: str
                                    type:
                                        type: str
                                    balancer_id:
                                        type: str
                                    target_set_id:
                                        type: str
                                    az_awareness:
                                        type: bool
                                    auto_weight:
                                        type: bool
"""

# TODO shibel: adjust the namespace here once we publish to Galaxy.
EXAMPLES = """
# Basic Example
- hosts: localhost
  tasks:
    - name: managed instance
      spotinst_aws_managed_instance:
        state: present
        do_not_update:
          - compute.product
        managed_instance:
          name: ansible-managed-instance-example
          description: a nice Managed Instance created via Ansible
          region: us-west-2
          persistence:
            persist_block_devices: true
            persist_root_device: true
            block_devices_mode: "onLaunch"
          strategy:
            life_cycle: "spot"
            revert_to_spot:
              perform_at: "always"
          health_check:
            type: "EC2"
            grace_period: 120
            unhealthy_duration: 120
          compute:
            product: "Linux/UNIX"
            launch_specification:
              image_id: "ami-082b5a644766e0e6f"
              instance_types:
                types: [ "t2.micro", "t3.small", "t3.micro" ]
                preferred_type: "t2.micro"
              key_pair: "shibel-core-oregon"
              security_group_ids:
                - "sg-XXXXXX"
            subnet_ids:
              - "subnet-XXXXX"
            vpc_id: "vpc-XXXX"
          scheduling:
            tasks:
              - is_enabled: true
                frequency: "weekly"
                start_time: "2050-22-22T00:00:00Z"
                task_type: "pause"
          integrations:
            route53:
              domains:
                - hosted_zone_id: "1"
                  spotinst_account_id: "act-xxx"
                  record_set_type: "a"
                  record_sets:
                    - name: "some_name"
                      use_public_ip: true
            load_balancers_config:
              load_balancers:
                - name: "some_lb"
                  arn: "arn:aws:elasticloadbalancing:us-east-2:123456789012:loadbalancer/app/my-load-balancer/1234567890123456"
                  type: "CLASSIC"
      register: result
    - debug: var=result
"""

RETURN = """
---
managed_instance_id: 
    description: The ID of the managed instance that was just created/update/deleted.
    returned: success
    type: str
    sample: smi-a20bbc74
"""

HAS_SPOTINST_SDK = False
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
import copy

try:
    import spotinst_sdk2 as spotinst
    from spotinst_sdk2 import SpotinstSession
    from spotinst_sdk2.client import SpotinstClientException

    HAS_SPOTINST_SDK = True

except ImportError as e:
    raise e

CLS_NAME_BY_ATTR_NAME = {
    "managed_instance.integrations.load_balancers_config": "LoadBalancersConfiguration",
    "managed_instance.integrations.route53": "Route53Configuration",
    "managed_instance.integrations": "IntegrationsConfig"
}

LIST_MEMBER_CLS_NAME_BY_ATTR_NAME = {
    "managed_instance.integrations.route53.domains.record_sets": "Route53RecordSetConfiguration",
    "managed_instance.integrations.route53.domains": "Route53DomainConfiguration",
    "managed_instance.scheduling.tasks": "Task",
    "managed_instance.integrations.load_balancers_config.load_balancers": "LoadBalancer"
}


class SpotAnsibleModule(AnsibleModule):

    def __init__(self, argument_spec, bypass_checks=False, no_log=False, mutually_exclusive=None,
                 required_together=None, required_one_of=None, add_file_common_args=False, supports_check_mode=False,
                 required_if=None, required_by=None):
        """
        Common code for quickly building an ansible module in Python
        (although you can write modules with anything that can return JSON).

        See :ref:`developing_modules_general` for a general introduction
        and :ref:`developing_program_flow_modules` for more detailed explanation.
        """

        self.argument_spec = argument_spec

        self._load_params()
        self._set_internal_properties()
        self.custom_params = self.params
        super().__init__(argument_spec, bypass_checks, no_log, mutually_exclusive, required_together, required_one_of,
                         add_file_common_args, supports_check_mode, required_if, required_by)


def to_snake_case(camel_str):
    import re
    ret_val = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

    return ret_val


def to_pascal_case(snake_str):
    return "".join(word.title() for word in snake_str.split("_"))


def is_primitive(some_obj):
    return any(isinstance(some_obj, x) for x in [bool, float, int, str])


def find_in_overrides(curr_path):
    return CLS_NAME_BY_ATTR_NAME.get(curr_path, None) or LIST_MEMBER_CLS_NAME_BY_ATTR_NAME.get(curr_path, None)


def get_client(module):
    creds_file_loaded_vars = dict()

    credentials_path = module.custom_params.get("credentials_path")

    if credentials_path is not None:
        try:
            with open(credentials_path, "r") as creds:
                for line in creds:
                    eq_index = line.find(":")
                    var_name = line[:eq_index].strip()
                    string_value = line[eq_index + 1:].strip()
                    creds_file_loaded_vars[var_name] = string_value
        except IOError:
            pass
    # End of creds file retrieval

    token = module.custom_params.get("token")
    if not token:
        token = creds_file_loaded_vars.get("token")

    account = module.custom_params.get("account_id")

    if not account:
        account = creds_file_loaded_vars.get("account")

    if account is not None:
        session = spotinst.SpotinstSession(auth_token=token, account_id=account)
    else:
        session = spotinst.SpotinstSession(auth_token=token)

    client = session.client("managed_instance_aws")

    return client


def turn_to_model(content, field_name: str, curr_path=None):
    if content is None:
        return None
    elif is_primitive(content):
        return content
    elif isinstance(content, list):
        new_l = []

        for item in content:
            value = turn_to_model(item, field_name, curr_path)
            new_l.append(value)

        return new_l

    elif isinstance(content, dict):
        if curr_path is not None:
            curr_path += "." + field_name
        else:
            curr_path = field_name

        override = find_in_overrides(curr_path)
        key_to_use = override if override else to_pascal_case(field_name)

        class_ = getattr(spotinst.models.managed_instance.aws, key_to_use)
        instance = class_()

        for key, value in content.items():
            new_value = turn_to_model(value, key, curr_path)
            setattr(instance, key, new_value)

        return instance


def find_mis_with_same_name(managed_instances, name):
    ret_val = []
    for mi in managed_instances:
        if mi["config"]["name"] == name:
            ret_val.append(mi)

    return ret_val


def clean_do_not_update_fields(
        managed_instance_module_copy: dict, do_not_update_list: list
):
    ret_val = managed_instance_module_copy

    # avoid deleting parent dicts before children
    do_not_update_list = sorted(do_not_update_list, key=lambda x: len(x), reverse=True)

    for dotted_path in do_not_update_list:
        curr_dict = managed_instance_module_copy
        path_as_list = dotted_path.split(".")
        last_part_of_path = path_as_list[-1]

        for path_part in path_as_list[:-1]:
            new_dict = curr_dict.get(path_part)
            curr_dict = new_dict

        if curr_dict.get(last_part_of_path) is not None:
            del curr_dict[last_part_of_path]

    return ret_val


def get_id_and_operation(client, state: str, module: SpotAnsibleModule):
    operation, id = None, None
    uniqueness_by = module.custom_params.get("uniqueness_by")
    manually_provided_mi_id = module.custom_params.get("id")
    managed_instance = module.custom_params.get("managed_instance")

    if state == "present":

        if uniqueness_by == "id":
            if manually_provided_mi_id is None:
                operation = "create"
            else:
                id = manually_provided_mi_id
                operation = "update"
        else:
            all_managed_instances = client.get_managed_instances()
            name = managed_instance["name"]
            instances_with_name = find_mis_with_same_name(all_managed_instances, name)

            if len(instances_with_name) == 0:
                operation = "create"
            elif len(instances_with_name) == 1:
                id = instances_with_name[0]["id"]
                operation = "update"
            else:
                msg = f"Failed updating managed instance - 'uniqueness_by' is set to 'name' but there's more than one managed instance with the name '{name}'"
                module.fail_json(changed=False, msg=msg)

    elif state == "absent":
        operation = "delete"

        if uniqueness_by == "id":
            if manually_provided_mi_id is not None:
                id = module.custom_params.get("id")
            else:
                msg = f"Failed deleting managed instance - 'uniqueness_by' is set to `id` but parameter 'id' was not provided"
                module.fail_json(changed=False, msg=msg)
        else:
            all_managed_instances = client.get_managed_instances()
            name = managed_instance["name"]
            instances_with_name = find_mis_with_same_name(all_managed_instances, name)

            if len(instances_with_name) == 1:
                id = instances_with_name[0]["id"]
            if len(instances_with_name) > 1:
                msg = f"Failed deleting managed instance - 'uniqueness_by' is set to 'name' but there's more than one managed instance with the name '{name}'"
                module.fail_json(changed=False, msg=msg)
            if len(instances_with_name) == 0:
                msg = f"Failed deleting managed instance - 'uniqueness_by' is set to 'name' but there is no managed instance with the name '{name}'"
                module.fail_json(changed=False, msg=msg)

    else:
        msg = f"Spot Ansible Module error: got unknown state {state}"
        module.fail_json(changed=False, msg=msg)
    return operation, id


def handle_managed_instance(client, module):
    mi_models = spotinst.models.managed_instance.aws
    managed_instance_module_copy = copy.deepcopy(module.custom_params.get("managed_instance"))
    state = module.custom_params.get("state")

    operation, mi_id = get_id_and_operation(client, state, module)

    if operation == "create":
        has_changed, managed_instance_id, message = handle_create_managed_instance(client, managed_instance_module_copy)
    elif operation == "update":
        has_changed, managed_instance_id, message = handle_update_managed_instance(client, managed_instance_module_copy,
                                                                                   mi_id, module)
    elif operation == "delete":
        has_changed, managed_instance_id, message = handle_delete_managed_instance(client, mi_id, mi_models, module)
    else:
        module.fail_json(changed=False, msg=f"Unknown operation {operation} - "
                                            f"this is probably a bug in the module's code: please report")
        return None, None, None  # for IDE - fail_json stops execution

    return managed_instance_id, message, has_changed


def handle_delete_managed_instance(client, mi_id, mi_models, module):
    managed_instance_id = mi_id
    delete_args = dict(managed_instance_id=managed_instance_id)

    handle_deletion_config(delete_args, mi_models, module)

    try:
        client.delete_managed_instance(**delete_args)
        message = f"Managed instance {mi_id} deleted successfully"
        has_changed = True
    except SpotinstClientException as exc:
        if "MANAGED_INSTANCE_DOES_NOT_EXIST" in exc.message:
            message = f"Failed deleting managed instance - managed instance with ID {mi_id} doesn't exist"
            module.fail_json(changed=False, msg=message)
        else:
            message = f"Failed deleting managed instance (ID: {mi_id}), error: {exc.message}"
            module.fail_json(msg=message)
        has_changed = False

    return has_changed, managed_instance_id, message


def handle_update_managed_instance(client, managed_instance_module_copy, mi_id, module):
    managed_instance_module_copy = clean_do_not_update_fields(
        managed_instance_module_copy,
        module.custom_params.get("do_not_update")
    )
    ami_sdk_object = turn_to_model(managed_instance_module_copy, "managed_instance")

    try:
        res: dict = client.update_managed_instance(mi_id, managed_instance_update=ami_sdk_object)
        managed_instance_id = res["id"]
        message = "Managed instance updated successfully"
        has_changed = True

        action_type = module.custom_params.get("action", None)
        should_perform_action = action_type is not None

        if should_perform_action:
            message = attempt_mi_action(
                action_type, client, managed_instance_id, message
            )

    except SpotinstClientException as exc:
        if "MANAGED_INSTANCE_DOES_NOT_EXIST" in exc.message:
            message = f"Failed updating managed instance - managed instance  with ID {mi_id} doesn't exist"
            module.fail_json(changed=False, msg=message)
        else:
            message = f"Failed updating managed instance (ID {mi_id}), error: {exc.message}"
            module.fail_json(msg=message)
        has_changed = False

    return has_changed, mi_id, message


def handle_create_managed_instance(client, managed_instance_module_copy):
    ami_sdk_object = turn_to_model(
        managed_instance_module_copy, "managed_instance"
    )
    res: dict = client.create_managed_instance(managed_instance=ami_sdk_object)
    managed_instance_id = res["id"]
    message = "Managed instance created successfully"
    has_changed = True
    return has_changed, managed_instance_id, message


def handle_deletion_config(delete_args, mi_models, module):
    mi_config = module.custom_params.get("managed_instance_config")

    if mi_config is not None:
        deletion_config = mi_config.get("deletion_config")

        if deletion_config is not None:
            deallocation_config = deletion_config.get("deallocation_config")
            ami_backup = deletion_config.get("ami_backup")

            if deallocation_config is not None:
                dealloc_sdk_object = turn_to_model(deallocation_config, mi_models.DeallocationConfig())
                delete_args["deallocation_config"] = dealloc_sdk_object

            if ami_backup is not None:
                ami_sdk_object = turn_to_model(ami_backup, mi_models.AmiBackup())
                delete_args["ami_backup"] = ami_sdk_object


def attempt_mi_action(action_type, client, managed_instance_id, message):
    try:
        if action_type == "pause":
            client.pause_managed_instance(managed_instance_id)
        if action_type == "resume":
            client.resume_managed_instance(managed_instance_id)
        if action_type == "recycle":
            client.recycle_managed_instance(managed_instance_id)

        message = message + f" and action '{action_type}' started"
    except SpotinstClientException as exc:
        message = (
                message + f" but action '{action_type}' failed, error: {exc.message}"
        )
    return message


def main():
    task_fields = dict(
        task_type=dict(type="str"),
        start_time=dict(type="str"),
        cron_expression=dict(type="str"),
        is_enabled=dict(type="bool"),
        frequency=dict(type="str"),
    )

    scheduling_fields = dict(
        tasks=dict(type="list", elements="dict", options=task_fields)
    )

    health_check_fields = dict(
        type=dict(type="str"),
        auto_healing=dict(type="bool"),
        grace_period=dict(type="int"),
        unhealthy_duration=dict(type="int"),
    )

    persistence_fields = dict(
        persist_root_device=dict(type="bool"),
        persist_block_devices=dict(type="bool"),
        persist_private_ip=dict(type="bool"),
        block_devices_mode=dict(type="str"),
    )

    revert_to_spot_fields = dict(perform_at=dict(type="str"))

    strategy_fields = dict(
        life_cycle=dict(type="str"),
        orientation=dict(type="str"),
        draining_timeout=dict(type="int"),
        fallback_to_od=dict(type="bool"),
        utilize_reserved_instances=dict(type="bool"),
        utilize_commitments=dict(type="bool"),
        optimization_windows=dict(type="list", elements="str"),
        minimum_instance_lifetime=dict(type="int"),
        revert_to_spot=dict(type="dict", options=revert_to_spot_fields),
    )

    instance_types_fields = dict(
        preferred_type=dict(type="str"), types=dict(type="list", elements="str")
    )

    iam_role_fields = dict(name=dict(type="str"), arn=dict(type="str"))

    tags_fields = dict(tag_key=dict(type="str"), tag_value=dict(type="str"))

    tag_spec_fields = dict(should_tag=dict(type="bool"))

    resource_ts_fields = dict(
        volumes=dict(type="dict", options=tag_spec_fields),
        snapshots=dict(type="dict", options=tag_spec_fields),
        enis=dict(type="dict", options=tag_spec_fields),
        amis=dict(type="dict", options=tag_spec_fields),
    )

    credit_specification_fields = dict(cpu_credits=dict(type="str"))

    network_interfaces_fields = dict(
        device_index=dict(type="int"),
        associate_ipv6_address=dict(type="bool"),
        associate_public_ip_address=dict(type="bool"),
    )

    ebs_fields = dict(
        delete_on_termination=dict(type="bool"),
        encrypted=dict(type="bool"),
        iops=dict(type="int"),
        throughput=dict(type="float"),
        volume_size=dict(type="int"),
        volume_type=dict(type="str"),
        kms_key_id=dict(type="str"),
        snapshot_id=dict(type="str"),
    )

    block_device_mappings_fields = dict(
        device_name=dict(type="str"),
        no_device=dict(type="str"),
        virtual_name=dict(type="str"),
        ebs=dict(type="dict", options=ebs_fields),
    )

    launch_spec_fields = dict(
        instance_types=dict(type="dict", options=instance_types_fields),
        ebs_optimized=dict(type="bool"),
        monitoring=dict(type="bool"),
        tenancy=dict(type="str"),
        iam_role=dict(type="dict", options=iam_role_fields),
        security_group_ids=dict(type="list", elements="str"),
        image_id=dict(type="str"),
        key_pair=dict(type="str"),
        tags=dict(type="list", elements="dict", options=tags_fields),
        resource_tag_specification=dict(type="dict", options=resource_ts_fields),
        user_data=dict(type="str"),
        shutdown_script=dict(type="str"),
        credit_specification=dict(type="dict", options=credit_specification_fields),
        network_interfaces=dict(
            type="list", elements="dict", options=network_interfaces_fields
        ),
        block_device_mappings=dict(
            type="list", elements="dict", options=block_device_mappings_fields
        ),
    )

    compute_fields = dict(
        subnet_ids=dict(type="list", elements="str"),
        vpc_id=dict(type="str"),
        elastic_ip=dict(type="str"),
        private_ip=dict(type="str"),
        product=dict(type="str"),
        launch_specification=dict(type="dict", options=launch_spec_fields),
    )

    route53_record_sets_fields = dict(
        name=dict(type="str"),
        use_public_ip=dict(type="bool"),
        use_public_dns=dict(type="bool"),
    )

    route53_domains_fields = dict(
        hosted_zone_id=dict(type="str"),
        spotinst_account_id=dict(type="str"),
        record_set_type=dict(type="str"),
        record_sets=dict(
            type="list", elements="dict", options=route53_record_sets_fields
        ),
    )

    route53_fields = dict(
        domains=dict(type="list", elements="dict", options=route53_domains_fields)
    )

    load_balancers_fields = dict(
        name=dict(type="str"),
        arn=dict(type="str"),
        type=dict(type="str"),
        balancer_id=dict(type="str"),
        target_set_id=dict(type="str"),
        az_awareness=dict(type="bool"),
        auto_weight=dict(type="bool"),
    )

    load_balancers_config_fields = dict(
        load_balancers=dict(type="list", elements="dict", options=load_balancers_fields)
    )

    integrations_fields = dict(
        route53=dict(type="dict", options=route53_fields),
        load_balancers_config=dict(type="dict", options=load_balancers_config_fields),
    )

    actual_fields = dict(
        name=dict(type="str", required=True),
        region=dict(type="str", required=True),
        description=dict(type="str"),
        persistence=dict(type="dict", options=persistence_fields),
        health_check=dict(type="dict", options=health_check_fields),
        scheduling=dict(type="dict", options=scheduling_fields),
        strategy=dict(type="dict", options=strategy_fields),
        compute=dict(type="dict", options=compute_fields),
        integrations=dict(type="dict", options=integrations_fields),
    )

    deallocation_config_fields = dict(
        deallocate_network_interfaces=dict(type="bool"),
        deallocate_volumes=dict(type="bool"),
        deallocate_snapshots=dict(type="bool"),
        deallocate_amis=dict(type="bool"),
        should_terminate_instance=dict(type="bool"),
    )

    ami_backup_fields = dict(should_delete_images=dict(type="bool"))

    deletion_config_fields = dict(
        ami_backup=dict(type="dict", options=ami_backup_fields),
        deallocation_config=dict(type="dict", options=deallocation_config_fields)
    )

    managed_instance_config_fields = dict(
        deletion_config=dict(type="dict", options=deletion_config_fields)
    )

    fields = dict(
        # region config fields
        token=dict(
            type="str", fallback=(env_fallback, ["SPOTINST_TOKEN"]), no_log=True
        ),
        credentials_path=dict(type="path", default="~/.spotinst/credentials"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        account_id=dict(
            type="str", fallback=(env_fallback, ["SPOTINST_ACCOUNT_ID", "ACCOUNT"])
        ),
        id=dict(type="str"),
        uniqueness_by=dict(type="str", choices=["id", "name"], default="name"),
        do_not_update=dict(type="list", elements="str"),
        # endregion
        # region mi-specific config fields
        action=dict(type="str", choices=["pause", "resume", "recycle"]),
        managed_instance_config=dict(type="dict", options=managed_instance_config_fields),
        # endregion
        # region managed_instance
        managed_instance=dict(type="dict", required=True, options=actual_fields)
        # endregion
    )

    module = SpotAnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(
            msg="the Spotinst SDK library is required. (pip install spotinst-sdk2)"
        )

    client = get_client(module=module)

    managed_instance_id, message, has_changed = handle_managed_instance(
        client=client, module=module
    )

    module.exit_json(
        changed=has_changed, managed_instance_id=managed_instance_id, message=message
    )


if __name__ == "__main__":
    main()
