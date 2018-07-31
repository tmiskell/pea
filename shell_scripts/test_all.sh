#!/bin/bash

source config.sh

# Exit should any command return a non-zero status code
trap 'exit' ERR ;

run_test( ){

    t_req_size=$1 ;
    c_start=$2 ;
    c_end=$3 ;
    start_time=$4 ;
    dest_dir=$5 ;
    log_fname=$6 ;
    t_start=$7 ;
    t_end=$8 ;
    t_step=$9 ;
    warm_up_only=${10} ;
    
    echo "ATS server: http://${ip_addr}:${ats_port}" ;
    echo "Total Request Size: ${t_req_size} B" ;
    echo "Work script: ${wrk_exec}, Lua script: ${lua_script}" ;
    thread=$t_start ;
    conn=$c_start ;	
    if [ $conn -lt $thread ] ; then
	conn=$thread ;
    fi
    while [ $conn -le $c_end ] ;
    do
	# Flush cache between each run
	flush_cache
        next_log_file="${dest_dir}/wrk_${output_prefix}_${thread}_${conn}_${start_time}.log" ;
	echo "Setting Thread: ${thread}, Connections: ${conn}" ;
	echo -n "${thread},${conn}," >> $log_fname ;
	# Perform warm-up run
	echo "Performing warm up run (W/R)" ;
	if [ "${warm_up_only}" == "false" ] ; then 
	    if [ "${emon_collect}" == "true" ] ; then
		start_emon_collection $emon_host_un $emon_host_rli $emon_start_script ;
	    fi ;
	    if [ "${aepwatch_collect}" == "true" ] ; then
		start_aepwatch_collection $aep_host_un $aep_host_rli $aep_start_script $aep_output_csv ;
	    fi ;
	fi ;
	$wrk_exec -t $thread \
		  -z $t_req_size \
		  -c $conn \
		  -s $lua_script \
		  "http://${ip_addr}:${ats_port}/" ;
	if [ "${warm_up_only}" == "false" ] ; then 
	    if [ "${emon_collect}" == "true" ] ; then
		stop_emon_collection $emon_host_un $emon_host_rli $emon_stop_script ;
		retrieve_emon_data $emon_host_un $emon_host_rli $dest_dir "emon_WR_${thread}-${conn}.dat" ;
	    fi ;
	    if [ "${aepwatch_collect}" == "true" ] ; then
		stop_aepwatch_collection $aep_host_un $aep_host_rli $aep_stop_script ;
		retrieve_aepwatch_data $aep_host_un $aep_host_rli $aep_output_csv "aep_WR_${thread}-${conn}.csv" ;
	    fi ;
	fi ;
	# Perform test run
	sleep 2 ;
	if [ "${warm_up_only}" == "false" ] ; then
	    echo "Performing test run (R)" ;
	    if [ "${emon_collect}" == "true" ] ; then
		start_emon_collection $emon_host_un $emon_host_rli $emon_start_script ;
	    fi ;
	    if [ "${aepwatch_collect}" == "true" ] ; then
		start_aepwatch_collection $aep_host_un $aep_host_rli $aep_start_script $aep_output_csv ;
	    fi ;	    
	    $wrk_exec -t $thread \
		      -z $t_req_size \
		      -c $conn \
		      -s $lua_script \
		      "http://${ip_addr}:${ats_port}/" \
		| tee $next_log_file ;
	    if [ "${emon_collect}" == "true" ] ; then
		stop_emon_collection $emon_host_un $emon_host_rli $emon_stop_script ;
		retrieve_emon_data $emon_host_un $emon_host_rli $dest_dir "emon_R_${thread}-${conn}.dat" ;
	    fi ;
	    if [ "${aepwatch_collect}" == "true" ] ; then
		stop_aepwatch_collection $aep_host_un $aep_host_rli $aep_stop_script ;
		retrieve_aepwatch_data $aep_host_un $aep_host_rli $aep_output_csv "aep_R_${thread}-${conn}.csv" ;
	    fi ;
	    sleep 2 ;
	fi ;
	let "conn=conn * 2" ;
    done

    return ;
    
}

flush_cache(){

    # Flush ATS cache
    cmd="${ats_ctl} config set proxy.config.cache.ram_cache.size 0 && ${ats_ctl} server restart" ;
    echo "Logging into ${ats_un}@${ats_rli}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;    
    sleep 5 ;
    
    cmd="${ats_ctl} config set proxy.config.cache.ram_cache.size ${ram_cache_size} && ${ats_ctl} server restart" ;
    echo "Logging into ${ats_un}@${ats_rli}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;    
    sleep 1 ;

    # Flush kernel cache on host for ATS
    echo "Logging into ${ats_un}@${ats_rli}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;        

    # Flush kernel cache on host for WRK client
    cmd="sysctl -w vm.drop_caches=3" ;
    echo "Executing: ${cmd}" ;
    $cmd ;

    return ;
    
}


