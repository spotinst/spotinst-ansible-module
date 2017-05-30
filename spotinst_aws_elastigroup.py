#!/usr/bin/python
from os.path import expanduser

import spotinst
from ansible.module_utils.basic import AnsibleModule


def create_autoscaling_group(client, module):
    eg = spotinst.aws_elastigroup.Elastigroup()

    name = module.params.get('name')
    description = module.params.get('description')

    if name is not None:
        eg.name = name

    if description is not None:
        eg.description = description

    # Capacity
    expand_capacity(eg, module)

    # Strategy
    expand_strategy(eg, module)

    # Scaling
    expand_scaling(eg, module)

    # Third party integrations
    expand_integrations(eg, module)

    # Compute
    expand_compute(eg, module)

    # TODO : MULTAI & SCHEDULING
    # # Multai
    # multai_token = module.params.get('multai_token')
    # multai_load_balancers = module.params.get('multai_load_balancers')
    #
    # # Scheduling
    # scheduled_tasks = module.params.get('scheduled_tasks'

    client.create_elastigroup(group=eg)


def expand_compute(eg, module):
    elastic_ips = module.params['elastic_ips']
    on_demand_instance_type = module.params.get('on_demand_instance_type')
    spot_instance_types = module.params['spot_instance_types']
    ebs_volume_pool = module.params['ebs_volume_pool']
    availability_zones = module.params['availability_zones']
    product = module.params.get('product')

    eg_compute = spotinst.aws_elastigroup.Compute()

    if product is not None:
        eg_compute.product = product

    if elastic_ips is not None:
        eg_compute.elastic_ips = elastic_ips

    if on_demand_instance_type or spot_instance_types is not None:
        eg_instance_types = spotinst.aws_elastigroup.InstanceTypes()

        if on_demand_instance_type is not None:
            eg_instance_types.spot = spot_instance_types
        if spot_instance_types is not None:
            eg_instance_types.ondemand = on_demand_instance_type

        if eg_instance_types.spot is not None or eg_instance_types.ondemand is not None:
            eg_compute.instanceTypes = eg_instance_types

    expand_ebs_volume_pool(eg_compute, ebs_volume_pool)

    expand_availability_zones(eg_compute, availability_zones)

    expand_launch_spec(eg_compute, module)

    eg.compute = eg_compute


def expand_availability_zones(eg_compute, az_list):
    if az_list is not None:
        eg_azs = []

        for az in az_list:
            eg_az = spotinst.aws_elastigroup.AvailabilityZone()
            if az.get('name') is not None:
                eg_az.name = az.get('name')
            if az.get('subnetId') is not None:
                eg_az.subnetId = az.get('subnetId')
            if az.get('placement_group_name') is not None:
                eg_az.placementGroupName = az.get('placement_group_name')

            if eg_az.name is not None:
                eg_azs.append(eg_az)

        if eg_azs.__sizeof__() > 0:
            eg_compute.availabilityZones = eg_azs


def expand_ebs_volume_pool(eg_compute, ebs_volumes_list):
    if ebs_volumes_list is not None:
        eg_volumes = []

        for volume in ebs_volumes_list:
            eg_volume = spotinst.aws_elastigroup.EbsVolume()

            if volume.get('deviceName') is not None:
                eg_volume.deviceName = volume.get('deviceName')
            if volume.get('volumeIds') is not None:
                eg_volume.volumeIds = volume.get('volumeIds')

            if eg_volume.deviceName is not None:
                eg_volumes.append(eg_volume)

        if eg_volumes.__sizeof__() > 0:
            eg_compute.ebsVolumePool = eg_volumes


