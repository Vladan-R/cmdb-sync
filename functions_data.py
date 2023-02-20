import cmdb_api_util as cmdb
import netbrain_api_util as nb
from datetime import datetime
import json

def get_cmdb_sites(endpoint_service_name, method_name, url_parameters, cmdb_username):
    print("Getting page 1 of CMDB sites.\n")
    api_gw_request = cmdb.prepare_request(endpoint_service_name, method_name, url_parameters, cmdb_username)
    cmdb_site_dict = cmdb.get_information(api_gw_request).json()
    number_of_pages = -(-cmdb_site_dict["outputs"]["siteCount"] // 100)
    # -(-x) is for // to round up

    for page_no in range(2,number_of_pages+1):
        print("Getting page {} of CMDB sites.\n".format(str(page_no)))
        api_gw_request = cmdb.prepare_request(endpoint_service_name, method_name, url_parameters + "&pageno=" + str(page_no), cmdb_username)
        cmdb_site_dict["outputs"]["sites"].extend(cmdb.get_information(api_gw_request).json()["outputs"]["sites"])

    return cmdb_site_dict


def get_cmdb_devices(endpoint_service_name, method_name, url_parameters, cmdb_username):
    print("Getting page 1 of CMDB devices.\n")
    api_gw_request = cmdb.prepare_request(endpoint_service_name, method_name, url_parameters, cmdb_username)
    cmdb_device_dict = cmdb.get_information(api_gw_request).json()
    number_of_pages = -(-cmdb_device_dict["outputs"]["count"] // 100)
    # -(-x) is for // to round up

    print("Number of pages for the devices:\n")
    print(str(number_of_pages) + "\n")

    for page_no in range(2,number_of_pages+1):
        print("Getting page {} of CMDB devices.\n".format(str(page_no)))
        api_gw_request = cmdb.prepare_request(endpoint_service_name, method_name, url_parameters + "&pageno=" + str(page_no), cmdb_username)
        cmdb_device_dict["outputs"]["equipmentDetail"].extend(cmdb.get_information(api_gw_request).json()["outputs"]["equipmentDetail"])

    return cmdb_device_dict

def get_nb_devices(user, pwd, server_url, tenant, domain):
    token = nb.get_token(
        user=user,
        pwd=pwd,
        server_url=server_url)
    print("Successfully got NB token: {}\n".format(str(token)))
    nb.set_domain(
        token=token,
        server_url=server_url,
        tenant=tenant,
        domain=domain
    )

    nb_device_dict = nb.get_all_devices(token=token, server_url=server_url).json()

    print("\nLogout:\n")
    print(nb.logout(token=token, server_url=server_url).text)

    return nb_device_dict



def produce_site_tree(cmdb_site_dict, cmdb_device_dict, nb_device_dict):
    logfile = "SITE,CMDB_DEVICE_EQUIPMENT_NAME,CMDB_DEVICE_EQUIPMENT_ALTERNATE_NAME,CMDB_DEVICE_IP,NB_DEVICE_HOSTNAME,NOTE, HOSTNAME_SEARCH_RESULT, IP_OF_FOUND_HOSTNAME\n"
    site_tree = []   

    for site_index, site in enumerate(cmdb_site_dict["outputs"]["sites"]):
        print("Site index: " + str(site_index) + "\n")
        if site["siteType"] == "Data Center":
            site_type = "Datacenter"
        else:
            site_type = "Branch"
        site_tree.append({
            "sitePath": "My Network/company/{site_type}/{country}/{city}/{address} @ {site_id}".format(
                site_type=site_type,
                country=site["country"].title(),
                city=site["city"].title(),
                address=site["addressLine1"].replace("/", "-").upper(),
                site_id=site["siteId"]
                ),
            "Devices": []
        })
        per_site_nb_devices_hostnames = []

        # START > get all devices per site #
        for device in [cmdb_device for cmdb_device in cmdb_device_dict["outputs"]["equipmentDetail"] if cmdb_device.get("siteId", "NOT_SPECIFIED") == site["siteId"]]:
            #print("Getting NB hostname for device {}.".format(device["equipmentName"]))
            nb_per_ip_devices = [nb_device for nb_device in nb_device_dict["devices"] if nb_device["mgmtIP"] == device.get("ipv4Address", "NOT_SPECIFIED")]
            nb_per_hostname_devices = [nb_device for nb_device in nb_device_dict["devices"] if nb_device["hostname"].lower() in (device["equipmentName"].lower(), device.get("equipmentAlternateName", "unspecified_alternate_name").lower())]
            if len(nb_per_ip_devices) == 1:
                per_site_nb_devices_hostnames.append(nb_per_ip_devices[0]["hostname"])
                logfile += "{site},{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{nb_device_hostname},{note},{hostname_search_result},{ip_of_found_hostname}\n".format(
                    site='"' + site_tree[site_index]["sitePath"] + '"',
                    cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                    cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                    cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                    nb_device_hostname='"' + nb_per_ip_devices[0]["hostname"] + '"',
                    note='"Finding device with this CMDB IP in NetBrain SUCCEEDED (returned one result)."',
                    hostname_search_result='""',
                    ip_of_found_hostname='""'
                )
            elif len(nb_per_ip_devices) == 0 and len(nb_per_hostname_devices) == 0:
                logfile += "{site},{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{nb_device_hostname},{note},{hostname_search_result},{ip_of_found_hostname}\n".format(
                    site='"' + site_tree[site_index]["sitePath"] + '"',
                    cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                    cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                    cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                    nb_device_hostname='""',
                    note='"Finding device with this CMDB IP in NetBrain FAILED (returned zero results)."',
                    hostname_search_result='""',
                    ip_of_found_hostname='""'
                )
            elif len(nb_per_ip_devices) == 0 and len(nb_per_hostname_devices) > 0:
                per_site_nb_devices_hostnames.append(nb_per_hostname_devices[0]["hostname"])
                # above line has been added to make the site assignment logic more "aggressive"
                # if the plan is to examine whether the data in CMDB is correct and fix it, I would suggest to omit this line
                # if the plan is to not worry about quality of CMDB data, this line can work around missing CMDB MGMT IP's or mismatches between MGTM IP's in CMDB and NB
                logfile += "{site},{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{nb_device_hostname},{note},{hostname_search_result},{ip_of_found_hostname}\n".format(
                    site='"' + site_tree[site_index]["sitePath"] + '"',
                    cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                    cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                    cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                    nb_device_hostname='""',
                    note='"Finding device with this CMDB IP in NetBrain FAILED (returned zero results)."',
                    hostname_search_result='"' + nb_per_hostname_devices[0]["hostname"] + '"',
                    ip_of_found_hostname='"' + nb_per_hostname_devices[0]["mgmtIP"] + '"'
                )
            else:
                for i, found_device in enumerate(nb_per_ip_devices):
                    if found_device["hostname"].lower() in (device["equipmentName"].lower(), device.get("equipmentAlternateName", "unspecified_alternate_name").lower()):
                        per_site_nb_devices_hostnames.append(nb_per_ip_devices[i]["hostname"])
                        logfile += "{site},{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{nb_device_hostname},{note},{hostname_search_result},{ip_of_found_hostname}\n".format(
                            site='"' + site_tree[site_index]["sitePath"] + '"',
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            nb_device_hostname='"' + nb_per_ip_devices[i]["hostname"] + '"',
                            note='"Finding device with this CMDB IP in NetBrain SUCCEEDED with MULTIPLE RESULTS (this hostname matched)."',
                            hostname_search_result='""',
                            ip_of_found_hostname='""'
                        )
                    else:
                        per_site_nb_devices_hostnames.append(nb_per_ip_devices[i]["hostname"])
                        logfile += "{site},{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{nb_device_hostname},{note},{hostname_search_result},{ip_of_found_hostname}\n".format(
                            site='"' + site_tree[site_index]["sitePath"] + '"',
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            nb_device_hostname='"' + nb_per_ip_devices[i]["hostname"] + '"',
                            note='"Finding device with this CMDB IP in NetBrain SUCCEEDED with MULTIPLE RESULTS (this hostname did not match)."',
                            hostname_search_result='""',
                            ip_of_found_hostname='""'
                        )
            site_tree[site_index]["Devices"] = per_site_nb_devices_hostnames
    # END > get all devices per site #
    site_tree_filtered = [leaf_site for leaf_site in site_tree if len(leaf_site["Devices"]) > 0]

    return (site_tree_filtered, logfile)

def devices_for_removal_cmdb_based(cmdb_device_dict_obsolete, cmdb_device_dict_production, nb_device_dict):
    logfile = "CMDB_DEVICE_EQUIPMENT_NAME,CMDB_DEVICE_EQUIPMENT_ALTERNATE_NAME,CMDB_DEVICE_IP,FOUND_IN_NB,NB_DEVICE_HOSTNAME,NB_DEVICE_IP,MARKED_FOR_DELETION,NOTE,CMDB_IN_SERVICE_DATE, CMDB_OUT_OF_SERVICE_DATE\n"
    nb_marked_for_removal = []
    for device in cmdb_device_dict_obsolete["outputs"]["equipmentDetail"]:
        nb_per_hostname_devices = [nb_device for nb_device in nb_device_dict["devices"] if nb_device["hostname"].lower() in (device["equipmentName"].replace('_DEL','').lower(), device.get("equipmentAlternateName", "unspecified_alternate_name").replace('_DEL','').lower())]
        cmdb_per_hostname_devices = [cmdb_device for cmdb_device in cmdb_device_dict_production["outputs"]["equipmentDetail"] if cmdb_device["equipmentName"].lower() == device["equipmentName"].replace('_DEL','').lower()]
        if len(nb_per_hostname_devices) == 0:
            logfile += "{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{found_in_nb},{nb_device_hostname},{nb_device_ip},{marked_for_deletion},{note},{cmdb_in_service_date},{cmdb_out_of_service_date}\n".format(
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            found_in_nb='"NO"',
                            nb_device_hostname='"N/A"',
                            nb_device_ip='"N/A"',
                            marked_for_deletion='"N/A"',
                            note='""',
                            cmdb_in_service_date='"' + device.get("inProdDate", "NOT_SPECIFIED") + '"',
                            cmdb_out_of_service_date='"' + device.get("outOfProdDate", "NOT_SPECIFIED") + '"'
                        )
        elif len(nb_per_hostname_devices) == 1 and len(cmdb_per_hostname_devices) == 0:
            nb_marked_for_removal.append(nb_per_hostname_devices[0]["hostname"])
            logfile += "{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{found_in_nb},{nb_device_hostname},{nb_device_ip},{marked_for_deletion},{note},{cmdb_in_service_date},{cmdb_out_of_service_date}\n".format(
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            found_in_nb='"YES"',
                            nb_device_hostname='"' + nb_per_hostname_devices[0]["hostname"] + '"',
                            nb_device_ip='"' + nb_per_hostname_devices[0]["mgmtIP"] + '"',
                            marked_for_deletion='"YES"',
                            note='""',
                            cmdb_in_service_date='"' + device.get("inProdDate", "NOT_SPECIFIED") + '"',
                            cmdb_out_of_service_date='"' + device.get("outOfProdDate", "NOT_SPECIFIED") + '"'
                        )
        elif len(nb_per_hostname_devices) == 1 and len(cmdb_per_hostname_devices) > 0:
            logfile += "{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{found_in_nb},{nb_device_hostname},{nb_device_ip},{marked_for_deletion},{note},{cmdb_in_service_date},{cmdb_out_of_service_date}\n".format(
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            found_in_nb="YES",
                            nb_device_hostname='"' + nb_per_hostname_devices[0]["hostname"] + '"',
                            nb_device_ip='"' + nb_per_hostname_devices[0]["mgmtIP"] + '"',
                            marked_for_deletion='"NO"',
                            note='"Hostname matches a production device in CMDB"',
                            cmdb_in_service_date='"' + device.get("inProdDate", "NOT_SPECIFIED") + '"',
                            cmdb_out_of_service_date='"' + device.get("outOfProdDate", "NOT_SPECIFIED") + '"'
                        )
        else:
            logfile += "{cmdb_device_equipment_name},{cmdb_device_equipment_alternate_name},{cmdb_device_ip},{found_in_nb},{nb_device_hostname},{nb_device_ip},{marked_for_deletion},{note},{cmdb_in_service_date},{cmdb_out_of_service_date}\n".format(
                            cmdb_device_equipment_name='"' + device["equipmentName"] + '"',
                            cmdb_device_equipment_alternate_name='"' + device.get("equipmentAlternateName", "unspecified_alternate_name") + '"',
                            cmdb_device_ip='"' + device.get("ipv4Address", "NOT_SPECIFIED") + '"',
                            found_in_nb="YES",
                            nb_device_hostname='"_multiple_results_"',
                            nb_device_ip='"_multiple_results_"',
                            marked_for_deletion='"NO"',
                            note='"Multiple hostnames found in NetBrain"',
                            cmdb_in_service_date='"' + device.get("inProdDate", "NOT_SPECIFIED") + '"',
                            cmdb_out_of_service_date='"' + device.get("outOfProdDate", "NOT_SPECIFIED") + '"'
                        )
    return (nb_marked_for_removal, logfile)

def devices_for_removal_time_based(nb_device_dict):
    logfile = "HOSTNAME,MGMT_IP,TYPE,FIRST_DISCOVERY,LAST_DISCOVERY\n"
    nb_marked_for_removal = []
    for device in [nb_device for nb_device in nb_device_dict["devices"] if (datetime.today() - datetime.strptime(nb_device["lastDiscoverTime"][:19], '%Y-%m-%dT%H:%M:%S')).days > 31 + datetime.today().weekday()]:
        #[:19] in above list comprehension is because of missing "Z" at the end of MPLS cloud lastDiscoverTime which has "0001-01-01T00:00:00"
        nb_marked_for_removal.append(device["hostname"])
        logfile += "{hostname},{mgmt_ip},{type},{first_discovery_time},{last_discovery_time}\n".format(
            hostname = '"' + device["hostname"] + '"',
            mgmt_ip = '"' + device["mgmtIP"] + '"',
            type = '"' + device["deviceTypeName"] + '"',
            first_discovery_time = '"' + device["firstDiscoverTime"] + '"',
            last_discovery_time = '"' + device["lastDiscoverTime"] + '"'
        )
    return (nb_marked_for_removal, logfile)