clear_previous_ats_logs( ){
    # Remove previous squid logs before starting next run

    ats_log_dir=$1 ;
    ats_un=$2 ;
    ats_rli=$3 ;

    cmd="rm -v ${ats_log_dir}/*" ;

    echo "Logging into ${ats_un}@${ats_rli}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;

    cmd="ls -l ${ats_log_dir}/" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;

    return ;
    
}

change_cache_permissions( ){
    # Ensure ATS can write to cache
    
    ats_drive=$1 ;
    ats_un=$2 ;
    ats_rli=$3 ;

    cmd="chown -R trafficserver:trafficserver ${ats_drive}" ;

    echo "Logging into ${ats_un}@${ats_rli}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 1 ;   
    
    return ;

}

update_proxy_cache_settings( ){
    # Updates proxy cache settings on ATS server

    ats_config_dir=$1 ;
    rc_size=$2 ;
    rc_cutoff=$3 ;
    ats_un=$4 ;
    ats_rli=$5 ;

    records="${ats_config_dir}/records.config" ;
    local_records="/tmp/records.config" ;

    echo "Logging into ${ats_un}@${ats_rli}: Updating proxy RAM cache settings in: ${records}" ;
    
    scp "${ats_un}@${ats_rli}:${records}" $local_records ;
    prev_rc_size=$( grep ram_cache.size $local_records | cut -d' ' -f4 ) ;
    prev_rc_cutoff=$( grep ram_cache.cutoff $local_records | cut -d' ' -f4 ) ;    
    
    echo "Setting RAM cache size to: ${ram_cache_size} B" ;
    sed -i "s/proxy.config.cache.ram_cache.size INT ${prev_rc_size}/proxy.config.cache.ram_cache.size INT ${rc_size}/" $local_records ; 
    echo "Setting RAM cache size to: ${ram_cache_cutoff} B" ;
    sed -i "s/proxy.config.cache.ram_cache_cutoff INT ${prev_rc_cutoff}/proxy.config.cache.ram_cache_cutoff INT ${rc_cutoff}/" $local_records ;

    scp $local_records "${ats_un}@${ats_rli}:${records}" ;
    rm $local_records ;

    cmd="grep ram_cache ${records}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    
    return ;
    
}

update_lua_script_settings( ){

    lua_script=$1 ;
    n_rand_objs=$2 ;
    seed_rand_n=$3 ;

    echo "Setting number of random objects to: ${n_rand_objs}" ;
    prev_n_rand_objs=$(grep "counter = math.random(" $lua_script | cut -d '(' -f 2) ;
    prev_n_rand_objs=$(echo $prev_n_rand_objs | sed -r "s/[)]//") ;
    sed -i "s/counter = math.random(${prev_n_rand_objs})/counter = math.random(${n_rand_objs})/" $lua_script ;
    grep "counter = math.random(" $lua_script ;

    if [ "${seed_rand_n}" == "true" ] ; then
        echo "Seeding random number generator for each thread" ;	
	sed -i "s/-- math.randomseed/math.randomseed/" $lua_script ;
    else
        echo "Not seeding random number generator for each thread" ;		
	grep --quiet "\-\- math.randomseed" $lua_script ;
	if [ $? -ne 0 ] ; then
	    sed -i "s/math.randomseed/-- math.randomseed/" $lua_script ;
	fi ;
    fi
    grep "math.randomseed" $lua_script ;
    
    return ;
    
}

start_ats_server( ){
    # Starts ATS server and local CDN

    ats_exec=$1 ;
    ats_gen=$2 ;
    ats_un=$3 ;
    ats_rli=$4 ;
    ats_gen_port=$5 ;
    ats_gen_ip=$6 ;
    ats_log_dir=$7 ;
    ats_ctl=$8 ;
    obj_dist_type=$9 ;
    obj_req_perc=${10} ;
    tot_demand_perc=${11} ;

    echo "Logging into ${ats_un}@${ats_rli}"

    cmd="${ats_gen} --host ${ats_gen_ip} --port ${ats_gen_port} --obj-dist ${obj_dist_type} --perc-obj ${obj_req_perc} --perc-tot ${tot_demand_perc}" ;
    cmd="nohup ${cmd} > $HOME/nohup.out 2> $HOME/nohup.err < /dev/null &" ;
    #cmd="nohup ${ats_gen} --port ${ats_gen_port} > $HOME/nohup.out 2> $HOME/nohup.err < /dev/null &" ;    
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 1 ;

    cmd="ps aux | grep $(basename ${ats_gen})" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;    
    sleep 1 ;
    
    cmd="${ats_exec} start" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;        
    sleep 1 ;

    cmd="${ats_exec} status" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;        
    sleep 5 ;

    cmd="cat ${ats_log_dir}/diags.log" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;        

    return ;
    
}

