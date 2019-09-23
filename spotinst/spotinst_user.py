#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}
DOCUMENTATION = """
---
module: spotinst_user
version_added: 2.9
short_description: Create, update or delete Spotinst User
author: Marco Braga (@mtulio)
description:
  - Create, update or delete Spotinst User
    You will have to have a credentials file in this location - <home>/.spotinst/credentials
    The credentials file must contain a row that looks like this
    token = <YOUR TOKEN>
    Full documentation available at U(https://help.spotinst.com/hc/en-us/articles/115003530285-Ansible-)
requirements:
  - python >= 2.7
  - spotinst_sdk >= 1.0.48
options:

  credentials_path:
    default: "~/.spotinst/credentials"
    description:
      - Optional parameter that allows to set a non-default credentials path.
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
      - create, update or delete

  email:
    type: str
    description:
      - Email that is the username on Spotinst

  first_name:
    type: str
    description:
      - First name

  last_name:
    type: str
    description:
      - First name

  password:
    type: str
    description:
      - First name

  role:
    type: str
    choices:
      - admin
      - viewer
    default: viewer
    description:
      - role from default Account

  role_mapping:
    type: list
    description:
      - List of role Mapping
"""
EXAMPLES = """

# create user and assigned to Account with Role mapping

- spotinst_user:
    email: "{{ item.email }}"
    first_name: "{{ item.first_name }}"
    last_name: "{{ item.last_name }}"
    password: "{{ item.password }}"
    role_default: "{{ item.role_default |d(omit) }}"
    role_mapping: "{{ item.role_mapping |d(omit) }}"
  with_items:
    - email: teste-01@mydomain.com.br
      first_name: "test"
      last_name: "last01"
      password: "Password1234!"
      role_default: "viewer"
      role_mapping: [{
          "account_id": "act-604e8730",
          "account_name": "x-test-01",
          "role": "viewer"
      }]
"""
RETURN = """
---
result:
    type: dict
    sample: sis-e62dfd0f
    returned: success
    description: Created Subscription successfully
"""

HAS_SPOTINST_SDK = False
__metaclass__ = type

import os
import time
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback

try:
    import spotinst_sdk as spotinst
    from spotinst_sdk import SpotinstClientException

    HAS_SPOTINST_SDK = True

except ImportError:
    pass


def handle_user(client, module):
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

    has_changed = False
    try:
      found, user = find_user(client, module)
      if not found:
        resp, message, has_changed = create_user(client, module)
        if resp["code"] == 200:
          message = 'User Created successfully'

        resp, message, has_changed = mapping_user(client, module, message, has_changed)
        if resp["code"] == 200:
          message = 'User Created successfully'

      else:
        resp, message, has_changed = update_user_mapping(client, module)
        if resp["code"] == 200:
          message = 'User Updated successfully'

      found, user = find_user(client, module)
      if found:
        user = {
          "email": module.params.get('email'),
          "roles": user
        }

    except Exception as e:
      module.fail_json(msg="Error getting Spotinst User mapping: {}".format(e))

    return user, message, has_changed


def get_ExceptionMessage(e):
    errmsg, payload = e.message.split('\n')
    return {
      "err": errmsg,
      "payload": json.loads(payload)
    }


def get_ExceptionErrorCode(err):
  errCode = "Unknown"
  try:
    for e in err["payload"]["errors"]:
      return e["code"]
  except:
    pass
  return errCode


def find_user(client, module):
    email = module.params.get('email')

    found, user = False, ""
    try:
      user = client.get_user(email)
      found = True

    except spotinst.SpotinstClientException as e:
      errCode = get_ExceptionErrorCode(get_ExceptionMessage(e))
      if errCode == 'USER_DOES_NOT_EXIST':
        found = False

    except Exception as e:
      module.fail_json(msg="Error On User's lookup: {}".format(e))

    return found, user


def create_user(client, module):
    first_name = module.params.get('first_name')
    last_name = module.params.get('last_name')
    email = module.params.get('email')
    password = module.params.get('password')
    role = module.params.get('role')
    has_changed = True

    if not role:
      module.fail_json(msg="Error Creating User: role must be provided for New Users")

    try:
      resp = client.create_user(first_name, last_name, email, password, role)
      message = "User Created successfully"

    except spotinst.SpotinstClientException as e:
      errMsg = get_ExceptionMessage(e)
      errors = []
      for er in errMsg["payload"]["errors"]:
        errors.append(er["message"])
      module.fail_json(msg="{}: {}".format(errMsg["err"], errors))

    except Exception as e:
      module.fail_json(msg="Error Creating User: {}".format(e))

    return resp, message, has_changed


def mapping_user(client, module, message, has_changed):
    role_mapping = module.params.get('role_mapping')
    email = module.params.get('email')
    try:
      accountUserMapping = []
      for m in role_mapping:
        accountUserMapping.append({
          "user_email": email,
          "account_id": m["account_id"],
          "role": m["role"]
        })

      resp = client.assign_user_to_account(accountUserMapping)
    except Exception as e:
      module.fail_json(msg="Error Mapping User: {}".format(e))

    return resp, message, has_changed


def update_user_mapping(client, module):
    role_mapping = module.params.get('role_mapping')
    email = module.params.get('email')

    try:
      accountUserMapping = []
      for m in role_mapping:
        resp = client.account_id = m["account_id"]
        resp = client.update_user_role(email, m["role"])
        has_changed = True
        message = 'User Mapping Updated Successful'
    except Exception as e:
      module.fail_json(msg="Error Updating User Map: {}".format(e))

    return resp, message, has_changed


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


def main():
    fields = dict(
        token=dict(type='str', fallback=(env_fallback, ['SPOTINST_TOKEN'])),
        credentials_path=dict(type='path', default="~/.spotinst/credentials"),
        generate_token=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        email=dict(type='str'),
        first_name=dict(type='str'),
        last_name=dict(type='str'),
        password=dict(type='str', no_log=True),
        role=dict(type='str', choices=['admin', 'viewer'], default="viewer"),
        role_mapping=dict(type='list'),
    )

    module = AnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(msg="the Spotinst SDK library is required. (pip install spotinst_sdk)")

    client = get_client(module=module)

    user, message, has_changed = handle_user(client=client, module=module)

    module.exit_json(changed=has_changed, spotinst_user=user, message=message)


if __name__ == '__main__':
    main()
