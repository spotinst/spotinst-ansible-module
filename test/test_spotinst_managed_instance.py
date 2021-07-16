import unittest
import sys
from mock import MagicMock

sys.modules['spotinst_sdk'] = MagicMock()


from ansible.modules.cloud.spotinst.spotinst_aws_managed_instance import turn_to_model
from spotinst_sdk2.models.managed_instance.aws import *


class MockModule:

    def __init__(self, input_dict):
        self.params = input_dict


class TestTurnToModel(unittest.TestCase):
    """Unit test for the turn to model helper function"""

    def test_all_fields(self):
        """Format input into proper json structure"""

        input_dict = {'fake_plain_list': [1, 2], 'fake_field': [[1, 2, 3], [4, 5, 6]],
                      'name': 'mi-managed-instance-example-new-check-pause',
                      'description': 'a nicely Managed Instance created via Ansible', 'region': 'us-west-2',
                      'persistence': {'persist_block_devices': True, 'persist_root_device': True,
                                      'block_devices_mode': 'onLaunch',
                                      'persist_private_ip': None},
                      'strategy': {'life_cycle': 'spot', 'revert_to_spot': {'perform_at': 'always'},
                                   'orientation': None,
                                   'draining_timeout': None, 'fallback_to_od': None, 'utilize_reserved_instances': None,
                                   'utilize_commitments': None, 'optimization_windows': None,
                                   'minimum_instance_lifetime': None},
                      'health_check': {'type': 'EC2', 'grace_period': 120, 'unhealthy_duration': 120,
                                       'auto_healing': None},
                      'compute': {'product': 'Linux/UNIX', 'launch_specification': {'image_id': 'ami-082b5a644766e0e6f',
                                                                                    'instance_types': {
                                                                                        'types': ['t2.micro',
                                                                                                  't3.small',
                                                                                                  't3.micro'],
                                                                                        'preferred_type': 't2.micro'},
                                                                                    'key_pair': 'shibel-core-oregon',
                                                                                    'security_group_ids': [
                                                                                        'sg-03ea0016f98e3c04d'],
                                                                                    'ebs_optimized': None,
                                                                                    'monitoring': None,
                                                                                    'tenancy': None, 'iam_role': None,
                                                                                    'tags': None,
                                                                                    'resource_tag_specification': None,
                                                                                    'user_data': None,
                                                                                    'shutdown_script': None,
                                                                                    'credit_specification': None,
                                                                                    'network_interfaces': None,
                                                                                    'block_device_mappings': None},
                                  'subnet_ids': ['subnet-0d67e8b90c74986c8'], 'vpc_id': 'vpc-4a74eb32',
                                  'elastic_ip': None,
                                  'private_up': None},
                      'scheduling': {'tasks': [
                          {'is_enabled': True, 'frequency': 'weekly', 'start_time': '2050-22-22T00:00:00Z',
                           'task_type': 'pause',
                           'cron_expression': None}]},
                      'integrations': {'route53': {
                          'domains': [
                              {'hosted_zone_id': '1', 'spotinst_account_id': 'act-xxx', 'record_set_type': 'a',
                               'record_sets': [{'name': 'some_name', 'use_public_ip': True, 'use_public_dns': None}]}]},
                          'load_balancers_config': None}}

        module = MockModule(input_dict=input_dict)
        mi: ManagedInstance = turn_to_model(module.params, ManagedInstance())
        # test name
        self.assertEqual(mi.name, "mi-managed-instance-example-new-check-pause")

        # test description
        self.assertEqual(mi.description, "a nicely Managed Instance created via Ansible")

        # test region
        self.assertEqual(mi.region, "us-west-2")

        # test fake_plain_list
        self.assertEqual(mi.fake_plain_list, [1, 2])
        self.assertEqual(mi.fake_field, [[1, 2, 3], [4, 5, 6]])

        # test persistence
        expected_persistence = Persistence(persist_block_devices=True, persist_root_device=True,
                                           block_devices_mode="onLaunch")
        actual_persistence = mi.persistence
        self.assertEqual(actual_persistence.persist_private_ip, expected_persistence.persist_private_ip)
        self.assertEqual(actual_persistence.persist_block_devices, expected_persistence.persist_block_devices)
        self.assertEqual(actual_persistence.persist_root_device, expected_persistence.persist_root_device)
        self.assertEqual(actual_persistence.block_devices_mode, expected_persistence.block_devices_mode)

        # test strategy
        actual_strategy = mi.strategy
        expected_strategy = Strategy(life_cycle="spot", revert_to_spot=RevertToSpot(perform_at="always"))
        self.assertEqual(actual_strategy.life_cycle, expected_strategy.life_cycle)
        self.assertEqual(actual_strategy.revert_to_spot.perform_at, expected_strategy.revert_to_spot.perform_at)
        self.assertEqual(actual_strategy.fallback_to_od, expected_strategy.fallback_to_od)
        self.assertEqual(actual_strategy.utilize_reserved_instances, expected_strategy.utilize_reserved_instances)
        self.assertEqual(actual_strategy.utilize_commitments, expected_strategy.utilize_commitments)
        self.assertEqual(actual_strategy.draining_timeout, expected_strategy.draining_timeout)
        self.assertEqual(actual_strategy.optimization_windows, expected_strategy.optimization_windows)
        self.assertEqual(actual_strategy.orientation, expected_strategy.orientation)
        self.assertEqual(actual_strategy.minimum_instance_lifetime, expected_strategy.minimum_instance_lifetime)

        # test compute
        launch_spec = LaunchSpecification(
            instance_types=InstanceTypes(preferred_type="t2.micro", types=["t2.micro", "t3.small", "t3.micro"]),
            image_id="ami-082b5a644766e0e6f",
            key_pair="shibel-core-oregon",
            security_group_ids=["sg-03ea0016f98e3c04d"]
        )

        expected_compute = Compute(subnet_ids=["subnet-0d67e8b90c74986c8"], vpc_id="vpc-4a74eb32",
                                   launch_specification=launch_spec)

        actual_compute = mi.compute
        self.assertEqual(expected_compute.subnet_ids, actual_compute.subnet_ids)
        self.assertEqual(expected_compute.vpc_id, actual_compute.vpc_id)
        self.assertEqual(expected_compute.launch_specification.image_id, actual_compute.launch_specification.image_id)
        self.assertEqual(expected_compute.launch_specification.ebs_optimized,
                         actual_compute.launch_specification.ebs_optimized)
        self.assertEqual(expected_compute.launch_specification.key_pair,
                         actual_compute.launch_specification.key_pair)
        self.assertEqual(expected_compute.launch_specification.security_group_ids,
                         actual_compute.launch_specification.security_group_ids)
        self.assertEqual(expected_compute.launch_specification.instance_types.types,
                         actual_compute.launch_specification.instance_types.types)
        self.assertEqual(expected_compute.launch_specification.instance_types.preferred_type,
                         actual_compute.launch_specification.instance_types.preferred_type)
        self.assertEqual(expected_compute.launch_specification.iam_role,
                         actual_compute.launch_specification.iam_role)
        self.assertEqual(expected_compute.launch_specification.shutdown_script,
                         actual_compute.launch_specification.shutdown_script)
        self.assertEqual(expected_compute.launch_specification.user_data,
                         actual_compute.launch_specification.user_data)
        self.assertEqual(expected_compute.launch_specification.monitoring,
                         actual_compute.launch_specification.monitoring)
        self.assertEqual(expected_compute.launch_specification.tenancy,
                         actual_compute.launch_specification.tenancy)

        # test health check
        expected_health_check = HealthCheck(type="EC2", grace_period=120, unhealthy_duration=120)
        actual_health_check = mi.health_check
        self.assertEqual(expected_health_check.type, actual_health_check.type)
        self.assertEqual(expected_health_check.grace_period, expected_health_check.grace_period)
        self.assertEqual(expected_health_check.unhealthy_duration, expected_health_check.unhealthy_duration)

        # test scheduling
        expected_scheduling = Scheduling(
            tasks=[Task(is_enabled=True, frequency="weekly", start_time="2050-22-22T00:00:00Z", task_type="pause")])
        actual_scheduling = mi.scheduling
        self.assertEqual(len(expected_scheduling.tasks), len(actual_scheduling.tasks))
        first_expected_task = expected_scheduling.tasks[0]
        first_actual_task = actual_scheduling.tasks[0]
        self.assertEqual(first_expected_task.task_type, first_actual_task.task_type)
        self.assertEqual(first_expected_task.is_enabled, first_actual_task.is_enabled)
        self.assertEqual(first_expected_task.frequency, first_actual_task.frequency)
        self.assertEqual(first_expected_task.start_time, first_actual_task.start_time)

        # test integrations.route53
        record_set = Route53RecordSetConfiguration(name="some_name", use_public_ip=True)
        domains_config = Route53DomainConfiguration(record_sets=[record_set], hosted_zone_id="1",
                                                    spotinst_account_id="act-xxx", record_set_type="a")
        route53_config = Route53Configuration(domains=[domains_config])

        expected_integrations = IntegrationsConfig(route53=route53_config)
        actual_integrations = mi.integrations

        self.assertEqual(len(actual_integrations.route53.domains), len(expected_integrations.route53.domains))
        self.assertEqual(len(actual_integrations.route53.domains), 1)
        exp_first_domain = expected_integrations.route53.domains[0]
        act_first_domain = actual_integrations.route53.domains[0]
        self.assertEqual(exp_first_domain.spotinst_account_id, act_first_domain.spotinst_account_id)
        self.assertEqual(exp_first_domain.record_set_type, act_first_domain.record_set_type)
        self.assertEqual(exp_first_domain.hosted_zone_id, act_first_domain.hosted_zone_id)
        self.assertEqual(len(exp_first_domain.record_sets), len(act_first_domain.record_sets))
        self.assertEqual(len(exp_first_domain.record_sets), 1)
        exp_first_record_set = exp_first_domain.record_sets[0]
        act_first_record_set = act_first_domain.record_sets[0]
        self.assertEqual(exp_first_record_set.name, act_first_record_set.name)
        self.assertEqual(exp_first_record_set.use_public_ip, act_first_record_set.use_public_ip)
        self.assertEqual(exp_first_record_set.use_public_dns, act_first_record_set.use_public_dns)
