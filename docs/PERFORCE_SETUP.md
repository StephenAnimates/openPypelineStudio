# Setting up Perforce (Helix Core) in the Cloud

Perforce (Helix Core) is the industry standard Version Control System (VCS) for VFX, Animation, and AAA Game Development. Perforce offers a **free tier for up to 5 users and 20 workspaces**, making it perfect for indie teams and testing `openPypeline Studio`.

This guide outlines how to deploy your free Perforce server on major cloud providers at zero cost using their free-tier Virtual Machines (VMs).

## 1. Choose Your Cloud Provider

### Google Cloud Platform (GCP) - *Best for "Always Free" Longevity*
GCP offers an "Always Free" tier that doesn't expire after 12 months.
* **Compute:** 1 `e2-micro` VM instance (must be in specific US regions like Oregon, Iowa, or South Carolina).
* **Storage:** 30 GB Standard persistent disk.
* **Bandwidth:** 1 GB outbound data transfer per month.
* *Note: The 1 GB bandwidth limit is fine for code and small `.mb` files, but will exhaust quickly with heavy assets.*

### Amazon Web Services (AWS) - *Best Balance for 12 Months*
AWS offers a generous free tier for your first 12 months.
* **Compute:** 750 hours/month of a `t2.micro` or `t3.micro` instance.
* **Storage:** 30 GB EBS General Purpose SSD.
* **Bandwidth:** 100 GB outbound data transfer per month.

### Microsoft Azure - *Most Storage for 12 Months*
Azure also provides a 12-month free tier.
* **Compute:** 750 hours/month of a `B1s` instance.
* **Storage:** 64 GB Premium SSD Managed Disks.
* **Bandwidth:** 100 GB outbound data transfer per month.

## 2. Install Perforce on your VM

When launching your VM on your chosen provider, select **Ubuntu 20.04 LTS or 22.04 LTS** as your Operating System. Once the VM is running, SSH into the machine and run the following commands to install the Helix Core Server (`p4d`).

**Step 1: Add the Perforce repository**
```bash
# Add the Perforce package key
wget -qO - https://package.perforce.com/perforce.pubkey | sudo apt-key add -

# Add the Perforce repository to your APT sources
echo "deb http://package.perforce.com/apt/ubuntu focal release" | sudo tee /etc/apt/sources.list.d/perforce.list

# Update APT
sudo apt-get update
```

**Step 2: Install Helix Core Server**
```bash
sudo apt-get install helix-p4d
```

**Step 3: Configure your Server**
Run the configuration script and follow the prompts to set up your server name, root directory, and administrator account:
```bash
sudo /opt/perforce/sbin/configure-helix-p4d.sh
```

## 3. Configure Firewall Rules
By default, Perforce communicates over port **1666**. You must open this port in your Cloud Provider's firewall/security group settings to allow `openPypeline Studio` (and your local P4 client) to connect to it.

* **GCP:** VPC Network -> Firewall -> Create Firewall Rule (Allow TCP: 1666).
* **AWS:** EC2 -> Security Groups -> Edit Inbound Rules (Add Custom TCP, Port 1666).
* **Azure:** Virtual Machine -> Networking -> Add inbound port rule (Port 1666).

## 4. Next Steps
Once your server is running, you can configure your `openPypeline` project settings to use `perforce` as the VCS type. Ensure your local machine has the `p4` command-line tool installed, as `openPypeline` uses it to communicate with the server.