# Configuration settings for test_all.sh
# Settings for next test
output_prefix="atsvm_128cache_128AEPx2"
duration=300   # (300 s / iteration) * (24 iterations) * (1 min. / 60 s) * (1 hr. / 60 min.) = 2 hours
conn_start=64
conn_end=256
conn_step=8
clear_cache="false"
emon_collect="true"
num_rand_objs=250000000
# Local base directory to store results
base_dest_dir="/home/tmelab"
# Local wrk settings
wrk_dir="/home/tmelab/wrk"
wrk_exec="${wrk_dir}/wrk"
lua_script="${wrk_dir}/scripts/ats.lua"
# Local Log analysis scripts
mem_log_parser="/home/tmelab/python_scripts/mem_log_parser.py"
squid_log_parser="/home/tmelab/python_scripts/squid_log_parser.py"
metrics_script="${HOME}/shell_scripts/collect_metrics.sh"
# ATS settings
ip_addr="192.168.0.95"
ats_port="8080"
ats_un="root"
ats_rli="192.168.100.110"
ats_dir="/opt/ats/bin"
ats_exec="${ats_dir}/trafficserver"
squid_cat="${ats_dir}/traffic_logcat"
ats_ctl="${ats_dir}/traffic_ctl"
ats_log_dir="/var/log/trafficserver"
ats_config_dir="/etc/trafficserver"
ats_gen="/home/tmelab/webatsgen/atsgen"
ats_gen_port="8888"
ats_drive="/dev/vda1"
# ATS host settings
ats_host_un="root"
ats_host_rli="aepdimm"
# emon settings
emon_start_script="/root/emon_collection/start_emon.sh"
emon_stop_script="/root/emon_collection/stop_emon.sh"
# Proxy RAM cache settings in bytes
ram_cache_size="137438953472"
ram_cache_cutoff="536870912"
