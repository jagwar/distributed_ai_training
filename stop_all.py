import time
import requests
import json
import datetime
import pytz

token = 'TBD'
header = {"Content-Type": "application/json"}
region = 'gra'
url = f"https://{region}.training.ai.cloud.ovh.net/v1/job"


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r

    
def get_job(id=None) -> bool:
    response = requests.get(f"{url}/{id}", auth=BearerAuth(token))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting job", response.json(), response.status_code)
        return False

def get_all_running_job(id=None) -> str:
    response = requests.get(f"{url}?statusState=RUNNING", auth=BearerAuth(token))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting job", response.json(), response.status_code)
        return ""

def stop(id):
  this_url = f"{url}/{id}/kill"
  response = requests.put(this_url, auth=BearerAuth(token))
  if response.status_code == 200:
     resp = response.json()
     print("Killed: ", resp["id"])
  else:
     print("Error killing job", response.json(), response.status_code)

listjob=get_all_running_job()
#Stop all running jobs
for job in listjob["items"]:
    print("Stopping:", job["id"])
    stop(job["id"])

