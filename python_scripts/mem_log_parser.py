#!/usr/bin/python
from __future__ import with_statement
import os
import sys

def convert_units( x ):
    # Removes trailing units and adjusts decimal place
    y = x.replace( ",", "" )
    y = y.replace( "s", "" )
    y = y.replace( "B", "" )
    if( y.endswith("G") ):
        y = y.replace( "G", "" )
        y = float( y )
        y = y * 1e9
    elif( y.endswith("M") ):
        y = y.replace( "M", "" )
        y = float( y )
        y = y * 1e6
    elif( y.endswith("k") ):
        y = y.replace( "k", "" )
        y = float( y )
        y = y * 1e3
    elif( y.endswith("m") ):
        y = y.replace( "m", "" )
        y = float( y )
        y = y * 1e-3
    elif( y.endswith("u") ):
        y = y.replace( "u", "" )
        y = float( y )
        y = y * 1e-6
    elif( y.endswith("n") ):
        y = y.replace( "n", "" )
        y = float( y )
        y = y * 1e-9
    elif( y.endswith("p") ):
        y = y.replace( "p", "" )
        y = float( y )
        y = y * 1e-12
    elif( y.endswith("%") ):
        y = y.replace( "%", "" )
    try:
        y = '{0:f}'.format( y )
    except ValueError:
        y = str( y )

    return y

# Indices for threads and connections
thread_pos = 0
conn_pos = 3
# Indices for latency and request fields
avg_pos = 1
std_dev_pos = 2
max_pos = 3
std_dev_perc_pos = 4
# Indices for requests/s and transfers/s
req_pos = 1
tran_pos = 1
# Indices for total requests, total time, and total transferred data
tot_req_pos = 0
tot_time_pos = 3
tot_tran_pos = 4
# Indices for Socket errors
sock_conn_err_pos = 3
sock_read_err_pos = 5
sock_write_err_pos = 7
sock_time_err_pos = 9

# Arrays for thread numbers and connection numbers
thread_num = []
conn_num = []
# Arrays for latency fields
avg_lat = []
std_dev_lat = []
max_lat = []
std_dev_lat_perc = []
# Arrays for request fields
avg_req = []
std_dev_req = []
max_req = []
std_dev_req_perc = []
# Arrays for request/s and transfer/s fields
req_per_sec = []
transfer_per_sec = []
# Arrays for total requests, total time, and total transferred data
tot_req = []
tot_time = []
tot_tran = []
# Arrays for socket errors
sock_conn_err = []
sock_read_err = []
sock_write_err = []
sock_time_err = []

# Parse command line arguments
try:
    dir_name = os.path.abspath( sys.argv[1] )
    output_f_name = os.path.join(dir_name, sys.argv[2] + ".csv")
except IndexError:
    print "Usage: %s input_dir output_file_prefix" % ( sys.argv[0] )
    sys.exit( 1 )

# Collect all log files
log_files = []
if os.path.exists( dir_name ):
    for next_file in os.listdir( dir_name ):
        if next_file.startswith( "squid" ):
            continue
        if next_file.startswith( "test" ):
            continue
        if next_file.endswith( ".log" ):
            log_files.append( os.path.join(dir_name, next_file) )             

