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
        * [Create Event Subscription via role](./examples/events/spotinst-event-subscription-role.yml)
<!--te-->

## Requirements
* [Requirements](./requirements.txt)

    - [spotinst-sdk2](https://pypi.org/project/spotinst-sdk2/)

      For more details on differences between 'spotinst-sdk' and 'spotinst-sdk2' see - [README](https://github.com/spotinst/spotinst-sdk-python/tree/v2)
      
    - [ansible](https://pypi.org/project/ansible/)
    - [mock](https://pypi.org/project/mock/)

## Installation
### Module directory
If you'd like to work with this version of the module and not the supplied version that is packaged with Ansible,
you can copy the module into your Ansible module directory. 

Example, assuming your Ansible module directory is at - '~/.ansible':
```bash
git clone https://github.com/spotinst/spotinst-ansible-module
mkdir -p ~/.ansible/plugins/modules/cloud/
cp -r spotinst-ansible-module/spotinst/ ~/.ansible/plugins/modules/cloud/
```
Otherwise the module comes pre-installed with the latest [Ansible](https://github.com/ansible/ansible) release.

### Role directory
You also can use this project as an Ansible role to be available in your playbook though `library/` directory. 

- See how you can create module as an [role](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-module-locally)

Clone the project, or create a git module, into your roles directory (see `roles_path=` on `ansible.cfg`).
 1. Clone in roles path `./roles`:
```bash
git clone https://github.com/spotinst/spotinst-ansible-module roles/spotinst-ansible-module
```
 2. Use as git module:
```bash
git submodule add git@github.com:spotinst/spotinst-ansible-module.git roles/spotinst-ansible-module
```
 3. Use the module in your playbook. See `role` section on [playbook spotinst-event-subscription-role.yml](./examples/events/spotinst-event-subscription-role.yml)

## Configuring Credentials
The mechanism in which the module looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials. 
The order in which the sdk searches for credentials is:
  1. Fetching the account and token from environment variables under `SPOTINST_ACCOUNT` & `SPOTINST_TOKEN`

If you choose to not pass your credentials directly you configure a credentials file, this file should be a valid `.yml` file.
The default shared credential file location is `~/.spotinst/credentials` 
- example

```yaml
default: #profile
  token: $default_spotinst_token
  account: $default_spotinst_account_id
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

