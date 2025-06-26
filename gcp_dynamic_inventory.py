#!/usr/bin/env python3

import json
import subprocess
import argparse

def get_gcp_instances():
    """Retrieves a list of GCP instances and their zones."""
    try:
        # Use gcloud to get instance details
        result = subprocess.run(
            ["gcloud", "compute", "instances", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        instances_data = json.loads(result.stdout)

        inventory = {}
        inventory["_meta"] = {"hostvars": {}}
        
        # Create a group for all GCP instances
        inventory["gcp"] = {"hosts": []}

        for instance in instances_data:
            zone = instance["zone"].split("/")[-1]
            instance_name = instance["name"]
            internal_ip = instance["networkInterfaces"][0]["networkIP"]
            external_ip = ""
            if "accessConfigs" in instance["networkInterfaces"][0] and instance["networkInterfaces"][0]["accessConfigs"]:
                external_ip = instance["networkInterfaces"][0]["accessConfigs"][0].get("natIP", "")

            # Add to main GCP group
            inventory["gcp"]["hosts"].append(instance_name)
            
            # Create a group for each zone if it doesn't exist
            if zone not in inventory:
                inventory[zone] = {"hosts": []}

            inventory[zone]["hosts"].append(instance_name)
            
            # Add host variables
            inventory["_meta"]["hostvars"][instance_name] = {
                "ansible_host": internal_ip,
                "gcp_zone": zone,
                "external_ip": external_ip,
                "machine_type": instance["machineType"].split("/")[-1],
                "status": instance["status"]
            }

        return inventory

    except subprocess.CalledProcessError as e:
        print(f"Error executing gcloud command: {e}")
        return {"_meta": {"hostvars": {}}}
    except Exception as e:
        print(f"Error: {e}")
        return {"_meta": {"hostvars": {}}}

def parse_args():
    parser = argparse.ArgumentParser(description='GCP dynamic inventory for Ansible')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='List all hosts')
    group.add_argument('--host', help='Get variables for a specific host')
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.list:
        inventory = get_gcp_instances()
        print(json.dumps(inventory, indent=2))
    elif args.host:
        # When called with --host, we return an empty dict
        # as all host variables are included in the --list output
        print(json.dumps({}))

if __name__ == "__main__":
    main()
