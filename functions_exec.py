import netbrain_api_util as nb
import json

def nb_assign_devices_to_sites(token, server_url, site_tree_dict):
    logfile = "SITE,STATUS_CODE,STATUS_DESCRIPTION\n"
    for i, site in enumerate(site_tree_dict["siteTree"]):
        print("Site " + str(i) + ".\n")
        try:
            result_dict = nb.add_devices_to_site(
                token=token,
                server_url=server_url,
                site_devices=site
                ).json()
        except:
            logfile += "{site},{device_add_result},{status_description}\n".format(
                    site='"' + site["sitePath"] + '"',
                    device_add_result='"' + 'DID NOT GET VALID RESPONSE' + '"',
                    status_description='"' + 'DID NOT GET VALID RESPONSE' + '"'
                )
        else:
            logfile += "{site},{device_add_result},{status_description}\n".format(
                        site='"' + site["sitePath"] + '"',
                        device_add_result='"' + str(result_dict.get("statusCode", "no status code returned")) + '"',
                        status_description='"' + result_dict.get("statusDescription", "no status description returned") + '"'
                    )
    return logfile