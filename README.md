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

Note: 
  - the startup script requires some optimization in order to copy the private key only to Ansible Controller
  - to expose VMs through a public load balancer (only NLB Passthrough works):

VM=your-VM-name

REGION=your-VM-region

ZONE=your-VM-zone

VPC=your-VM-name

gcloud compute addresses create ssh-nlb-ip   --region=${REGION}

gcloud compute instance-groups unmanaged create ssh-nlb-group   --zone=${REGION}

gcloud compute instance-groups unmanaged add-instances ssh-nlb-group   --instances=${VM}  --zone=${ZONE}

gcloud compute health-checks create tcp ssh-nlb-hc   --region=${REGION}   --port=22

gcloud compute backend-services create ssh-nlb-backend   --load-balancing-scheme=EXTERNAL   --protocol=TCP   --region=${REGION}   --health-checks=ssh-nlb-hc   --health-checks-region=${REGION}

gcloud compute backend-services add-backend ssh-nlb-backend   --instance-group=ssh-nlb-group   --instance-group-zone=${ZONE}   --region=${REGION}

gcloud compute forwarding-rules create ssh-nlb-fr   --region=${REGION}   --address=ssh-nlb-ip   --ports=22   --backend-service=ssh-nlb-backend   --backend-service-region=${REGION}   --load-balancing-scheme=EXTERNAL   --ip-protocol=TCP

gcloud compute firewall-rules create allow-ssh-nlb   --network=${VPC}   --allow=tcp:22   --source-ranges=0.0.0.0/0   --target-tags=ssh-nlb

gcloud compute instances add-tags ${VM}   --tags=ssh-nlb   --zone=${ZONE}

# get the Public IP Address of the NLB
gcloud compute addresses describe ssh-nlb-ip --region=${REGION --format="get(address)"
