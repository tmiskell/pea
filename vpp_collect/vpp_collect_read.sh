#!/bin/bash
source ./config.sh

echo "[Creating destination directory]"
dest_dir=/home/tmelab/vpp_collect/vpp_collect_read_$(date +%Y_%m_%d)
mkdir -v -p $dest_dir

echo "[Setting up for next data collection]"
source /opt/intel/vpp-collector/vpp/collector/vpp-collect-vars.sh
sudo $sep_ins_script
curr_ram_cache=$($traffic_ctl config get $ram_cache_size | cut -d ' ' -f 2)
comment="Config:Baseline;Phase:Read;RAM:${curr_ram_cache}"

echo "[Starting data collection]"
vpp-collect-start -c $comment

start_time="$(date -u +%s)"
elapsed_time=0
while [ $elapsed_time -le $read_time ] ; do
    curr_clients=$($traffic_ctl metric get $client_conn | cut -d ' ' -f 2)
    curr_ratio=$($traffic_ctl metric get $cache_hit_mem_ratio | cut -d ' ' -f 2)        
    mark="Clients:${curr_clients},Ratio:${curr_ratio}"
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
