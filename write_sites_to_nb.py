import netbrain_api_util as nb
from functions_exec import nb_assign_devices_to_sites
from datetime import datetime
import json
import os

print("Write sites script start:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")

customer = 'company'

nb_user = os.environ["NB_ID"]
nb_pwd = os.environ["NB_PWD"]      
nb_server_url = "https://netbrain.intra.company.com/ServicesAPI/API"
nb_tenant = "f99bb033-2c09-0c8d-3b3b-851d34340a84"
nb_domain = "45300342-3bb3-4293-b344-1fb63f9bf6ef"


folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', customer)
file_path = os.path.join(folder_path, "site_tree.json")
with open(file_path) as f:
    site_tree_dict = json.load(f)

site_request = {"sites": []}
for site in site_tree_dict["siteTree"]:
    site_request["sites"].append({"sitePath":site['sitePath'], "isContainer":False})


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

print("\nStart Site Transaction:\n")
print(nb.start_site_transaction(
    token=token,
    server_url=nb_server_url
    ).text)

site_path = "My Network/company"
print("\nDelete Existing Sites:\n")
print(nb.delete_site(
    token=token,
    server_url=nb_server_url,
    site_path=site_path
    ).text)

print("\nCreate Sites:\n")
print(nb.create_sites(
    token=token,
    server_url=nb_server_url,
    site_tree=site_request
    ).text)

print("\nAssign Devices to Sites:\n")
folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', customer)
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "log_nb_site_creation.csv")
with open(file_path,'w',  encoding='utf-8') as f:
    f.write(nb_assign_devices_to_sites(
        token=token,
        server_url=nb_server_url,
        site_tree_dict=site_tree_dict
        ))
    

print("\nCommit Site Change:\n")
print(nb.commit_site_change(
    token=token,
    server_url=nb_server_url
    ).text)

print("\nStop Site Transaction:\n")
print(nb.stop_site_transaction(
    token=token,
    server_url=nb_server_url
    ).text)

print("\nLogout:\n")
print(nb.logout(
    token=token,
    server_url=nb_server_url
    ).text)

print("Write sites script end:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")