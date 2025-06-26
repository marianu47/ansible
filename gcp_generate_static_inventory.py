#!/usr/bin/env python3

import json
import subprocess
import argparse
import os
import yaml

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
        return instances_data
    except subprocess.CalledProcessError as e:
        print(f"Error executing gcloud command: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_yaml_inventory(instances_data, output_file):
    """Generate a YAML inventory file from GCP instances data."""
    inventory = {
        'all': {
            'children': {
                'gcp': {
                    'hosts': {},
                    'children': {}
                }
            }
        }
    }
    
    # Process each instance
    for instance in instances_data:
        zone = instance["zone"].split("/")[-1]
        instance_name = instance["name"]
        internal_ip = instance["networkInterfaces"][0]["networkIP"]
        external_ip = ""
        if "accessConfigs" in instance["networkInterfaces"][0] and instance["networkInterfaces"][0]["accessConfigs"]:
            external_ip = instance["networkInterfaces"][0]["accessConfigs"][0].get("natIP", "")
        
        # Add host to inventory
        inventory['all']['children']['gcp']['hosts'][instance_name] = {
            'ansible_host': internal_ip,
            'gcp_zone': zone,
            'external_ip': external_ip,
            'machine_type': instance["machineType"].split("/")[-1],
            'status': instance["status"]
        }
        
        # Create zone group if it doesn't exist
        if zone not in inventory['all']['children']['gcp']['children']:
            inventory['all']['children']['gcp']['children'][zone] = {
                'hosts': {}
            }
        
        # Add host to zone group
        inventory['all']['children']['gcp']['children'][zone]['hosts'][instance_name] = None
    
    # Write to YAML file
    with open(output_file, 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False)
    
    print(f"Inventory file generated: {output_file}")

def generate_ini_inventory(instances_data, output_file):
    """Generate an INI inventory file from GCP instances data."""
    with open(output_file, 'w') as f:
        # Write the gcp group
        f.write("[gcp]\n")
        for instance in instances_data:
            instance_name = instance["name"]
            internal_ip = instance["networkInterfaces"][0]["networkIP"]
            f.write(f"{instance_name} ansible_host={internal_ip}\n")
        f.write("\n")
        
        # Write zone groups
        zones = {}
        for instance in instances_data:
            zone = instance["zone"].split("/")[-1]
            instance_name = instance["name"]
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(instance_name)
        
        for zone, hosts in zones.items():
            f.write(f"[{zone}]\n")
            for host in hosts:
                f.write(f"{host}\n")
            f.write("\n")
        
        # Write host variables
        f.write("[all:vars]\n")
        f.write("ansible_python_interpreter=/usr/bin/python3\n\n")
        
        f.write("[gcp:vars]\n")
        f.write("gcp_project=auto\n\n")
        
        # Write host-specific variables
        for instance in instances_data:
            instance_name = instance["name"]
            zone = instance["zone"].split("/")[-1]
            machine_type = instance["machineType"].split("/")[-1]
            status = instance["status"]
            external_ip = ""
            if "accessConfigs" in instance["networkInterfaces"][0] and instance["networkInterfaces"][0]["accessConfigs"]:
                external_ip = instance["networkInterfaces"][0]["accessConfigs"][0].get("natIP", "")
            
            f.write(f"[{instance_name}:vars]\n")
            f.write(f"gcp_zone={zone}\n")
            f.write(f"machine_type={machine_type}\n")
            f.write(f"status={status}\n")
            if external_ip:
                f.write(f"external_ip={external_ip}\n")
            f.write("\n")
    
    print(f"Inventory file generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate static Ansible inventory from GCP instances')
    parser.add_argument('--format', choices=['yaml', 'ini'], default='yaml', help='Output format (yaml or ini)')
    parser.add_argument('--output', default='inventory', help='Output file name (without extension)')
    args = parser.parse_args()
    
    # Get GCP instances
    instances_data = get_gcp_instances()
    
    if not instances_data:
        print("No instances found or error occurred.")
        return
    
    # Generate inventory file
    output_file = f"{args.output}.{args.format}"
    if args.format == 'yaml':
        generate_yaml_inventory(instances_data, output_file)
    else:
        generate_ini_inventory(instances_data, output_file)

if __name__ == "__main__":
    main()
