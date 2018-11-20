#!/bin/bash
# emon configuration variables
sep_ins_script="/opt/intel/vpp-collector/sepdk/src/insmod-sep" 
sep_rm_script="/opt/intel/vpp-collector/sepdk/src/rmmod-sep"
mark_duration=120
# ATS configuration variables
traffic_ctl=/opt/ats/bin/traffic_ctl
clear_cache=/home/tmelab/shell_scripts/clear_cache.sh
# ATS RAM cache fill specific variables
ram_cache_size=proxy.config.cache.ram_cache.size
ram_cache_bytes_used=proxy.process.cache.ram_cache.bytes_used
ssd_cache_bytes_used=proxy.process.cache.bytes_used
# ATS RAM cache read specific variables
cache_hit_mem_tol=0.50
cache_hit_mem_ratio=proxy.node.cache_hit_mem_ratio
client_conn=proxy.process.http.current_client_connections
# VPP collection specific variables
sec_per_min=60
write_time=$((30*sec_per_min))
read_time=$((20*sec_per_min))
