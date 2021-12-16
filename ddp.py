import time
import requests
import json
import datetime
import pytz

token='TBD'
header = {"Content-Type": "application/json"}

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

def start():
    createjob = { "image": "ovhcom/ai-training-pytorch" }
    datain = '''{
      "image": "ovhcom/ai-training-pytorch",
      "name": "funny-ddp",
      "resources": {
         "cpu": 1
       },
       "shutdown": "Stop",
       "timeout": 0
    }'''

    url = "https://gra.training.ai.cloud.ovh.net/v1/job"
    response = requests.post(url, data=datain, headers=header, auth=BearerAuth(token))
    if response.status_code == 200:
       project = response.json()
       print(project["status"]["state"])
       idprimary=project["id"]
       return idprimary
    else:
       print("Error soumission job", response.json(), response.status_code)

def is_not_running(id):
  url = "https://gra.training.ai.cloud.ovh.net/v1/job/"+id
  response = requests.get(url, auth=BearerAuth(token))
  if response.status_code == 200:
     project = response.json()
     status=project["status"]["state"]
     return status == "RUNNING"
  else:
     print("Error get job", response.json(), response.status_code)
     return False
  return False

def get_private_ip(id):
  url = "https://gra.training.ai.cloud.ovh.net/v1/job/"+id
  response = requests.get(url, auth=BearerAuth(token))
  if response.status_code == 200:
     resp = response.json()
     return resp["status"]["ip"]
  else:
     print("Erreur get job", response.json(), response.status_code)
     return "0"
  return "0"

def send_command_container(id, command):
  url = "https://gra.training.ai.cloud.ovh.net/v1/job/"+id+"/exec"
  response = requests.get(url, auth=BearerAuth(token))
  if response.status_code == 200:
     resp = response.json()
     return resp["status"]["ip"]
  else:
     print("Error get job", response.json(), response.status_code)
     return "0"
  return "0"

def stop(id):
  url = "https://gra.training.ai.cloud.ovh.net/v1/job/"+id+"/kill"
  response = requests.put(url, auth=BearerAuth(token))
  if response.status_code == 200:
     resp = response.json()
     print("Killed: ", resp["id"])
  else:
     print("Error kill job", response.json(), response.status_code)


primaryid=start()
print("Primary starting")
while not (is_not_running(primaryid)):
     time.sleep(1)
     print("Waiting Primary Creation...")
primaryip=get_private_ip(primaryid)

print("Primary private ip", primaryip)
primarynode=f"python -m torch.distributed.launch --nproc_per_node=2 --nnodes=2 --node_rank=0 --master_addr {primaryip} --master_port 5555 experiment.py hyperparams.yaml --distributed_launch --distributed_backend='nccl'"
stop(primaryid)
