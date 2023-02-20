import netbrain_api_util as nb
import os
import json
from datetime import datetime

print("Delete obsolete devices script start:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")

customer = 'company'

nb_user = os.environ["NB_ID"]
nb_pwd = os.environ["NB_PWD"]       
nb_server_url = "https://netbrain.intra.company.com/ServicesAPI/API"
nb_tenant = "f99bb033-2c09-0c8d-3b3b-851d34340a84"
nb_domain = "45300342-3bb3-4293-b344-1fb63f9bf6ef"


folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', customer)
file_path = os.path.join(folder_path, "devices_for_removal.json")
with open(file_path) as f:
    devices_for_removal = json.load(f)
# type(devices_for_removal) = list

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

print("\nDelete Devices:\n")
print(nb.delete_devices_by_hostname(
    token=token,
    server_url=nb_server_url,
    device_list=devices_for_removal
    ).text)

print("\nLogout:\n")
print(nb.logout(
    token=token,
    server_url=nb_server_url
    ).text)

print("Delete obsolete devices script end:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")