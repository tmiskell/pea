#!/bin/bash
source config.sh

dest_dir=$1 ;
output_file="${dest_dir}/metrics.csv" ;

chr_avg_cmd="${ats_ctl} metric get proxy.node.cache_hit_ratio_avg_10s | cut -d \" \" -f 2" ;
chf_cmd="${ats_ctl} metric get proxy.node.http.cache_hit_fresh | cut -d \" \" -f 2" ;

echo "elapsed_time (s),cache_hit_ratio_avg_10s,cache_hit_fresh" > $output_file ;
start_time="$(date -u +%s)" ;
while true ; do
    curr_time="$(date -u +%s)" ;
    dt="$(($curr_time-$start_time))" ;
    next_chr_avg=$(ssh $ats_un@$ats_rli "bash -c '"$chr_avg_cmd"'") ;
    next_chf=$(ssh $ats_un@$ats_rli "bash -c '"$chf_cmd"'") ;
    echo "${dt},${next_chr_avg},${next_chf}" >> $output_file ;
    sleep 10 ;
done ;