stop_ats_server( ){
    # Stops ATS server and local CDN

    ats_exec=$1 ;
    ats_gen=$2 ;
    ats_un=$3 ;
    ats_rli=$4 ;

    echo "Logging into ${ats_un}@${ats_rli}"

    cmd="${ats_exec} stop" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 5 ;
    
    cmd="pkill $(basename ${ats_gen})" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 1 ;
    
    return ;
    
}

retrieve_squid_log( ){
    # Convert and move the squid log that was generated.

    squid_cat=$1 ;
    ats_log_dir=$2 ;
    dest_dir=$3 ;
    output_prefix=$4 ;
    ats_un=$5 ;
    ats_rli=$6 ;
    
    echo "Logging into ${ats_un}@${ats_rli}"

    cmd="${squid_cat} --output_file ${ats_log_dir}/squid.log ${ats_log_dir}/squid.blog" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 90 ;

    echo "Transferring: ${ats_un}@${ats_rli}:${ats_log_dir}/squid.log to ${dest_dir}/squid_${output_prefix}.log" ;
    scp "${ats_un}@${ats_rli}:${ats_log_dir}/squid.log" "${dest_dir}/squid_${output_prefix}.log" ;
    
    return ;
    
}

start_metrics_collection( ){
    # Starts collection of metrics

    metrics_script=$1 ;
    dest_dir=$2 ;

    echo "Starting collection of metrics" ;
    $metrics_script $dest_dir &
    
    return ;
    
}

stop_metrics_collection( ){
    # Stops collection of metrics    

    metrics_script=$1 ;
    
    echo "Stopping collection of metrics" ;
    bname_metrics_script=$(basename $metrics_script) ;
    bname_metrics_script=$(echo $bname_metrics_script | sed -r 's/.sh//') ;
    pkill $bname_metrics_script ;  
    
    return ;
    
}

start_aepwatch_collection( ){

    aep_host_un=$1 ;
    aep_host_rli=$2 ;
    aep_start_script=$3 ;
    output_csv=$4 ;
    
    echo "Logging into ${aep_host_un}@${aep_host_rli}" ;
    cmd="${aep_start_script} 1 -f ${output_csv}" ;
    echo "Executing: ${cmd}" ;
    ssh $aep_host_un@$aep_host_rli "bash -c '"${cmd}"'" &
    
    return ;
    
}

stop_aepwatch_collection( ){

    aep_host_un=$1 ;
    aep_host_rli=$2 ;
    aep_stop_script=$3 ;
    
    echo "Logging into ${aep_host_un}@${aep_host_rli}" ;
    cmd="${aep_stop_script}" ;
    echo "Executing: ${cmd}" ;
    ssh $aep_host_un@$aep_host_rli "bash -c '"${cmd}"'" &
    
    return ;
    
}

retrieve_aepwatch_data( ){

    aep_host_un=$1 ;
    aep_host_rli=$2 ;
    aep_output_csv=$3 ;
    f_name=$4 ;
    
    echo "Retrieving ${aep_output_csv}" ;    
    scp "${aep_host_un}@${aep_host_rli}:/${aep_output_csv}" "${dest_dir}/${f_name}" ;

    echo "Logging into ${aep_host_un}@${aep_host_rli}" ;
    cmd="rm ${aep_output_csv}" ;
    echo "Executing: ${cmd}" ;
    ssh $aep_host_un@$aep_host_rli "bash -c '"${cmd}"'" ;

    return ;
    
}


start_emon_collection( ){
    # Start emon data collection

    emon_host_un=$1 ;
    emon_host_rli=$2 ;
    emon_start_script=$3 ;
    
    echo "Logging into ${emon_host_un}@${emon_host_rli}" ;
    cmd="${emon_start_script}" ;
    echo "Executing: ${cmd}" ;
    ssh $emon_host_un@$emon_host_rli "bash -c '"${cmd}"'" &

    return ;
    
}

stop_emon_collection( ){
    # Stop emon data collection

    emon_host_un=$1 ;
    emon_host_rli=$2 ;
    emon_stop_script=$3 ;
    
    echo "Logging into ${emon_host_un}@${emon_host_rli}" ;
    cmd="${emon_stop_script}" ;
    echo "Executing: ${cmd}" ;
    ssh $emon_host_un@$emon_host_rli "bash -c '"${cmd}"'" ;

    return ;
    
}

