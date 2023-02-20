import netbrain_api_util as nb
import os
import json
import ipaddress
from datetime import datetime


def isvalidip(ip_string):
    try:
        ipaddress.ip_address(ip_string)
    except:
        return False
    else:
        return True


print("CMDB based discovery script start:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")

customer = 'company'

nb_user = os.environ["NB_ID"]
nb_pwd = os.environ["NB_PWD"]       
nb_server_url = "https://netbrain.intra.company.com/ServicesAPI/API"
nb_tenant = "f99bb033-2c09-0c8d-3b3b-851d34340a84"
nb_domain = "45300342-3bb3-4293-b344-1fb63f9bf6ef"
cmdb_discovery_task = "6481cdcd-c0e3-40f0-f193-38206255dbdd"


folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', customer)
file_path = os.path.join(folder_path, "cmdb_devices_production.json")
with open(file_path) as f:
    cmdb_devices = json.load(f)


ip_dict = {
            "seeds": [
                {
                    "mgmtIP": device.get("ipv4Address", "NOT_SPECIFIED")
                } for device in cmdb_devices["outputs"]["assetDetail"] if isvalidip(device.get("ipv4Address", "NOT_SPECIFIED"))
            ]
        }


token = nb.get_token(
        user=nb_user,
        pwd=nb_pwd,
        server_url=nb_server_url)
print("Token: " + str(token))

print("\nSet Domain:\n")
print(nb.set_domain(
        token=token,
        server_url=nb_server_url,
        tenant=nb_tenant,
        domain=nb_domain
    ).text)

print("\nAdd IPs to discovery task:\n")
print(nb.add_ips_to_discovery_task(
    token=token,
    server_url=nb_server_url,
    task_id=cmdb_discovery_task,
    ips=ip_dict).text)

print("\nLogout:\n")
print(nb.logout(
    token=token,
    server_url=nb_server_url
    ).text)

print("CMDB based discovery script end:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")