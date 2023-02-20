import requests
import tenacity
import json
import base64

headers = {"Content-Type": "application/json", "Accept": "application/json"}

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_token(user, pwd, server_url):   
    target_url= server_url + "/V1/Session"
    return requests.post(target_url,
        headers=headers,
        json={
            "username": user,
            "password": pwd
        },
        verify=False).json()["token"]

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def logout(token, server_url):
    target_url= server_url + "/V1/Session"
    return requests.delete(target_url,
        headers=headers,
        json={
            "token": token,
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def set_domain(token, server_url, tenant, domain):
    target_url= server_url + "/V1/Session/CurrentDomain"
    headers["token"] = token
    return requests.put(target_url,
        headers=headers,
        json={
            "tenantId": tenant,
            "domainId": domain
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_site_info(token, server_url, site_path):
    target_url= server_url + "/V1/CMDB/Sites/SiteInfo"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        params={
            "sitePath": site_path
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_child_sites_of_a_site(token, server_url, site_path):
    target_url= server_url + "/V1/CMDB/Sites/ChildSites"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        params={
            "sitePath": site_path
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def start_site_transaction(token, server_url):
    target_url= server_url + "/V1/CMDB/Sites/Transactions"
    headers["token"] = token
    return requests.post(target_url,
        headers=headers,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def stop_site_transaction(token, server_url):
    target_url= server_url + "/V1/CMDB/Sites/Transactions"
    headers["token"] = token
    return requests.delete(target_url,
        headers=headers,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def delete_site(token, server_url, site_path):
    target_url= server_url + "/V1/CMDB/Sites"
    headers["token"] = token
    return requests.delete(target_url,
        headers=headers,
        params={
            "sitePath": site_path
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def create_leaf_site(token, server_url, site_path):
    target_url= server_url + "/V1/CMDB/Sites/Leaf"
    headers["token"] = token
    return requests.post(target_url,
        headers=headers,
        json={
            "sitePath": site_path
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def create_sites(token, server_url, site_tree):
    target_url= server_url + "/V1/CMDB/Sites"
    headers["token"] = token
    return requests.post(target_url,
        headers=headers,
        json=site_tree,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def add_devices_to_site(token, server_url, site_devices):
    target_url= server_url + "/V1/CMDB/Sites/Devices"
    headers["token"] = token
    return requests.post(target_url,
        headers=headers,
        json=site_devices,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def commit_site_change(token, server_url):
    target_url= server_url + "/V1/CMDB/Sites/Transactions"
    headers["token"] = token
    return requests.put(target_url,
        headers=headers,
        json={
            "rebuildSite": True
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_tenants(token, server_url):
    target_url= server_url + "/V1/CMDB/Tenants"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_domains(token, server_url, tenant):
    target_url= server_url + "/V1/CMDB/Domains"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        params={
            "tenantId": tenant
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_devices_by_ip(token, server_url, ip):
    target_url= server_url + "/V1/CMDB/Devices"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        params={
            "ip": ip
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_all_devices(token, server_url):
    target_url= server_url + "/V1/CMDB/Devices"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def delete_devices_by_hostname(token, server_url, device_list):
    target_url= server_url + "/V1/CMDB/Devices"
    headers["token"] = token
    return requests.delete(target_url,
        headers=headers,
        json={
            "hostnames": device_list,
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_oneip_table_entries(token, server_url, begin_index, count):
    target_url= server_url + "/V1/CMDB/Topology/OneIPTable"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        params={
            "beginIndex": begin_index,
            "count": count
        },
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_discovery_tasks(token, server_url):
    target_url= server_url + "/V1/CMDB/Discovery/Tasks"
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def add_ips_to_discovery_task(token, server_url, task_id, ips):
    target_url= server_url + "/V1/CMDB/Discovery/Tasks/{}/Seeds".format(task_id)
    headers["token"] = token
    return requests.post(target_url,
        headers=headers,
        json=ips,
        verify=False)

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_ips_in_discovery_task(token, server_url, task_id):
    target_url= server_url + "/V1/CMDB/Discovery/Tasks/{}/Seeds".format(task_id)
    headers["token"] = token
    return requests.get(target_url,
        headers=headers,
        verify=False)