retrieve_emon_data( ){

    emon_host_un=$1 ;
    emon_host_rli=$2 ;
    dest_dir=$3 ;
    f_name=$4 ;

    echo "Retrieving emon.dat" ;    
    scp "${emon_host_un}@${emon_host_rli}:/${emon_host_un}/emon_collection/emon.dat" "${dest_dir}/${f_name}" ;

    echo "Logging into ${emon_host_un}@${emon_host_rli}" ;
    cmd="rm /${emon_host_un}/emon_collection/emon.dat" ;
    echo "Executing: ${cmd}" ;
    ssh $emon_host_un@$emon_host_rli "bash -c '"${cmd}"'" ;

    return ;
    
}

cache_warmed_up( ){

    dest_dir=$1 ;
    cache_thresh=$2 ;

    cache_hit_ratio=$(tail -n1 "${dest_dir}/metrics.csv" | cut -d "," -f 2) ;

    if (( $(bc <<< "${cache_hit_ratio} >= ${cache_thresh}") )) ; then
	echo "true" ;
    else
	echo "false" ;
    fi    
    
}

# Initialize internal variables
warm_up_start_time=`date +%Y%m%d%H%M` ;
dest_dir="${base_dest_dir}/${warm_up_start_time}/${output_prefix}" ;
log_fname="${dest_dir}/test_${output_prefix}_${warm_up_start_time}.log" ;

# Set destination directory
mkdir -p $dest_dir ;

# Make certain ATS server is stopped before updated settings.
stop_ats_server $ats_exec $ats_gen $ats_un $ats_rli ;
# Perform setup tasks
clear_previous_ats_logs $ats_log_dir $ats_un $ats_rli ;
change_cache_permissions $ats_drive $ats_un $ats_rli ;
update_proxy_cache_settings $ats_config_dir $ram_cache_size $ram_cache_cutoff $ats_un $ats_rli ;
start_ats_server $ats_exec $ats_gen $ats_un $ats_rli $ats_gen_port $ats_gen_ip $ats_log_dir \
		 $ats_ctl $obj_dist_type $obj_req_perc $tot_demand_perc ;
start_metrics_collection $metrics_script $dest_dir ;

if [ "${warm_disk_cache}" == "true" ] ; then
    # Perform initial warm up of cache before collecting data
    update_lua_script_settings $lua_script $warm_up_rand_objs $seed_rand_num ;
    warm_up_only="true" ;
    warm_up_conn_start=$conn_end;
    warm_up_conn_end=$conn_end;
    warm_up_thrd_start=$thrd_end ;
    warm_up_thrd_end=$thrd_end ;
    run_test $warm_up_req_size $warm_up_conn_start \
	     $warm_up_conn_end $warm_up_start_time $dest_dir $log_fname \
	     $warm_up_thrd_start $warm_up_thrd_end $thrd_step $warm_up_only ;
    result=$(cache_warmed_up $dest_dir $cache_thresh)
    if [ "${result}" != "true" ] ; then
	echo "Warning: Cache still not warmed up, results may be invalid"
    fi ;
fi ;

stop_metrics_collection $metrics_script ;
rm -rfv $dest_dir ;

# Start actual test run after initial warm up phase
echo "Cached warmed up, starting actual test"

start_time=`date +%Y%m%d%H%M` ;
dest_dir="${base_dest_dir}/${start_time}/${output_prefix}" ;
log_fname="${dest_dir}/test_${output_prefix}_${start_time}.log" ;

mkdir -p $dest_dir ;
update_lua_script_settings $lua_script $num_rand_objs $seed_rand_num ;
start_metrics_collection $metrics_script $dest_dir ;

# Write header for log file
echo "Test Start Time: ${start_time}" > $log_fname ;
echo "Threads,Connections,Req/s,MB/s,Avg(us),StDev(us),50%(us),90%(us), 99%(us),99.999(us)" >> $log_fname ;

warm_up_only="false"
run_test $tot_req_size $conn_start $conn_end $start_time \
	 $dest_dir $log_fname $thrd_start $thrd_end $thrd_step $warm_up_only ;

# Mark end time of test
stop_time=`date +%Y%m%d%H%M` ;
echo "Test Stop Time: ${stop_time}" >> $log_fname ;

# Perform clean-up
stop_metrics_collection $metrics_script ;
stop_ats_server $ats_exec $ats_gen $ats_un $ats_rli ;

# Analyze log files
echo "Analyzing log files in: ${dest_dir} with ${mem_log_parser}" ;
$mem_log_parser $dest_dir $output_prefix $mem_topo ;

#retrieve_squid_log $squid_cat $ats_log_dir $dest_dir $output_prefix $ats_un $ats_rli ;
#echo "Analyzing log files in: ${dest_dir} with ${squid_log_parser}" ;
#$squid_log_parser $dest_dir ;

exit ;
