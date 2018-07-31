# Configuration settings for test_all.sh
# Settings for next test
output_prefix="aepdimm_32G_2x" ;
duration=240 ;
conn_start=64 ;
conn_end=256 ;
conn_step=8 ;
# Local base directory to store results
base_dest_dir=/home/tmelab ;
# Local wrk settings
wrk_dir=$HOME/wrk
wrk_exec=${wrk_dir}/wrk ;
lua_script=${wrk_dir}/scripts/ats.lua ;
# Local Log analysis scripts
mem_log_parser=$HOME/python_scripts/mem_log_parser.py ;
squid_log_parser=$HOME/python_scripts/squid_log_parser.py ;
# ATS settings
ip_addr="192.168.0.55" ;
ats_port="8080" ;
ats_un="root" ;
ats_rli="aepdimm" ;
ats_dir=/opt/ats/bin
ats_exec=${ats_dir}/trafficserver ;
squid_cat=${ats_dir}/traffic_logcat ;
ats_log_dir=/var/log/trafficserver ;
ats_config_dir=/etc/trafficserver ;
ats_gen=/home/tmelab/webatsgen/atsgen ;
ats_gen_port=8888 ;
# Proxy RAM cache settings in bytes
ram_cache_size=34359738368 ;
ram_cache_cutoff=1073741824 ;