# Parse log files
for log_file in log_files:
    sys.stdout.write( "Processing: %s\n" % (log_file) )
    with open( log_file, 'r' ) as input_file:
        lines = input_file.readlines()
    thread_num.append( "0" )
    conn_num.append( "0" )
    avg_lat.append( "0" )
    std_dev_lat.append( "0" )
    max_lat.append( "0" )
    std_dev_lat_perc.append( "0" )
    avg_req.append( "0" )
    std_dev_req.append( "0" )
    max_req.append( "0" )
    std_dev_req_perc.append( "0" )
    req_per_sec.append( "0" )
    transfer_per_sec.append( "0" )
    tot_req.append( "0" )
    tot_time.append( "0" )
    tot_tran.append( "0" )
    sock_conn_err.append( "0" )
    sock_read_err.append( "0" )
    sock_write_err.append( "0" )
    sock_time_err.append( "0" )
    for line in lines:
        next_line = line.strip()
        next_fields = next_line.split()
        if( ("threads" in next_line.lower()) and ("connections" in next_line.lower()) ):
            thread_num[-1] = next_fields[thread_pos]
            conn_num[-1]   = next_fields[conn_pos]
        elif( next_line.lower().startswith("latency") ):
            avg_lat[-1]          = convert_units( next_fields[avg_pos] )
            std_dev_lat[-1]      = convert_units( next_fields[std_dev_pos] )
            max_lat[-1]          = convert_units( next_fields[max_pos] )
            std_dev_lat_perc[-1] = convert_units( next_fields[std_dev_perc_pos] )
        elif( next_line.lower().startswith("req/sec") ):
            avg_req[-1]          = convert_units( next_fields[avg_pos] )
            std_dev_req[-1]      = convert_units( next_fields[std_dev_pos] )
            max_req[-1]          = convert_units( next_fields[max_pos] )
            std_dev_req_perc[-1] = convert_units( next_fields[std_dev_perc_pos] )
        elif( next_line.lower().startswith("requests/sec:") ):
            req_per_sec[-1]      = convert_units( next_fields[req_pos] )
        elif( next_line.lower().startswith("transfer/sec:") ):
            transfer_per_sec[-1] = convert_units( next_fields[tran_pos] )
        elif( ("requests in" in next_line.lower()) and (next_line.lower().endswith("read")) ):
            tot_req[-1]          = convert_units( next_fields[tot_req_pos] )
            tot_time[-1]         = convert_units( next_fields[tot_time_pos] )
            tot_tran[-1]         = convert_units( next_fields[tot_tran_pos] )
        elif( next_line.lower().startswith("socket errors") ):
            sock_conn_err[-1]    = convert_units( next_fields[sock_conn_err_pos] )
            sock_read_err[-1]    = convert_units( next_fields[sock_read_err_pos] )
            sock_write_err[-1]   = convert_units( next_fields[sock_write_err_pos] )
            sock_time_err[-1]    = convert_units( next_fields[sock_time_err_pos] )

# Write CSV file
header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                                                                        "Thread_Connection_Number",
                                                                        "Thread_Number",
                                                                        "Connection_Number",
                                                                        "Avg_Latency (s)",
                                                                        "Stdev_Latency (s)",
                                                                        "Max_Latency (s)",
                                                                        "+/-Stdev_Latency (%)",
                                                                        "Avg (Requests/s)",
                                                                        "Stdev (Requests/s)",
                                                                        "Max (Requests/s)",
                                                                        "+/- Stdev (Requests/s %)",
                                                                        "Total_Requests",
                                                                        "Total_Time (s)",
                                                                        "Total_Transfer (B)",
                                                                        "Total (Requests/s)",
                                                                        "Total (Transfers/s B)",
                                                                        "Socket_Connection_Errors",
                                                                        "Socket_Read_Errors",
                                                                        "Socket_Write_Errors",
                                                                        "Socket_Timeout_Errors"
                                                                        )

with open( output_f_name, 'w' ) as output_file:
    output_file.write( header )
    output_file.write( '\n' )
    for i in range( len(avg_lat) ):
        output_file.write( "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                                                                                         thread_num[i] + conn_num[i],
                                                                                         thread_num[i],
                                                                                         conn_num[i],
                                                                                         avg_lat[i],
                                                                                         std_dev_lat[i],
                                                                                         max_lat[i],
                                                                                         std_dev_lat_perc[i],
                                                                                         avg_req[i],
                                                                                         std_dev_req[i],
                                                                                         max_req[i],
                                                                                         std_dev_req_perc[i],
                                                                                         tot_req[i],
                                                                                         tot_time[i],
                                                                                         tot_tran[i],
                                                                                         req_per_sec[i],
                                                                                         transfer_per_sec[i],
                                                                                         sock_conn_err[i],
                                                                                         sock_read_err[i],
                                                                                         sock_write_err[i],
                                                                                         sock_time_err[i]
                                                                                         )
                           )
        output_file.write( '\n' )
    sys.stdout.write( "Wrote: %s in %s\n" % (os.path.basename(output_f_name), dir_name) )

sys.exit( 0 )
