#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}
DOCUMENTATION = """
---
module: spotinst_account
version_added: 2.9
short_description: Create, update or delete Spotinst Account
author: Marco Braga (@mtulio)
description:
  - Create, update or delete Spotinst Account
    You will have to have a credentials file in this location - <home>/.spotinst/credentials
    The credentials file must contain a row that looks like this
    token = <YOUR TOKEN>
    Full documentation available at U(https://help.spotinst.com/hc/en-us/articles/115003530285-Ansible-)
requirements:
  - python >= 2.7
  - spotinst_sdk >= 1.0.48
options:

  id:
    description:
      - Parameters used for Updating or Deleting subscription.
    type: str

  credentials_path:
    default: "~/.spotinst/credentials"
    description:
      - Optional parameter that allows to set a non-default credentials path.
    type: str

  account_id:
    description:
      - Optional parameter that allows to set an account-id inside the module configuration. By default this is retrieved from the credentials path
    type: str

  token:
    description:
      - Optional parameter that allows to set an token inside the module configuration. By default this is retrieved from the credentials path
    type: str

  state:
    type: str
    choices:
      - present
      - absent
    default: present
    description:
      - create update or delete

  name:
    description:
      - Account name from current organization
    type: str

  cloud:
    type: str
    choices:
      - aws
    description:
      - Set Cloud Provider to setup to a new Account
    type: str

  aws_iam_role:
    description:
      - AWS IAM Role ARN
    type: str

  aws_external_id:
    description:
      - AWS IAM Role external ID
    type: str
"""
EXAMPLES = """

# create Spotinst account named aws-account-01

- name: Spotinst account creation
  spotinst_account:
    name: "{{ item.name }}"
    state: "{{ item.state |d('present') }}"
    cloud: "{{ item.cloud |d(omit) }}"
    aws_iam_role: "{{ item.aws_iam_role |d(omit) }}"
    aws_external_id: "{{ item.aws_external_id |d(omit) }}"
  with_items:
    - name: x-test-01
      cloud: aws
      aws_iam_role: 'arn:aws:iam::123456789012:role/spotinst'
      aws_external_id: 'spotinst:aws:extid:hahahahah1234560'

# Delete an Spotinst Account

- name: Spotinst account deletion
  spotinst_account:
    name: "{{ item.name }}"
    state: "{{ item.state |d('present') }}"
  with_items:
    - name: x-test-01
      state: absent

"""
RETURN = """
---
result:
    type: str
    sample: sis-e62dfd0f
    returned: success
    description: Created Subscription successfully
"""

HAS_SPOTINST_SDK = False
__metaclass__ = type

import os
import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback

try:
    import spotinst_sdk as spotinst
    from spotinst_sdk import SpotinstClientException

    HAS_SPOTINST_SDK = True

except ImportError:
    pass


def get_client(module):
    # Retrieve creds file variables
    creds_file_loaded_vars = dict()

    credentials_path = module.params.get('credentials_path')

    if credentials_path is not None:
        try:
            with open(credentials_path, "r") as creds:
                for line in creds:
                    eq_index = line.find('=')
                    var_name = line[:eq_index].strip()
                    string_value = line[eq_index + 1:].strip()
                    creds_file_loaded_vars[var_name] = string_value
        except IOError:
            pass
    # End of creds file retrieval

    token = module.params.get('token')
    if not token:
        token = creds_file_loaded_vars.get("token")

    account = module.params.get('account_id')
    if not account:
        account = creds_file_loaded_vars.get("account")

    client = spotinst.SpotinstClient(auth_token=token, print_output=False)

    if account is not None:
        client = spotinst.SpotinstClient(auth_token=token, account_id=account, print_output=False)

    return client


def find_account(client, name):
    accounts = client.get_accounts()
    return list(filter(lambda a: (a["name"] == name), accounts))


def handle_account(client, module):
    account = None
    message = None
    has_changed = False
    request_type = module.params.get('state')

    if request_type == "present":
        account, message, has_changed = handle_create(client=client, module=module)
    elif request_type == "absent":
        account, message, has_changed = handle_delete(client=client, module=module)
    else:
        module.fail_json(msg="Request {} Not Allowed for Account {}".format(request_type, account))

    return account, message, has_changed


def handle_create(client, module):
    account_name = module.params.get('name')
    cloud = module.params.get('cloud')
    allow_dup = module.params.get('allow_duplicates')

    ac_check = find_account(client, account_name)
    if len(ac_check) > 0:
      message = "Account(s) Already exists"
      return ac_check, message, False

    account = client.create_account(account_name=account_name)
    message = 'Created Account successfully'

    if account and cloud == 'aws':
      try:
        iam_role = module.params.get('aws_iam_role')
        external_id = module.params.get('aws_external_id')
        ac_check = find_account(client, account_name)
        ac_id = ac_check[0]["account_id"]

        resp = client.set_cloud_credentials(
            account_id=ac_id,
            iam_role=iam_role,
            external_id=external_id,
        )
        message += ' and Cloud {} Setup'.format(cloud)
      except Exception as e:
        module.fail_json(msg=e)

    has_changed = True
    return account, message, has_changed


def handle_delete(client, module):
    account_name = module.params.get('name')

    accounts = find_account(client, account_name)
    if len(accounts) < 1:
      message = "Account Name [{}] Not Found".format(account_name)
      return accounts, message, False

    try:
      for a in accounts:
        resp = client.delete_account(account_name=a["account_id"])
    except Exception as e:
      module.fail_json(msg=accounts)

    message = 'Account(s) removed successfully'
    has_changed = True

    return accounts, message, has_changed


def main():
    fields = dict(
        account_id=dict(type='str', fallback=(env_fallback, ['SPOTINST_ACCOUNT_ID', 'ACCOUNT'])),
        token=dict(type='str', fallback=(env_fallback, ['SPOTINST_TOKEN'])),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        credentials_path=dict(type='path', default="~/.spotinst/credentials"),
        name=dict(type='str'),
        allow_duplicates=dict(type='bool', default=False),
        cloud=dict(type='str', choices=['aws']),
        aws_iam_role=dict(type='str'),
        aws_external_id=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(msg="the Spotinst SDK library is required. (pip install spotinst_sdk)")

    client = get_client(module=module)

    account, message, has_changed = handle_account(client=client, module=module)

    module.exit_json(changed=has_changed, spotinst_accounts=account, message=message)


if __name__ == '__main__':
    main()
