#!/usr/bin/python
from __future__ import with_statement
import numpy as np
import logging
import sys
import os

def create_histogram( x, x_min, x_max, n_bins ):
    bins = []
    delta = (x_max - x_min) / np.float64(n_bins)
    for i in range( n_bins ):
        bins.append( x_min + (i * delta) )
    return np.histogram(x, bins=bins)

num_args = 2
if len( sys.argv ) < num_args:
    sys.stderr.write( "Usage: %s %s\n" % (sys.argv[0], "log_dir") )
    sys.exit( 1 )

# Create logger for parsing script
logger = logging.getLogger( )
logger.setLevel( logging.DEBUG )
stream = logging.StreamHandler( sys.stdout )
stream.setLevel( logging.DEBUG )
log_format = logging.Formatter( "%(asctime)s - %(levelname)s - %(message)s" )
stream.setFormatter( log_format )
logger.addHandler( stream )
# Collect log files
dir_name = sys.argv[1]
squid_files = []
logger.info( "Collecting files" )
for next_item in os.listdir( dir_name ):
    if( next_item.startswith("squid") ):
        if( next_item.endswith(".log") ):
            squid_files.append( os.path.join(dir_name, next_item) )
# Parse log files
events = []
lat_tcp_hit = []
lat_tcp_miss = []
lat_tcp_mem_hit = []
lat_other = []
for next_file in squid_files:
    logger.info("Reading:\t" + next_file)
    with open( next_file, 'r' ) as input_file:
        lines = input_file.readlines()
    for line in lines:
        cache_field = line.split("|Cache=")[1].split("|")[0].strip()
        lat_field = line.split("|Latency=")[1].split("|")[0].strip()
        events.append( cache_field )
        if cache_field == "TCP_HIT":
            lat_tcp_hit.append(int(lat_field))
        elif cache_field == "TCP_MISS":
            lat_tcp_miss.append(int(lat_field))
        elif cache_field == "TCP_MEM_HIT":
            lat_tcp_mem_hit.append(int(lat_field))
        else:
            lat_other.append(int(lat_field))
# Calculate metrics for events
tot_tcp_hit_event = events.count( "TCP_HIT" )
tot_tcp_miss_event = events.count( "TCP_MISS" )
tot_tcp_mem_hit_event = events.count( "TCP_MEM_HIT" )
tot_event = len( events )
tot_other_event = tot_event - (tot_tcp_hit_event + tot_tcp_miss_event + tot_tcp_mem_hit_event)
if tot_event != 0:
    pct_tcp_hit_event = tot_tcp_hit_event / np.float64(tot_event) * 100.0
    pct_tcp_miss_event = tot_tcp_miss_event / np.float64(tot_event) * 100.0
    pct_tcp_mem_hit_event = tot_tcp_mem_hit_event / np.float64(tot_event) * 100.0
    pct_other_event = tot_other_event / np.float64(tot_event) * 100.0
else:
    logger.warning("Zero cache events detected" )
    pct_tcp_hit_event = 0.0
    pct_tcp_miss_event = 0.0
    pct_tcp_mem_hit_event = 0.0
    pct_tcp_other_event = 0.0
# Convert to Numpy arrays. Note: Although a performance hit, use Python objects to avoid potential overflows with large ints
lat_tcp_hit = np.array(lat_tcp_hit, dtype=object)
lat_tcp_miss = np.array(lat_tcp_miss, dtype=object)
lat_tcp_mem_hit = np.array(lat_tcp_mem_hit, dtype=object)
lat_other = np.array(lat_other, dtype=object)
# Calculate total latency. Calculate average latency. Calculate standard deviation. Note: Account for division by zero.
if np.size(lat_tcp_hit) != 0:
    tot_lat_tcp_hit = np.sum(lat_tcp_hit)
    avg_lat_tcp_hit = np.mean(lat_tcp_hit)
    min_lat_tcp_hit = np.amin(lat_tcp_hit)
    max_lat_tcp_hit = np.amax(lat_tcp_hit)
    std_lat_tcp_hit = np.std(lat_tcp_hit)
