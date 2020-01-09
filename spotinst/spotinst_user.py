#!/usr/bin/python
# Copyright (c) 2020 Ansible Project
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
      - Last name

  password:
    type: str
    description:
      - Password

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

EXAMPLES = '''
# create user and assigned to Account with Role mapping
- spotinst_user:
    email: "{{ item.email }}"
    first_name: "{{ item.first_name }}"
    last_name: "{{ item.last_name }}"
    password: "{{ item.password }}"
    role_default: "{{ item.role_default |d(omit) }}"
    role_mapping: "{{ item.role_mapping |d(omit) }}"
  with_items:
    - email: firstName.lastName@mydomain.com.br
      first_name: "firstName"
      last_name: "lastName"
      password: "Ch@ngeME"
      role_default: "viewer"
      role_mapping: [{
          "account_id": "act-604e8730",
          "account_name": "x-test-01",
          "role": "viewer"
      }]

# remove user
- spotinst_user:
    email: "{{ item.email }}"
    state: absent
  with_items:
    - email: firstName.lastName@mydomain.com.br
    - email: secondUser@mydomain.com.br

'''
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
from ansible.module_utils.urls import open_url

try:
    import spotinst_sdk as spotinst
    from spotinst_sdk import SpotinstClientException

    HAS_SPOTINST_SDK = True
except ImportError:
    pass


## START SHARED IN MODULES

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


def get_client(module):
    """
    Credentials order (first is higher):
    - module argument
    - token env vars (TODO)
    - user and pass credentials to request a new token
    - credentials file
    """
    try:
      token = module.params.get('token')
      if (not token):
          token = getOAuthUserToken()
          if not token:
              # Retrieve creds file variables
              creds_file_loaded_vars = getConfigCredentials(
                credentials_path=module.params.get('credentials_path')
              )
              token = creds_file_loaded_vars.get("token")
    except Exception as e:
      module.fail_json(msg="ERROR: {}".format(e))

    account = module.params.get('account_id')
    client = spotinst.SpotinstClient(
        auth_token=token,
        account_id=account,
        print_output=True,
      )

    return client

## END SHARED

## Handlers
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
    """ Create User

    """
    has_changed = False
    try:
      found, user = find_user(client, module)
      if not found:
        resp, message, has_changed = create_user(client, module)
        # if resp["code"] == 200:
        message = 'User Created successfully'

        resp, message, has_changed = mapping_user(client, module, message, has_changed)
        #if resp["code"] == 200:
        message = 'User Created successfully'

      else:
        resp, message, has_changed = update_user_mapping(client, module)
        # if resp["code"] == 200:
        message = 'User Updated successfully'

      found, user = find_user(client, module)
      if found:
        user = {
          "email": module.params.get('email'),
          "roles": user
        }

    except spotinst.SpotinstClientException as e:
      errMsg = get_ExceptionMessage(e)
      module.fail_json(msg="Create Handler1> {}".format(errMsg))

    except Exception as e:
      module.fail_json(msg="Create Handler2> {} {}".format(type(e), e))

    return user, message, has_changed


def handle_delete(client, module):
    """ Delete User

    """
    user = module.params.get('email')
    has_changed = False

    try:
      found, user = find_user(client, module)
      if found:
        resp, message, has_changed = delete_user(client, module)
        if resp["code"] == 200:
          message = 'User Removed successfully'
      else:
        message = 'User {} Not Found'.format(user)
        has_changed = False


    except Exception as e:
      module.fail_json(msg="Error getting Spotinst User mapping: {}".format(e))

    return user, message, has_changed


## Middleaware
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
      err = get_ExceptionMessage(e)
      module.fail_json(msg="{}: {}".format(err["err"], json.dumps(err["payload"])))

    except Exception as e:
      module.fail_json(msg="Error while creating User: {}".format(e))

    return resp, message, has_changed


def delete_user(client, module):

    email = module.params.get('email')
    has_changed = True

    try:
      resp = client.detach_user(email)

      message = "User Detached successfully"

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
          "userEmail": email,
          "accountId": m["account_id"],
          "role": m["role"]
        })

      resp = client.assign_user_to_account(accountUserMapping)
    except Exception as e:
      module.fail_json(msg="Error Mapping User: {}".format(e))

    return resp, message, has_changed


def update_user_mapping(client, module):
    """
    Steps TODO:
    - Get User
    - Compare user mapping in the ver
    - Check if has changes
    - send to mapping_user user ensure that all maps

    Problem using 'update_user_role':
    - if the user is not in the Account, it will fail (It could be an bug).
    ERROR:
      Error encountered while updating user:
      [u'There is no mapping with user teste-01@domain.com and account act-XID.']
    """
    role_mapping = module.params.get('role_mapping')
    email = module.params.get('email')
    message = "Update User mapping is not supported"
    resp = {}
    has_changed = False

    try:
      for m in role_mapping:
        client.account_id = m["account_id"]
        resp = client.update_user_role(email, m["role"])
        has_changed = True
        message = 'User Mapping Updated Successful'

    except spotinst.SpotinstClientException as e:
      errMsg = get_ExceptionMessage(e)
      errors = []
      for er in errMsg["payload"]["errors"]:
        errors.append(er["message"])

      pass

    except Exception as e:
      module.fail_json(msg="Error Updating User Map: {}".format(e))

    return resp, message, has_changed


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
        account_id=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)

    if not HAS_SPOTINST_SDK:
        module.fail_json(msg="the Spotinst SDK library is required. (pip install spotinst_sdk)")

    client = get_client(module=module)

    user, message, has_changed = handle_user(client=client, module=module)

    module.exit_json(changed=has_changed, spotinst_user=user, message=message)


if __name__ == '__main__':
    main()
