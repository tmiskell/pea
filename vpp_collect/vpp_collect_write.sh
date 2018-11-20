#!/bin/bash
source ./config.sh

echo "[Creating destination directory]"
dest_dir=/home/tmelab/vpp_collect/vpp_collect_write_$(date +%Y_%m_%d)
mkdir -v -p $dest_dir

echo "[Setting up for next data collection]"
source /opt/intel/vpp-collector/vpp/collector/vpp-collect-vars.sh
sudo $sep_ins_script

echo "[Starting data collection]"
curr_ram_cache=$($traffic_ctl config get $ram_cache_size | cut -d ' ' -f 2)
comment="Config:Baseline;Phase:Write;RAM:${curr_ram_cache}"
vpp-collect-start -c $comment

start_time="$(date -u +%s)"
elapsed_time=0
while [ $elapsed_time -le $write_time ] ; do
    curr_ssd_bytes_used=$($traffic_ctl metric get $ssd_cache_bytes_used | cut -d ' ' -f 2)
    curr_ram_bytes_used=$($traffic_ctl metric get $ram_cache_bytes_used | cut -d ' ' -f 2)
    mark="SSD:${curr_ssd_bytes_used};RAM:${curr_ram_bytes_used}"
    echo "[Marking timeline: ${mark}]"
    vpp-collect-mark $mark
    sleep $mark_duration
    curr_time="$(date -u +%s)"
    let "elapsed_time=curr_time-start_time"
done

echo "[Stopping data collection]"
vpp-collect-stop

echo "[Moving output file]"
mv -v *.tar.gz $dest_dir

echo "[Cleaning up]"
sudo $sep_rm_script

exit 0