else:
    logger.warning("Zero latency events recorded for TCP_HIT latency")
    avg_lat_tcp_hit = 0.0
    tot_lat_tcp_hit = 0.0
    min_lat_tcp_hit = 0.0
    max_lat_tcp_hit = 0.0
    std_lat_tcp_hit = 0.0    
if np.size(lat_tcp_miss) != 0:
    tot_lat_tcp_miss = np.sum(lat_tcp_miss)
    avg_lat_tcp_miss = np.mean(lat_tcp_miss)
    min_lat_tcp_miss = np.amin(lat_tcp_miss)
    max_lat_tcp_miss = np.amax(lat_tcp_miss)
    std_lat_tcp_miss = np.std(lat_tcp_miss)
else:
    logger.warning("Zero latency events recorded for TCP_MISS latency")    
    avg_lat_tcp_miss = 0.0
    tot_lat_tcp_miss = 0.0        
    min_lat_tcp_miss = 0.0
    max_lat_tcp_miss = 0.0
    std_lat_tcp_miss = 0.0    
if np.size(lat_tcp_mem_hit) != 0:
    tot_lat_tcp_mem_hit = np.sum(lat_tcp_mem_hit)
    avg_lat_tcp_mem_hit = np.mean(lat_tcp_mem_hit)
    min_lat_tcp_mem_hit = np.amin(lat_tcp_mem_hit)
    max_lat_tcp_mem_hit = np.amax(lat_tcp_mem_hit)
    std_lat_tcp_mem_hit = np.std(lat_tcp_mem_hit)
else:
    logger.warning("Zero latency events recorded for TCP_MEM_HIT latency")
    avg_lat_tcp_mem_hit = 0.0
    tot_lat_tcp_mem_hit = 0.0
    min_lat_tcp_mem_hit = 0.0
    max_lat_tcp_mem_hit = 0.0
    std_lat_tcp_mem_hit = 0.0    
if np.size(lat_other) != 0.0:
    tot_lat_other = np.sum(lat_other)
    avg_lat_other = np.mean(lat_other)
    min_lat_other = np.amin(lat_other)
    max_lat_other = np.amax(lat_other)
    std_lat_other = np.std(lat_other)
else:
    logger.warning("Zero latency events recorded for latency for all other events")
    avg_lat_other = 0.0
    tot_lat_other = 0.0    
    min_lat_other = 0.0
    max_lat_other = 0.0
    std_lat_other = 0.0    
tot_lat = np.sum(np.array([tot_lat_tcp_hit, tot_lat_tcp_miss, tot_lat_tcp_mem_hit, tot_lat_other], dtype=object))
# Create histogram of latency data
n_bins = 100
if min_lat_tcp_hit != max_lat_tcp_hit:
    tcp_hit_hist = create_histogram( lat_tcp_hit, 0, max_lat_tcp_hit, n_bins )
else:
    logger.warning("Unable to create histogram for TCP_HIT. Min and max are equal.")
    tcp_hit_hist = None
if min_lat_tcp_miss != max_lat_tcp_miss:
    tcp_miss_hist = create_histogram( lat_tcp_miss, 0, max_lat_tcp_miss, n_bins )
else:
    logger.warning("Unable to create histogram for TCP_MISS. Min and max are equal.")
    tcp_miss_hist = None    
if min_lat_tcp_mem_hit != max_lat_tcp_mem_hit:
    tcp_mem_hit_hist = create_histogram( lat_tcp_mem_hit, 0, max_lat_tcp_mem_hit, n_bins )
else:
    logger.warning("Unable to create histogram for TCP_MEM_HIT. Min and max are equal.")
    tcp_mem_hit_hist = None    
if min_lat_other != max_lat_other:
    other_hist = create_histogram( lat_other, 0, max_lat_other, n_bins )