def expand_launch_spec(eg_compute, module):
    user_data = module.params.get('user_data')
    key_pair = module.params.get('key_pair')
    i_am_role = module.params.get('i_am_role')
    tenancy = module.params.get('tenancy')
    shut_down_script = module.params.get('shut_down_script')
    monitoring = module.params.get('monitoring')
    ebs_optimized = module.params.get('ebs_optimized')
    image_id = module.params.get('image_id')
    health_check_type = module.params.get('health_check_type')
    health_check_grace_period = module.params.get('health_check_grace_period')
    health_check_unhealthy_duration_before_replacement = module.params.get(
        'health_check_unhealthy_duration_before_replacement')
    security_group_ids = module.params['security_group_ids']
    tags = module.params['tags']

    # TODO : LOAD_BALANCERS, TARGET_GROUPS, BLOCK_DEVICE_MAPPINGS, NETWORK_INTERFACES
    load_balancers = module.params['load_balancers']
    target_group_arns = module.params['target_group_arns']
    block_device_mappings = module.params['block_device_mappings']
    network_interfaces = module.params['network_interfaces']

    eg_launch_spec = spotinst.aws_elastigroup.LaunchSpecification()

    if user_data is not None:
        eg_launch_spec.userData = user_data

    if monitoring is not None:
        eg_launch_spec.monitoring = monitoring

    if ebs_optimized is not None:
        eg_launch_spec.ebsOptimized = ebs_optimized

    if tenancy is not None:
        eg_launch_spec.tenancy = tenancy

    if shut_down_script is not None:
        eg_launch_spec.shutdownScript = shut_down_script

    if ebs_optimized is not None:
        eg_launch_spec.ebsOptimized = ebs_optimized

    if i_am_role is not None:
        eg_launch_spec.iamRole = i_am_role

    if key_pair is not None:
        eg_launch_spec.keyPair = key_pair

    if image_id is not None:
        eg_launch_spec.imageId = image_id

    if health_check_type is not None:
        eg_launch_spec.healthCheckType = health_check_type

    if health_check_grace_period is not None:
        eg_launch_spec.healthCheckGracePeriod = health_check_grace_period

    if health_check_unhealthy_duration_before_replacement is not None:
        eg_launch_spec.healthCheckUnhealthyDurationBeforeReplacement = health_check_unhealthy_duration_before_replacement

    if security_group_ids is not None:
        eg_launch_spec.securityGroupIds = security_group_ids

    expand_tags(eg_launch_spec, tags)

    eg_compute.launchSpecification = eg_launch_spec


def expand_integrations(eg, module):
    rancher = module.params.get('rancher')
    mesosphere = module.params.get('mesosphere')
    elastic_beanstalk = module.params.get('elastic_beanstalk')
    ecs = module.params.get('ecs')
    kubernetes = module.params.get('kubernetes')
    rightscale = module.params.get('rightscale')
    opsworks = module.params.get('opsworks')
    chef = module.params.get('chef')
    eg_integrations = spotinst.aws_elastigroup.ThirdPartyIntegrations()
    if rancher:
        eg_rancher = spotinst.aws_elastigroup.Rancher(accessKey=rancher.get('access_key'),
                                                      secretKey=rancher.get('secret_key'),
                                                      masterHost=rancher.get('master_host'))
        eg_integrations.rancher = eg_rancher

    if chef:
        eg_chef = spotinst.aws_elastigroup.ChefConfiguration(chefServer=chef.get('chef_server'),
                                                             organization=chef.get('organization'),
                                                             user=chef.get('user'),
                                                             pemKey=chef.get('pem_key'),
                                                             chefVersion=chef.get('chef_version'))
        eg_integrations.chef = eg_chef

    if mesosphere:
        eg_mesosphere = spotinst.aws_elastigroup.Mesosphere(apiServer=mesosphere.get('api_server'))
        eg_integrations.mesosphere = eg_mesosphere

    if ecs:
        eg_ecs = spotinst.aws_elastigroup.EcsConfiguration(clusterName=ecs.get('cluster_name'))
        eg_integrations.ecs = eg_ecs

    if kubernetes:
        eg_kube = spotinst.aws_elastigroup.KubernetesConfiguration(apiServer=kubernetes.get('api_server'),
                                                                   token=kubernetes.get('token'))
        eg_integrations.kubernetes = eg_kube

    if rightscale:
        eg_rightscale = spotinst.aws_elastigroup.RightScaleConfiguration(accountId=rightscale.get('account_id'),
                                                                         refreshToken=rightscale.get('refresh_token'))
        eg_integrations.rightScale = eg_rightscale

    if opsworks:
        eg_opsworks = spotinst.aws_elastigroup.OpsWorksConfiguration(layerId=opsworks.get('layer_id'))
        eg_integrations.opsWorks = eg_opsworks

    if eg_integrations.rancher is not None \
            or eg_integrations.rightScale is not None \
            or eg_integrations.opsWorks is not None \
            or eg_integrations.chef is not None \
            or eg_integrations.ecs is not None \
            or eg_integrations.elasticBeanstalk is not None \
            or eg_integrations.mesosphere is not None \
            or eg_integrations.kubernetes is not None:
        eg.thirdPartiesIntegration = eg_integrations


def expand_capacity(eg, module):
    min_size = module.params.get('min_size')
    max_size = module.params.get('max_size')
    target = module.params.get('target')
    unit = module.params.get('unit')

    eg_capacity = spotinst.aws_elastigroup.Capacity()

    if min_size is not None:
        eg_capacity.minimum = min_size

    if max_size is not None:
        eg_capacity.maximum = max_size

    if target is not None:
        eg_capacity.target = target

    if unit is not None:
        eg_capacity.unit = unit

    eg.capacity = eg_capacity


