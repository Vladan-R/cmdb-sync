import requests
import tenacity
import base64
import os

def prepare_request(endpoint_service_name, method_name, url_parameters, cmdb_username):
    """
    ----------------------
     SITES
    ----------------------
     endpoint_service_name = "company.cmdb.geo"
     method_name =  "sites"
    ----------------------
     DEVICES
    ----------------------
     endpoint_service_name = "company.cmdb.equipment"
     method_name =  "deviceDetails"
    ----------------------
     PAGINATION PARAMETERS
    ----------------------
     pagesize=50 --> page size (how many results per page)
     pageno=5000 --> page number (which page to get)
    """
    return {
            "env": "PROD",
            "epServiceName": endpoint_service_name,
            "method": method_name,
            "auth": {
                "usr": os.environ["APIGW_ID"],
                "cred": {
                    "password": os.environ["APIGW_PWD"]
                }
            },
            "inputs": {
                "urlParameters": [
                    {
                        "name": "urlParameters",
                        "value": url_parameters
                    },
                    {
                        "name": "env",
                        "value": "PROD"
                    },
                ],
                "httpHeaders": [
                    {
                        "name": "X-Cmpn-OriginId",
                        "value": cmdb_username
                    }
                ]
            }
        }

@tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(5))
def get_information(api_gw_request):
    return requests.post('https://apigw.web.company.com/svcs/apigw',
        json=api_gw_request,
        headers={
            'Authorization': base64.b64encode("{}:{}".format(os.environ["APIGW_ID"],os.environ["APIGW_PWD"]).encode('ascii')).decode('ascii'),
            'Content-type': 'application/json'
            },
        verify=False)