# Ansible GCP Demo project
Designed to be ran in gcloud shell as Owner of a project and it creates:
- VPC
- Subnet
- SSH Firewall Rule
- Cloud Router
- Public Nat Gateway
- Compute Instances:
    - Ansible Controller
    - Ansible Managed Nodes
 
Provides example of static ini inventory and static yaml inventory.

Note: the startup script requires some optimization in order to copy the private key only to Ansible Controller