def expand_strategy(eg, module):
    risk = module.params.get('risk')
    utilize_reserved_instances = module.params.get('utilize_reserved_instances')
    fallback_to_ondemand = module.params.get('fallback_to_ondemand')
    on_demand_count = module.params.get('on_demand_count')
    availability_vs_cost = module.params.get('availability_vs_cost')
    draining_timeout = module.params.get('draining_timeout')
    spin_up_time = module.params.get('spin_up_time')
    lifetime_period = module.params.get('lifetime_period')
    terminate_at_end_of_billing_hour = module.params.get('terminate_at_end_of_billing_hour')
    persistence = module.params.get('persistence')
    signals = module.params['signals']

    eg_strategy = spotinst.aws_elastigroup.Strategy()

    if risk is not None:
        eg_strategy.risk = risk
    if utilize_reserved_instances is not None:
        eg_strategy.utilizeReservedInstances = utilize_reserved_instances
    if fallback_to_ondemand is not None:
        eg_strategy.fallbackToOd = fallback_to_ondemand
    if on_demand_count is not None:
        eg_strategy.onDemandCount = on_demand_count
    if availability_vs_cost is not None:
        eg_strategy.availabilityVsCost = availability_vs_cost
    if draining_timeout is not None:
        eg_strategy.drainingTimeout = draining_timeout
    if spin_up_time is not None:
        eg_strategy.spinUpTime = spin_up_time
    if lifetime_period is not None:
        eg_strategy.lifetimePeriod = lifetime_period
    if terminate_at_end_of_billing_hour is not None:
        eg_scaling_strategy = spotinst.aws_elastigroup.ScalingStrategy()
        eg_scaling_strategy.terminateAtEndOfBillingHour = terminate_at_end_of_billing_hour
        eg_strategy.scalingStrategy = eg_scaling_strategy

    expand_persistence(eg_strategy, persistence)

    expand_signals(eg_strategy, signals)

    eg.strategy = eg_strategy


def expand_signals(eg_strategy, signals):
    if signals is not None:
        eg_signals = []

        for signal in signals:
            eg_signal = spotinst.aws_elastigroup.Signal()
            if signal.get('name') is not None:
                eg_signal.name = signal.get('name')
            if signal.get('timeout') is not None:
                eg_signal.timeout = signal.get('timeout')

            if eg_signal.name is not None:
                eg_signals.append(eg_signal)

        if eg_signals.__sizeof__() > 0:
            eg_strategy.signals = eg_signals


def expand_tags(eg_launchspec, tags):
    if tags is not None:
        eg_tags = []

        for tag in tags:
            eg_tag = spotinst.aws_elastigroup.Tag()
            if tag.get('key') is not None:
                eg_tag.tagKey = tag.get('key')
            if tag.get('value') is not None:
                eg_tag.tagValue = tag.get('value')

            eg_tags.append(eg_tag)

        if eg_tags.__sizeof__() > 0:
            eg_launchspec.tags = eg_tags


def expand_persistence(eg_strategy, persistence):
    if persistence is not None:
        eg_persistence = spotinst.aws_elastigroup.Persistence()
        eg_persistence.shouldPersistRootDevice = persistence.get('should_persist_root_device')
        eg_persistence.shouldPersistBlockDevices = persistence.get('should_persist_block_devices')
        eg_persistence.shouldPersistPrivateIp = persistence.get('should_persist_private_ip')
        eg_strategy.persistence = eg_persistence


def expand_scaling(eg, module):
    up_scaling_policies = module.params['up_scaling_policies']
    down_scaling_policies = module.params['down_scaling_policies']

    eg_scaling = spotinst.aws_elastigroup.Scaling()

    if up_scaling_policies is not None:
        eg_up_scaling_policies = expand_scaling_policies(up_scaling_policies)
        if eg_up_scaling_policies.__sizeof__() > 0:
            eg_scaling.up = eg_up_scaling_policies

    if down_scaling_policies is not None:
        eg_down_scaling_policies = expand_scaling_policies(down_scaling_policies)
        if eg_down_scaling_policies.__sizeof__() > 0:
            eg_scaling.down = eg_down_scaling_policies

    if eg_scaling.down is not None or eg_scaling.up is not None:
        eg.scaling = eg_scaling


