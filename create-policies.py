import requests
import sys
import json
import os
import logging
import yaml
from jinja2 import Template
import pprint

from vmanage.apps.files import Files
from vmanage.api.authentication import Authentication

from logging.handlers import TimedRotatingFileHandler
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings()

def get_logger(logfile, level):
    '''
    Create a logger
    '''
    if logfile is not None:

        '''
        Create the log directory if it doesn't exist
        '''

        fldr = os.path.dirname(logfile)
        if not os.path.exists(fldr):
            os.makedirs(fldr)

        logger = logging.getLogger()
        logger.setLevel(level)
 
        log_format = '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(lineno)-3d | %(message)s'
        formatter = logging.Formatter(log_format)
 
        file_handler = TimedRotatingFileHandler(logfile, when='midnight', backupCount=7)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        return logger

    return None


if __name__ == '__main__':

    try:

        log_level = logging.DEBUG
        logger = get_logger("log/create_policies.txt", log_level)

        if logger is not None:
            logger.info("Loading vManage login details from YAML\n")
        with open("config_details.yaml") as f:
            config = yaml.safe_load(f.read())

        policy_variables = dict()
        vmanage_host = config["vmanage_host"]
        vmanage_port = config["vmanage_port"]
        username = config["vmanage_username"]
        password = config["vmanage_password"]

        policy_variables["DC1_site_id"] = config["DC1_site_id"]
        policy_variables["DC2_site_id"] = config["DC2_site_id"]
        policy_variables["Spokes_site_id"] = config["Spokes_site_id"]
        policy_variables["Service_VPNs"] = config["Service_VPNs"]
        
        policy_variables["AAR_site_ids"] = config["AAR_site_ids"]
        policy_variables["Latency"] = config["Latency"]
        policy_variables["Loss"] = config["Loss"]
        policy_variables["Jitter"] = config["Jitter"]
        policy_variables["pref_color"] = config["pref_color"]
        policy_variables["backup_pref_color"] = config["backup_pref_color"]       

        pp = pprint.PrettyPrinter(indent=2)

        session = Authentication(host=vmanage_host, port=vmanage_port, user=username, password=password).login()

        with open("sdwanlab.j2") as f:
            policy_template = Template(f.read())

        policy_def = policy_template.render(config=policy_variables)

        with open("sdwanlab_temp.json", "w") as f:
            f.write(policy_def)

        vmanage_files = Files(session,vmanage_host)
        

        result = vmanage_files.import_policy_from_file("sdwanlab_temp.json", update=True)

        print(f"Policy List Updates: {len(result['policy_list_updates'])}")
        print(f"Policy Definition Updates: {len(result['policy_definition_updates'])}")
        print(f"Central Policy Updates: {len(result['central_policy_updates'])}")
        print(f"Local Policy Updates: {len(result['local_policy_updates'])}")

        os.remove("sdwanlab_temp.json")

    except Exception as e:
        print('Exception line number: {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

           