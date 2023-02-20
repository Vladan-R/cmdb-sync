# CMDB NB Sync Automation

Python version used: 3.8.1

Python libraries: requirements.txt

This version of the program is intended to be run from command line.

## Recommended script order for one sync run

### 1. data_gathering.py
###### gathers below data from CMDB
  * all "Production" devices of the customer \[./data/\<customer\>/cmdb_devices_production.json\]
  * all "Obsolete" devices of the customer \[./data/\<customer\>/cmdb_devices_obsolete.json\]
  * all "Operational" sites of the customer \[./data/\<customer\>/cmdb_sites.json\]

###### gathers below data from NetBrain
  * all devices \[./data/nb_devices.json\]

###### produces below data structures based on the data above:
  * formatted NetBrain site tree \[./data/\<customer\>/site_tree.json\]
  * formatted list of devices to remove from NetBrain \[./data/\<customer\>/devices_for_removal.json\]
  * the above devices_for_removal.json contains devices that are a) obsolete according to CMDB b) their last discovery time is more than one month

###### produces logfiles
  * data analysis on mismatches between CMDB and NetBrain \[./log/\<customer\>/log_data_gathering.csv\]
  * data analysis done to produce removal list based on CMDB \[./log/\<customer\>/devices_for_removal/log_devices_for_removal_cmdb_based\<timestamp\>.csv\]
  * time based data analysis done to produce removal list based on last discovery time \[./log/\<customer\>/devices_for_removal/log_devices_for_removal_time_based\<timestamp\>.csv\]

### 2. write_sites_to_nb.py
  * deletes current site tree
  * builds new site tree from scratch based on site_tree.json
  * produces log of this activity \[./log/\<customer\>/log_nb_site_creation.csv\]

### 3. delete_obsolete_devices.py
  * removes the devices specified in devices_for_removal.json from NetBrain

### 4. discovery_cmdb_based.py
  * takes all devices in cmdb_devices_production.json and adds their IP's to a pre-made scheduled discovery task
  * this ensures that all devices that are added to CMDB are discovered by NetBrain
  * without this feature, it is likely that some of the new devices wouldn't be discovered by NetBrain auto-discovery depending on discovery depth