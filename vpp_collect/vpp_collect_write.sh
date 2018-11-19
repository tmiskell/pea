#!/bin/bash
source ./config.sh

dest_dir=/home/tmelab/vpp_collect/vpp_collect_write_$(date +%Y_%m_%d)
mkdir -v -p $dest_dir

source /opt/intel/vpp-collector/vpp/collector/vpp-collect-vars.sh
sudo $sep_ins_script

curr_ram_cache=$($traffic_ctl config get $ram_cache_size | cut -d ' ' -f 2)
comment="Config:AEP;Phase:Write;RAM:${curr_ram_cache}"
vpp-collect-start
sleep $write_time
vpp-collect-stop
mv -v *.tar.gz $dest_dir
sudo $sep_rm_script

exit 0
