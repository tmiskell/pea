# Configuration settings for test_all.sh
# Settings for next test
ram_cache_size="68719476736"                 # Proxy RAM cache settings in bytes
ram_cache_cutoff="536870912"
mem_topo="8-8-8-128"
num_rand_objs=131072                 # Previously: 250000000
thrd_start=8
thrd_end=8
thrd_step=1
conn_start=$thrd_start
conn_end=1024
emon_collect="true"
aepwatch_collect="true"
seed_rand_num="true"
obj_dist_type="fixed"                 # fixed,gauss,zipf,real
obj_req_perc=0.05
tot_demand_perc=0.10
tot_req_size=64G
warm_disk_cache="true"
warm_up_req_size=128G
warm_up_rand_objs=524288
ats_gen_port="8888"
ats_gen_ip="localhost"
output_prefix="atsvm_${ram_cache_size}cache_${mem_topo}_${obj_dist_type}_seq"
# Local base directory to store results
base_dest_dir="/home/tmelab"
# Local wrk settings
wrk_dir="/home/tmelab/wrk"
wrk_exec="${wrk_dir}/wrk"
lua_script="${wrk_dir}/scripts/ats_seq.lua"
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
ats_gen="/home/tmelab/python_scripts/web_ats_gen.py" # Previously: /home/tmelab/webatsgen/atsgen
ats_drive="/dev/nvme0n1p1"
cache_thresh=0.95                                    # Threshold above which the cache will be considered warm
# ATS host settings
ats_host_un="root"
ats_host_rli="192.168.100.110"
# emon settings
emon_host_un="root"
emon_host_rli="aepdimm"
emon_start_script="/root/emon_collection/start_emon.sh"
emon_stop_script="/root/emon_collection/stop_emon.sh"
# AEPWatch settings
aep_host_un=$emon_host_un
aep_host_rli=$emon_host_rli
aep_start_script="/opt/intel/AEPWatch_1.1.0/bin64/AEPWatch"
aep_stop_script="/opt/intel/AEPWatch_1.1.0/bin64/AEPWatch-stop"
aep_output_csv="/home/tmelab/aepwatch_data/aepwatch.csv"
