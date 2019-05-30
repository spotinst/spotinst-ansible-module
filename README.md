# spotinst-ansible-module
An Ansible Module for creating or deleting Spotinst Elastigroups

## Table of contents
<!--ts-->
   * [Requirements](#requirements)
   * [Installation](#installation)
   * [Configuring Credentials](#configuring-credentials)
   * [Usage](#usage)
   * Examples:
      * [Elastigroup](./examples/elastigroup)
        * [Getting Started With Elastigroup](./examples/elastigroup/elastigroup-basic.yml)
        * [Elastigroup Advanced](./examples/elastigroup/elastigroup-advanced.yml)
        * [Elastigroup Additional Configurations](./examples/elastigroup/elastigroup-additional-configurations.yml)
          * [Scaling](./examples/elastigroup/elastigroup-scaling-policies.yml)
          * [Stateful](./examples/elastigroup/elastigroup-stateful.yml)
          * [Scheduling](./examples/elastigroup/elastigroup-scheduling.yml)
          * [Load Balancing](./examples/elastigroup/elastigroup-load-balancers.yml)
        * Third Party Integrations
          * [ECS](./examples/elastigroup/elastigroup-ecs.yml)
          * [Kubernetes](./examples/elastigroup/elastigroup-kubernetes.yml)
          * [Nomad](./examples/elastigroup/elastigroup-nomad.yml)
          * [Docker Swarm](./examples/elastigroup/elastigroup-docker-swarm.yml)
          * [CodeDeploy](./examples/elastigroup/elastigroup-code-deploy.yml)
          * [Route53](./examples/elastigroup/elastigroup-route53.yml)
          * [ElasticBeanstalk](./examples/elastigroup/elastigroup-elasticbeanstalk.yml)
      * [EMR](./examples/emr)
        * [Create EMR Cluster](./examples/emr/spotinst-emr.yml)
      * [Ocean](./examples/ocean)
        * [Create Ocean Cluster](./examples/ocean/spotinst-ocean.yml)
      * [Event Subscription](./examples/events)
        * [Create Event Subscription](./examples/events/spotinst-event-subscription.yml)
<!--te-->

## Requirements
- [spotinst-sdk-python](https://github.com/spotinst/spotinst-sdk-python) >= `v1.0.44`

## Installation
If you'd like to work with this version of the module and not the supplied version that is packaged with Ansible,
you can copy the module into your Ansible module directory. 
```bash
git clone https://github.com/spotinst/spotinst-ansible-module
mkdir -p /root/.ansible/plugins/modules/cloud/
cp -r spotinst-ansible-module/spotinst/ /root/.ansible/plugins/modules/cloud/
```
Otherwise the module comes pre-installed with the latest [Ansible](https://github.com/ansible/ansible) release.

## Configuring Credentials
The mechanism in which the module looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials. 
The order in which the sdk searches for credentials is:
  1. Fetching the account and token from environment variables under `SPOTINST_ACCOUNT` & `SPOTINST_TOKEN`

If you choose to not pass your credentials directly you configure a credentials file, this file should be a valid `.yml` file.
The default shared credential file location is `~/.spotinst/credentials` 
- example

```yaml
default: #profile
  token: $defaul_spotinst_token
  account: $default_spotinst-account-id
```
  
  2. You can overwrite the credentials file location and the profile used as parameters `credentials_path` inside the playbook
- example
  
```yaml
- hosts: localhost
  tasks:
    - name: example elastigroup
      spotinst_aws_elastigroup:
          name: ansible_test_group
          state: present
          credentials_path: /path/to/file
...
```

  3. You can overwrite the credentials file location used as environment variables `SPOTINST_PROFILE` and/or `SPOTINST_SHARED_CREDENTIALS_FILE`

## Usage
```bash
ansible-playbook elastigroup-basic.yml
```

### Argument Reference
- [spotinst_aws_elastigroup](./docs/argument_reference_eg.yml)  
- [spotinst_mrScaler](./docs/argument_reference_emr.yml)
- [spotinst_ocean_cloud](./docs/argument_reference_ocean.yml)

More information can be found in the official Ansible [documentation](https://docs.ansible.com/ansible/latest/modules/spotinst_aws_elastigroup_module.html#spotinst-aws-elastigroup-module) 
page as well as in the spotinst [documentation](https://help.spotinst.com/hc/en-us/articles/115003530285-Ansible-).

