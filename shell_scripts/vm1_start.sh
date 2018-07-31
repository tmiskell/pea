#!/bin/bash
# Global variables
NAME="ats_vm" ;
RAM_MB=262144 ;   
CPU_MODEL="host" ;
NUM_VCPU=16 ;
CPU_SET="2-17" ;
BOOT_ORDER="hd" ;
DISK_PATH="${HOME}/images/disk/${NAME}_boot.img" ;
DISK_SIZE_GB=45 ;
DISK_FORMAT="qcow2" ;      # Format must be specified otherwise for security reasons the hypervisor may not be able to access the HD
NET_NAME="default" ;       # Connect to the default virtual network supplied by libvirt
NET_DEV_MODEL="virtio" ;
DISPLAY_TYPE="spice" ;
DISPLAY_PORT=5901 ;
DISPLAY_IP="0.0.0.0" ;     # Set to 0.0.0.0 to allow connections from other machines
OS_TYPE="linux" ;
HOST_DEV0="pci_0000_18_02_0" ;
HOST_DEV1="pci_0000_18_0a_0" ;
HOST_DEV2="pci_0000_af_02_0" ;
HOST_DEV3="pci_0000_af_0a_0" ;
ISO_PATH="${HOME}/Downloads/CentOS-7-x86_64-DVD-1804.iso" ;
# Create virtual machine using specified variables
# listen=$DISPLAY_IP,port=$DISPLAY_PORT
# --video qxl
# --cdrom $ISO_PATH
virt-install --name $NAME --ram $RAM_MB --cpu $CPU_MODEL --vcpu=$NUM_VCPU --os-type $OS_TYPE --boot $BOOT_ORDER --disk path=$DISK_PATH,size=$DISK_SIZE_GB,format=$DISK_FORMAT --network network=$NET_NAME,model=$NET_DEV_MODEL --graphics $DISPLAY_TYPE --noautoconsole --hvm --hostdev $HOST_DEV0 --hostdev $HOST_DEV1 --hostdev $HOST_DEV2 --hostdev $HOST_DEV3