else:
    logger.warning("Unable to create histogram for all other events. Min and max are equal.")
    other_hist = None
# Create histogram csv file per event type
hist = [tcp_hit_hist, tcp_miss_hist, tcp_mem_hit_hist, other_hist]
csv_fnames_prefix = ["tcp_hit", "tcp_miss", "tcp_mem_hit", "other"]
for i in range( len(hist) ):
    if( hist[i] ):
        data = zip( *(hist[i]) )
        next_csv_fname = os.path.join( dir_name, csv_fnames_prefix[i] + "_histogram.csv" )
        np.savetxt( next_csv_fname, data, delimiter=',' )
        logger.info( "Wrote %s in %s" % (os.path.basename(next_csv_fname), dir_name) )
# Create top level metrics output csv file
main_csv_fname = os.path.join( dir_name, "squid_log_results.csv" )
with open( main_csv_fname, 'w' ) as output_file:
    # Write the header
    output_file.write( "Total_TCP_HIT_Events,Total_TCP_MISS_Events,Total_TCP_MEM_HIT_Events,Total_Other_Events,Total_Events" )
    output_file.write( ",Percent_TCP_HIT_events_(%),Percent_TCP_MISS_events_(%),Percent_TCP_MEM_HIT_events_(%),Percent_Others_events_(%)" )
    output_file.write( ",Total_Latency_TCP_HIT_(ms),Total_Latency_TCP_MISS_(ms),Total_Latency_TCP_MEM_HIT_(ms),Total_Latency_Others_(ms)" )
    output_file.write( ",Avg_Latency_TCP_HIT_(ms),Avg_Latency_TCP_MISS_(ms),Avg_Latency_TCP_MEM_HIT_(ms),Avg_Latency_Others_(ms)" )
    output_file.write( ",Min_Latency_TCP_HIT_(ms),Min_Latency_TCP_MISS_(ms),Min_Latency_TCP_MEM_HIT_(ms),Min_Latency_Others_(ms)" ) 
    output_file.write( ",Max_Latency_TCP_HIT_(ms),Max_Latency_TCP_MISS_(ms),Max_Latency_TCP_MEM_HIT_(ms),Max_Latency_Others_(ms)" )
    output_file.write( ",StdDev_Latency_TCP_HIT,StdDev_Latency_TCP_MISS,StdDev_Latency_TCP_MEM_HIT,StdDev_Latency_Others\n" )
    # Write the body
    output_file.write( "%d,%d,%d,%d,%d" % (tot_tcp_hit_event, tot_tcp_miss_event, tot_tcp_mem_hit_event, tot_other_event, tot_event) )
    output_file.write( ",%g,%g,%g,%g" % (pct_tcp_hit_event, pct_tcp_miss_event, pct_tcp_mem_hit_event, pct_other_event) )
    output_file.write( ",%d,%d,%d,%d" % (tot_lat_tcp_hit, tot_lat_tcp_miss, tot_lat_tcp_mem_hit, tot_lat_other) )
    output_file.write( ",%g,%g,%g,%g" % (avg_lat_tcp_hit, avg_lat_tcp_miss, avg_lat_tcp_mem_hit, avg_lat_other) )
    output_file.write( ",%d,%d,%d,%d" % (min_lat_tcp_hit, min_lat_tcp_miss, min_lat_tcp_mem_hit, min_lat_other) )
    output_file.write( ",%d,%d,%d,%d" % (max_lat_tcp_hit, max_lat_tcp_miss, max_lat_tcp_mem_hit, max_lat_other) )
    output_file.write( ",%g,%g,%g,%g" % (std_lat_tcp_hit, std_lat_tcp_miss, std_lat_tcp_mem_hit, std_lat_other) )
    output_file.write( "\n" )
logger.info( "Wrote %s in %s" % (os.path.basename(main_csv_fname), dir_name) )
sys.exit()
