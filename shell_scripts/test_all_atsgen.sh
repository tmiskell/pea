#!/bin/bash

source config.sh

# Exit should any command return a non-zero status code
trap 'exit' ERR ;

run_test( ){

    duration=$1 ;
    ip_addr=$2 ;
    ats_port=$3 ;
    output_prefix=$4 ;
    conn_start=$5 ;
    conn_end=$6 ;
    conn_step=$7 ;
    start_time=$8 ;
    lua_script=$9 ;
    dest_dir=${10} ;
    wrk_exec=${11} ;
    log_fname=${12} ;
 
    echo "Running test: ATS server: http://${ip_addr}:${ats_port}"
    echo "Connections: [${conn_start},${conn_end}], Connection Step: ${conn_step}"
    echo "Duration: ${duration} s" ;
    echo "Work script: ${wrk_exec}, Lua script: ${lua_script}"
    conn=$conn_start ;
    while [ $conn -lt $conn_end ] ;
    do
	thread=$conn ;
	next_log_file="${dest_dir}/wrk_${output_prefix}_${thread}_${conn}_${start_time}.log";
	echo "Setting Thread: ${thread}, Connections: ${conn}" ;
	echo -n "${thread},${conn}," >> $log_fname ;
	$wrk_exec -t $thread \
	      -d $duration \
	      -c $conn \
	      -s $lua_script \
	      "http://${ip_addr}:${ats_port}/1048576/" \
	    | tee $next_log_file ;
	let "conn=conn + conn_step" ;
	sleep 2 ;
    done

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
    num_rand_objs=$2 ;

    echo "Setting number of random objects to: ${num_rand_objs}" ;
    prev_num_rand_objs=$(grep "counter = math.random(" $lua_script | cut -d '(' -f 2) ;
    prev_num_rand_objs=$(echo $prev_num_rand_objs | sed -r "s/[)]//") ;
    sed -i "s/counter = math.random(${prev_num_rand_objs})/counter = math.random(${num_rand_objs})/" $lua_script ;
    grep "counter = math.random(" $lua_script ;
    
    return ;
    
}

start_ats_server( ){
    # Starts ATS server and local CDN

    ats_exec=$1 ;
    ats_gen=$2 ;
    ats_un=$3 ;
    ats_rli=$4 ;
    ats_gen_port=$5 ;
    ats_log_dir=$6 ;
    ats_ctl=$7 ;
    clear_cache=$8 ;

    echo "Logging into ${ats_un}@${ats_rli}"

    cmd="nohup ${ats_gen} --port ${ats_gen_port} > $HOME/nohup.out 2> $HOME/nohup.err < /dev/null &" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;
    sleep 1 ;

    cmd="ps aux | grep atsgen" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_un@$ats_rli "bash -c '"$cmd"'" ;    
    sleep 1 ;
    
    cmd="${ats_exec} start" ;
    if [ "$clear_cache" == "true" ] ; then
        cmd="${cmd} && ${ats_ctl} server start --clear-cache" ;
    fi ;
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
     
    cmd="pkill atsgen" ;
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

start_emon_collection( ){
    # Start emon data collection

    ats_host_un=$1 ;
    ats_host_rli=$2 ;
    emon_start_script=$3 ;
        
    echo "Logging into ${ats_host_un}@${ats_host_rli}" ;
    cmd="${emon_start_script}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_host_un@$ats_host_rli "bash -c '"${cmd}"'" &

    return ;
    
}

stop_emon_collection( ){
    # Stop emon data collection

    ats_host_un=$1 ;
    ats_host_rli=$2 ;
    emon_stop_script=$3 ;
        
    echo "Logging into ${ats_host_un}@${ats_host_rli}" ;
    cmd="${emon_stop_script}" ;
    echo "Executing: ${cmd}" ;
    ssh $ats_host_un@$ats_host_rli "bash -c '"${cmd}"'" ;

    return ;
    
}

retrieve_emon_data( ){

    ats_host_un=$1 ;
    ats_host_rli=$2 ;
    dest_dir=$3 ;

    echo "Retrieving emon.dat" ;    
    scp "${ats_host_un}@${ats_host_rli}:/${ats_host_un}/emon_collection/emon.dat" "${dest_dir}/emon.dat" ;

    return ;
    
}

# Initialize internal variables
log_fname="${dest_dir}/test_${output_prefix}_${start_time}.log" ;

# Make certain ATS server is stopped before updated settings.
stop_ats_server $ats_exec $ats_gen $ats_un $ats_rli ;
# Perform setup tasks
clear_previous_ats_logs $ats_log_dir $ats_un $ats_rli ;
change_cache_permissions $ats_drive $ats_un $ats_rli ;
update_proxy_cache_settings $ats_config_dir $ram_cache_size $ram_cache_cutoff $ats_un $ats_rli ;
update_lua_script_settings $lua_script $num_rand_objs  ;
start_ats_server $ats_exec $ats_gen $ats_un $ats_rli $ats_gen_port $ats_log_dir $ats_ctl $clear_cache ;

# Start test
start_time=`date +%Y%m%d%H%M` ;
# Set destination directory
dest_dir="${base_dest_dir}/${start_time}/${output_prefix}" ;
mkdir -v -p $dest_dir ;

start_metrics_collection $metrics_script $dest_dir ;
if [ "$emon_collect" == "true" ] ; then
    start_emon_collection $ats_host_un $ats_host_rli $emon_start_script ;
fi ;

# Write header for log file
echo "Test Start Time: ${start_time}" > $log_fname ;
echo "Threads,Connections,Req/s,MB/s,Avg(us),StDev(us),50%(us),90%(us), 99%(us),99.999(us)" >> $log_fname ;

run_test $duration $ip_addr $ats_port $output_prefix $conn_start \
	 $conn_end $conn_step $start_time $lua_script $dest_dir $wrk_exec $log_fname ;

# Mark end time of test
stop_time="`date +%Y%m%d%H%M`" ;
echo "Test Stop Time: ${stop_time}" >> $log_fname ;

stop_metrics_collection $metrics_script ;
if [ "$emon_collect" == "true" ] ; then
    stop_emon_collection $ats_host_un $ats_host_rli $emon_stop_script ;
fi ;

# Perform clean-up
stop_ats_server $ats_exec $ats_gen $ats_un $ats_rli ;
if [ "$emon_collect" == "true" ] ; then
    retrieve_emon_data $ats_host_un $ats_host_rli $dest_dir ;
fi ;
#retrieve_squid_log $squid_cat $ats_log_dir $dest_dir $output_prefix $ats_un $ats_rli ;

# Analyze log files
echo "Analyzing log files in: ${dest_dir} with ${mem_log_parser}" ;
$mem_log_parser $dest_dir $output_prefix ;
#echo "Analyzing log files in: ${dest_dir} with ${squid_log_parser}" ;
#$squid_log_parser $dest_dir ;

exit ;