def expand_scaling_policies(scaling_policies):
    eg_scaling_policies = []

    for policy in scaling_policies:
        eg_policy = spotinst.aws_elastigroup.ScalingPolicy()

        if policy.get('policyName') is not None:
            eg_policy.policyName = policy.get('policyName')

        if policy.get('namespace') is not None:
            eg_policy.namespace = policy.get('namespace')

        if policy.get('metricName') is not None:
            eg_policy.metricName = policy.get('metricName')

        if policy.get('dimensions') is not None:
            eg_policy.dimensions = policy.get('dimensions')

        if policy.get('statistic') is not None:
            eg_policy.statistic = policy.get('statistic')

        if policy.get('evaluationPeriods') is not None:
            eg_policy.evaluationPeriods = policy.get('evaluationPeriods')

        if policy.get('period') is not None:
            eg_policy.period = policy.get('period')

        if policy.get('threshold') is not None:
            eg_policy.threshold = policy.get('threshold')

        if policy.get('cooldown') is not None:
            eg_policy.cooldown = policy.get('cooldown')

        eg_scaling_action = spotinst.aws_elastigroup.ScalingPolicyAction()

        if policy.get('action_type') is not None:
            eg_scaling_action.type = policy.get('action_type')

        if policy.get('adjustment') is not None:
            eg_scaling_action.adjustment = policy.get('adjustment')

        if policy.get('min_target_capacity') is not None:
            eg_scaling_action.minTargetCapacity = policy.get('min_target_capacity')

        if policy.get('max_target_capacity') is not None:
            eg_scaling_action.maxTargetCapacity = policy.get('max_target_capacity')

        if policy.get('target') is not None:
            eg_scaling_action.target = policy.get('target')

        if policy.get('minimum') is not None:
            eg_scaling_action.minimum = policy.get('minimum')

        if policy.get('maximum') is not None:
            eg_scaling_action.maximum = policy.get('maximum')

        if policy.get('unit') is not None:
            eg_policy.unit = policy.get('unit')

        if policy.get('operator') is not None:
            eg_policy.operator = policy.get('operator')

        if policy.get('threshold') is not None:
            eg_policy.threshold = policy.get('threshold')

        eg_scaling_policies.append(eg_policy)

    return eg_scaling_policies


def main():
    fields = dict(
        name=dict(type='str'), elastic_ips=dict(type='list'),
        on_demand_instance_type=dict(type='str'), spot_instance_types=dict(type='list'),
        ebs_volume_pool=dict(type='list'),
        availability_zones=dict(type='list'), product=dict(type='str'), user_data=dict(type='str'),
        key_pair=dict(type='str'), i_am_role=dict(type='str'), tenancy=dict(type='str'),
        shut_down_script=dict(type='str'), monitoring=dict(type='str'), ebs_optimized=dict(type='bool'),
        image_id=dict(type='str'), health_check_type=dict(type='str'), health_check_grace_period=dict(type='int'),
        security_group_ids=dict(type='list'), tags=dict(type='list'), load_balancers=dict(type='list'),
        target_group_arns=dict(type='list'), block_device_mappings=dict(type='list'),
        network_interfaces=dict(type='list'), rancher=dict(required=False, default=None),
        mesosphere=dict(required=False, default=None), elastic_beanstalk=dict(required=False, default=None),
        ecs=dict(required=False, default=None), kubernetes=dict(required=False, default=None),
        rightscale=dict(required=False, default=None), opsworks=dict(required=False, default=None),
        chef=dict(required=False, default=None), max_size=dict(type='int'), min_size=dict(type='int'),
        target=dict(type='int'), unit=dict(type='str'), utilize_reserved_instances=dict(type='bool'),
        fallback_to_ondemand=dict(type='bool'), risk=dict(type='int'), on_demand_count=dict(type='int'),
        availability_vs_cost=dict(type='str'),
        draining_timeout=dict(type='int'), spin_up_time=dict(type='int'), lifetime_period=dict(type='int'),
        terminate_at_end_of_billing_hour=dict(type='bool'), persistence=dict(required=False, default=None),
        signals=dict(type='list'), up_scaling_policies=dict(type='list'), down_scaling_policies=dict(type='list')
    )

    module = AnsibleModule(argument_spec=fields)

    creds = retrieve_creds()
    token = creds["token"]
    client = spotinst.SpotinstClient(authToken=token)

    create_autoscaling_group(client=client, module=module)
    module.exit_json(changed=False, meta=module.params)


def retrieve_creds():
    # Retrieve auth token
    home = expanduser("~")
    vars = dict()
    with open(home + "/.spotinst/credentials", "r") as creds:
        for line in creds:
            eq_index = line.find('=')
            var_name = line[:eq_index].strip()
            string_value = line[eq_index + 1:].strip()
            vars[var_name] = string_value
    return vars


if __name__ == '__main__':
    main()
