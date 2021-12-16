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

    
def get_job(id=None) -> Any:
    response = requests.get(f"{url}/{id}", auth=BearerAuth(token))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting job", response.json(), response.status_code)
        return False
    
    
def start_primary_node() -> Any:
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

    response = requests.post(url, data=datain, headers=header, auth=BearerAuth(token))
    if response.status_code == 200:
       project = response.json()
       print(project["status"]["state"])
       idprimary=project["id"]
       return idprimary
    else:
       print("Error soumission job", response.json(), response.status_code)

    
def is_not_running(id) -> Any:
  if not get_job(id):
       return False
  else:
       return get_job(id)["status"]["state"] == 'RUNNING'

    
def get_private_ip(id) -> string:
 if not get_job(id):
       return "0"
  else:
       return get_job(id)["status"]["ip"]
    
def send_command_container(id, command) -> Any:
  this_url = f"{url}/{id}/exec?command={command}&stderr=true&stdout=true&stdin=false&tty=false"
  response = requests.get(this_url, auth=BearerAuth(token))

  if response.status_code == 200:
     return response.json()
  else:
     print("Error running command in container", response.json(), response.status_code)
     return False

def stop(id):
  this_url = f"{url}/{id}/kill"
  response = requests.put(url, auth=BearerAuth(token))
  if response.status_code == 200:
     resp = response.json()
     print("Killed: ", resp["id"])
  else:
     print("Error killing job", response.json(), response.status_code)

        
        
primaryid=start_primary_node()
print("Primary Node starting")
while not (is_not_running(primaryid)):
     time.sleep(1)
     print("Waiting Primary Node Creation ...")

primaryip=get_private_ip(primaryid)

print(f"Primary private ip: {primaryip}")
primarynode_cmd=f"python -m torch.distributed.launch --nproc_per_node=2 --nnodes=2 --node_rank=0 --master_addr {primaryip} --master_port 5555 experiment.py hyperparams.yaml --distributed_launch --distributed_backend='nccl'"

cmd_output = send_command_container(primaryid, primarynode_cmd)
print(cmd_output)
stop_container(primaryid)
