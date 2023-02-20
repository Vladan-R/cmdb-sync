import os
import json
from functions_data import get_cmdb_sites, get_cmdb_devices, get_nb_devices, produce_site_tree, devices_for_removal_cmdb_based, devices_for_removal_time_based
from datetime import datetime

print("Data gathering script start:")
print(datetime.now().strftime("%H:%M:%S") +"\n\n")

customer = "company"

cmdb_username = os.environ["CMDB_USER"]

nb_user = os.environ["NB_ID"]
nb_pwd = os.environ["NB_PWD"]
nb_server_url = "https://netbrain.intra.company.com/ServicesAPI/API"
nb_tenant = "f99bb033-2c09-0c8d-3b3b-851d34340a84"
nb_domain = "45300342-3bb3-4293-b344-1fb63f9bf6ef"


cmdb_url_parameters = "custid=GOKNR&status=Production"
cmdb_endpoint_service_name = "company.cmdb.geo"
cmdb_method_name =  "sites"
cmdb_site_dict = get_cmdb_sites(
            endpoint_service_name=cmdb_endpoint_service_name,
            method_name=cmdb_method_name,
            url_parameters=cmdb_url_parameters,
            cmdb_username=cmdb_username
            )

cmdb_url_parameters = "custid=GOKNR&status=Production&main=1"
cmdb_endpoint_service_name = "company.cmdb.equipment"
cmdb_method_name =  "deviceDetails"
cmdb_device_dict_production = get_cmdb_devices(
            endpoint_service_name=cmdb_endpoint_service_name,
            method_name=cmdb_method_name,
            url_parameters=cmdb_url_parameters,
            cmdb_username=cmdb_username
            )

cmdb_url_parameters = "custid=GOKNR&status=Obsolete&main=1"
cmdb_device_dict_obsolete = get_cmdb_devices(
            endpoint_service_name=cmdb_endpoint_service_name,
            method_name=cmdb_method_name,
            url_parameters=cmdb_url_parameters,
            cmdb_username=cmdb_username
            )

nb_device_dict = get_nb_devices(
            user=nb_user,
            pwd=nb_pwd,
            server_url=nb_server_url,
            tenant=nb_tenant,
            domain=nb_domain
            )

site_tree_result = produce_site_tree(
            cmdb_site_dict=cmdb_site_dict,
            cmdb_device_dict=cmdb_device_dict_production,
            nb_device_dict=nb_device_dict
            )

removal_result_cmdb_based = devices_for_removal_cmdb_based(
            cmdb_device_dict_obsolete=cmdb_device_dict_obsolete,
            cmdb_device_dict_production=cmdb_device_dict_production,
            nb_device_dict=nb_device_dict
            )

removal_result_time_based = devices_for_removal_time_based(
            nb_device_dict=nb_device_dict
            )
# remove devices that has not been rediscovered for more than a month

folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', customer)
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "cmdb_sites.json")
with open(file_path,'w') as f:
    json.dump(cmdb_site_dict, f)

file_path = os.path.join(folder_path, "cmdb_devices_production.json")
with open(file_path,'w') as f:
    json.dump(cmdb_device_dict_production, f)

file_path = os.path.join(folder_path, "cmdb_devices_obsolete.json")
with open(file_path,'w') as f:
    json.dump(cmdb_device_dict_obsolete, f)

file_path = os.path.join(folder_path, "nb_devices.json")
with open(file_path,'w') as f:
    json.dump(nb_device_dict, f)

file_path = os.path.join(folder_path, "site_tree.json")
with open(file_path,'w') as f:
    json.dump({"siteTree": site_tree_result[0]}, f)

file_path = os.path.join(folder_path, "devices_for_removal.json")
with open(file_path,'w') as f:
    json.dump(removal_result_cmdb_based[0] + removal_result_time_based[0], f)

folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', customer)
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "log_data_gathering.csv")
with open(file_path,'w',  encoding='utf-8') as f:
    f.write(site_tree_result[1])

folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', customer, "devices_for_removal")
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "log_devices_for_removal_cmdb_based_{timestamp}.csv".format(timestamp=datetime.now().strftime("%Y_%m_%d_%H_%M")))
with open(file_path,'w',  encoding='utf-8') as f:
    f.write(removal_result_cmdb_based[1])
file_path = os.path.join(folder_path, "log_devices_for_removal_time_based_{timestamp}.csv".format(timestamp=datetime.now().strftime("%Y_%m_%d_%H_%M")))
with open(file_path,'w',  encoding='utf-8') as f:
    f.write(removal_result_time_based[1])

print("Data gathering script end:")
print(datetime.now().strftime("%H:%M:%S") + "\n")