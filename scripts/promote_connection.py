import requests
import os
import sys
import json
from helper_functions import iics_login, check_ws_return

### Setup environment
LOGIN_URL = os.environ['IICS_LOGIN_URL']
POD_URL =  os.environ['IICS_POD_URL']

IICS_USERNAME = os.environ['IICS_USERNAME']
IICS_PASSWORD = os.environ['IICS_PASSWORD']

CONNECTION_NAME = os.environ['CONNECTION_NAME']
SECRET_LIST = os.environ['SECRET_LIST']

### Login
SESSION_ID = iics_login(LOGIN_URL, IICS_USERNAME, IICS_PASSWORD )

HEADERS_V2 = {"Content-Type": "application/json; charset=utf-8", "icSessionId": SESSION_ID }

### Get connection details
conn = requests.get(POD_URL + "/api/v2/connection/name/" + CONNECTION_NAME, headers = HEADERS_V2)
check_ws_return(conn)

conn_json = conn.json()

### Loop through all secrets for connection and replace params
### TODO: Evaluate what attributes are in connParams vs top level
for secret in SECRET_LIST.split(","):
    secret_value = os.environ[secret]
    secret_json_key = secret[len(CONNECTION_NAME):]
    conn_json['connParams'][secret_json_key] = secret_value


### This part post the connection with replaced variables
UAT_IICS_USERNAME = os.environ['UAT_IICS_USERNAME']
UAT_IICS_PASSWORD = os.environ['UAT_IICS_PASSWORD']

UAT_SESSION_ID = iics_login(LOGIN_URL, UAT_IICS_USERNAME, UAT_IICS_PASSWORD )
UAT_HEADERS_V2 = {"Content-Type": "application/json; charset=utf-8", "icSessionId": UAT_SESSION_ID }

### Need connection id in target to replace
uat_conn = requests.get(POD_URL + "/api/v2/connection/name/" + CONNECTION_NAME, headers = UAT_HEADERS_V2)

### IF connection exists, replace with ID, else create
if uat_conn.status_code == 200:
    uat_conn_json = uat_conn.json()
    conn_post = requests.post(POD_URL + "/api/v2/connection/" + uat_conn_json['id'], headers = UAT_HEADERS_V2, json = conn_json)
    check_ws_return(conn_post)
else:
    conn_post = requests.post(POD_URL + "/api/v2/connection/", headers = UAT_HEADERS_V2, json = conn_json)
    check_ws_return(conn_post)