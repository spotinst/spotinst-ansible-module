#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}
DOCUMENTATION = """
---
module: spotinst_facts
version_added: 2.9
short_description: Retrieve information from Spotinst
author: Marco Braga (@mtulio)
description:
  - Retrieve facts from Spotinst. Supported services: Accounts and Users
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

  type:
    description:
      - Type of fact to retrieve information from. Supported: account, user
    type: str

  filter:
    description:
      - Filters dictionary
    type: str

"""
EXAMPLES = """

# list all accounts from Current Token's Organizations

- spotinst_facts:
    type: account
  register: spotinst_accounts

# list all users

- spotinst_facts:
    type: user
  register: spotinst_user

# list user with email

- spotinst_facts:
    type: user
    filter:
      email: 'marco@test.com.br'
  register: spotinst_user

# list users filtered by email

- spotinst_facts:
    type: user
    filter:
      email:
        - 'user1@test.com.br'
        - 'user2@test.com.br'
  register: spotinst_user

"""
RETURN = """
---
result:
    type: list
    sample:
      "message": "Successfully get Users Role Mapping",
      "spotinst_facts": [
          {
            "email": "user1@domain.com.br",
            "roles": [
                {
                    "account_id": "act-a5b62853",
                    "account_name": "account-01",
                    "permission_strategy": null,
                    "role": "editor"
                },
                {
                    "account_id": "act-d79a6b85",
                    "account_name": "account-02",
                    "permission_strategy": null,
                    "role": "viewer"
                }
            ]
          },
          {
              "email": "user2@test.com.br",
              "error": "User Not Found"
          }
      ]
    returned: success
    description: uccessfully get Accounts
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


def handle_facts(client, module):
    request_type = module.params.get('type')

    if request_type == "account":
        fact, message, has_changed = handle_accounts(client=client, module=module)
    elif request_type == "user":
        fact, message, has_changed = handle_user(client=client, module=module)
    else:
        module.fail_json(msg="Request {} Not Allowed.")

    return fact, message, has_changed


def handle_accounts(client, module):

    try:
      accounts = client.get_accounts()
    except Exception as e:
      module.fail_json(msg="Unknown error getting Spotinst Accounts")

    message = 'Successfully get Accounts'
    has_changed = False

    return accounts, message, has_changed


def get_AccountNameById(client, module, account_id):
    global cached_accounts
    if len(cached_accounts) < 1:
      try:
        cached_accounts = client.get_accounts()
      except Exception as e:
        module.fail_json(msg="Error getting Spotinst Accounts: {}".format(e))

    for a in cached_accounts:
      if a["account_id"] == account_id:
        return a["name"]


def map_AccountNameToRoles(client, module, userRoles):
    newRoles = []
    try:
      for r in userRoles:
        try:
          r["account_name"] = get_AccountNameById(client, module, r["account_id"])
        except Exception as e:
          module.fail_json(msg="Error getting Account Name: {}".format(e))
          pass
        newRoles.append(r)
    except Exception as e:
      module.fail_json(msg="Error mapping Account Name: {}".format(e))

    return newRoles


def handle_user(client, module):

    ft = module.params.get('filter')
    if 'email' not in ft:
      module.fail_json(msg="Missing filter for User facts. The valids are: [email]")

    try:
      email = ft["email"]
      userAndRoles = []
      if isinstance(email, list):
        for e in email:
          try:
            userRoles = map_AccountNameToRoles(client, module, client.get_user(e))
            userAndRoles.append({
              "email": e,
              "roles": userRoles
            })
          except:
            userAndRoles.append({
              "email": e,
              "error": "User Not Found"
            })
      else:
        try:
          userRoles = map_AccountNameToRoles(client, module, client.get_user(email))
          userAndRoles.append({
            "email": email,
            "roles": userRoles
          })
        except:
          userAndRoles.append({
            "email": email,
            "error": "User Not Found"
          })
    except Exception as e:
      module.fail_json(msg="Error getting Spotinst User mapping: {}".format(e))
    
    message = 'Successfully get Users Role Mapping'
    has_changed = False

    return userAndRoles, message, has_changed


def main():
    fields = dict(
        token=dict(type='str', fallback=(env_fallback, ['SPOTINST_TOKEN'])),
        credentials_path=dict(type='path', default="~/.spotinst/credentials"),
        type=dict(type='str', choices=['account', 'user']),
        filter=dict(type='dict'),
    )

    global cached_accounts
    cached_accounts = []

    module = AnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(msg="the Spotinst SDK library is required. (pip install spotinst_sdk)")

    client = get_client(module=module)

    spotinst_facts, message, has_changed = handle_facts(client=client, module=module)

    module.exit_json(changed=has_changed, spotinst_facts=spotinst_facts, message=message)


if __name__ == '__main__':
    main()
