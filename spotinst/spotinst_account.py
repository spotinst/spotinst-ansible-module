#!/usr/bin/python
# Copyright (c) 2020 Ansible Project
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
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import open_url

try:
    import spotinst_sdk as spotinst
    from spotinst_sdk import SpotinstClientException

    HAS_SPOTINST_SDK = True

except ImportError:
    pass



## START - SHARED MODULES

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


def retErrMessage(message, debugErr=None):
  """Create the error message """
  e = {
    "err": True,
    "errMsg": message
  }
  if debugErr:
    e["errDebug"] = debugErr
  return e


def getConfigCredentials(credentials_path=None):
    # Retrieve creds file variables
    creds_file_loaded_vars = dict()
    if credentials_path is not None:
        try:
            with open(credentials_path, "r") as creds:
                for line in creds:
                    eq_index = line.find('=')
                    var_name = line[:eq_index].strip()
                    var_value = line[eq_index + 1:].strip()
                    creds_file_loaded_vars[var_name] = var_value
        except IOError:
            pass

    return creds_file_loaded_vars


def getOAuthTokenFromVar():
    """ TODO """
    return


def requestOAuthToken():
    """
    Generate a new bearer token and return it.
    """
    sp_username = os.getenv("SPOTINST_USER")
    sp_password = os.getenv("SPOTINST_PASSWORD")
    sp_client_id = os.getenv("SPOTINST_CLIENT_ID")
    sp_client_sec = os.getenv("SPOTINST_CLIENT_SECRET")

    if (not sp_username) or (not sp_password):
      return {
        "err": True,
        "errMsg": "SPOTINST_USER or SPOTINST_PASSWORD env var not found"
      }
    if (not sp_client_id) or (not sp_client_sec):
      return {
        "err": True,
        "errMsg": "SPOTINST_CLIENT_ID or SPOTINST_CLIENT_SECRET env var not found"
      }

    headers = {
      "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = "username={}&password={}&grant_type=password&client_id={}&client_secret={}".format(
      sp_username, sp_password, sp_client_id, sp_client_sec
    )
    authURL = "https://oauth.spotinst.io/token"

    try:
      resp = open_url(authURL, method="POST", data=payload, headers=headers)
    except Exception as e:
      return retErrMessage("Unable to open request to retrieve token", debugErr=e)

    try:
      respJS = json.loads(resp.read())
      if "response" not in respJS:
        return retErrMessage("Unable to get response payload", debugErr=e)
      try:
        accessToken = respJS["response"]["items"][0]["accessToken"]
      except Exception as e:
        return retErrMessage("Unable to get access token", debugErr=e)

      return accessToken

    except Exception as e:
      return retErrMessage("Unable to parse token response", debugErr=e)

    return None


def getOAuthUserToken():
    """
    - [TODO] Get local TOKEN (already generated), if not found, then
    - Generate a new token from user and pass

    """

    sp_user_token = os.getenv("SPOTINST_USER_TOKEN")
    sp_user_token_ttl = os.getenv("SPOTINST_USER_TOKEN_TTL")
    if not sp_user_token:
      return requestOAuthToken()

    return retErrMessage("Unavailable option to get current token", debugErr=e)


def get_client(module, account=None):
    """
    Credentials order (first is higher):
    - module argument
    - token env vars (TODO)
    - user and pass credentials to request a new token
    - credentials file
    """

    # Token
    try:
      token = module.params.get('token')
      if not token:
          token = getOAuthUserToken()
          if not token:
              # Retrieve creds file variables
              creds_file_loaded_vars = getConfigCredentials(
                credentials_path=module.params.get('credentials_path')
              )
              token = creds_file_loaded_vars.get("token")
    except Exception as e:
      module.fail_json(msg="ERROR: {}".format(e))

    # account
    if not account:
      account = module.params.get('account_id')
    if account:
      return spotinst.SpotinstClient(
          auth_token=token,
          account_id=account,
          print_output=True,
        )

    return spotinst.SpotinstClient(
        auth_token=token,
        print_output=True,
      )

## END - SHARED MODULES


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
    message = "Account"
    has_changed = True

    # create if not exists
    ac_check = find_account(client, account_name)
    if len(ac_check) <= 0:
      try:
        account = client.create_account(account_name=account_name)
        message = 'Created Account'
      except Exception as e:
        module.fail_json(msg="ERROR handle_create() {} ".format(e))
    elif len(ac_check) > 1:
      message = 'More than one account found with same name, exiting'
      return ac_check, message, False
    else:
      account = ac_check[0]

    if account and cloud == 'aws':
      try:
        iam_role = module.params.get('aws_iam_role')
        external_id = module.params.get('aws_external_id')

        ac_check = find_account(client, account_name)
        if len(ac_check) <= 0:
            message = 'Account not found to setup External Cloud Provider'
            module.fail_json(msg=message)

        # check if it's already setup
        account = ac_check[0]
        if account["provider_external_id"] is not None:
          message += ' Cloud Provider is already updated'
          has_changed = False
          return account, message, has_changed

        # create new client to setup the account
        ## SDK (#62) does not support setup account with global tokens,
        ## so forcing to switch account on current client session.
        client.account_id = account["account_id"]

        resp = client.set_cloud_credentials(
            iam_role=iam_role,
            external_id=external_id,
        )
        message += ' and Cloud {} Setup successfully'.format(cloud)
      except Exception as e:
        module.fail_json(msg=e)

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
