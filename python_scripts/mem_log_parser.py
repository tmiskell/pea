#!/usr/bin/python
from __future__ import with_statement
import os
import sys
import operator

class LatencyBWData( object ):
    ""
    def __init__( self ):
        # Arrays for thread numbers and connection numbers
        self.thread_num = "0"
        self.conn_num = "0"
        # Arrays for latency fields
        self.avg_lat = "0"
        self.avg_lat_ms = "0"
        self.std_dev_lat = "0"
        self.max_lat = "0"
        self.std_dev_lat_perc = "0"
        # Arrays for request fields
        self.avg_req = "0"
        self.std_dev_req = "0"
        self.max_req = "0"
        self.std_dev_req_perc = "0"
        # Arrays for request/s and transfer/s fields        
        self.req_per_sec = "0"
        self.transfer_b_per_sec = "0"
        # Arrays for total requests, total time, and total transferred data
        self.tot_req = "0"
        self.tot_time = "0"
        self.tot_tran = "0"
        self.transfer_mb_per_sec = "0"
        # Arrays for socket errors
        self.sock_conn_err = "0"
        self.sock_read_err = "0"
        self.sock_write_err = "0"
        self.sock_time_err = "0"
        # Memory Topology
        self.mem_topo = ""

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

def main( argv ):
    """ Main program """
    
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
    
    # Parse command line arguments
    try:
        dir_name = os.path.abspath( argv[1] )
        output_f_name = os.path.join( dir_name, argv[2] + ".csv" )
        topology = argv[3]
    except IndexError:
        print "Usage: %s input_dir output_file_prefix topology" % ( argv[0] )
        return 1

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
    lat_bw = []
    for log_file in log_files:
        lat_bw.append( LatencyBWData() )
        lat_bw[-1].mem_topo = topology
        sys.stdout.write( "Processing: %s\n" % (log_file) )
    
        with open( log_file, 'r' ) as input_file:
            lines = input_file.readlines()
        
        for line in lines:
            next_line = line.strip()
            next_fields = next_line.split()
            if( ("threads" in next_line.lower()) and ("connections" in next_line.lower()) ):
                lat_bw[-1].thread_num = next_fields[thread_pos]
                lat_bw[-1].conn_num   = next_fields[conn_pos]
            elif( next_line.lower().startswith("latency") ):
                lat_bw[-1].avg_lat          = convert_units( next_fields[avg_pos] )
                lat_bw[-1].std_dev_lat      = convert_units( next_fields[std_dev_pos] )
                lat_bw[-1].max_lat          = convert_units( next_fields[max_pos] )
                lat_bw[-1].std_dev_lat_perc = convert_units( next_fields[std_dev_perc_pos] )
            elif( next_line.lower().startswith("req/sec") ):
                lat_bw[-1].avg_req          = convert_units( next_fields[avg_pos] )
                lat_bw[-1].std_dev_req      = convert_units( next_fields[std_dev_pos] )
                lat_bw[-1].max_req          = convert_units( next_fields[max_pos] )
                lat_bw[-1].std_dev_req_perc = convert_units( next_fields[std_dev_perc_pos] )
            elif( next_line.lower().startswith("requests/sec:") ):
                lat_bw[-1].req_per_sec      = convert_units( next_fields[req_pos] )
            elif( next_line.lower().startswith("transfer/sec:") ):
                lat_bw[-1].transfer_b_per_sec = convert_units( next_fields[tran_pos] )
            elif( ("requests in" in next_line.lower()) and (next_line.lower().endswith("read")) ):
                lat_bw[-1].tot_req          = convert_units( next_fields[tot_req_pos] )
                lat_bw[-1].tot_time         = convert_units( next_fields[tot_time_pos] )
                lat_bw[-1].tot_tran         = convert_units( next_fields[tot_tran_pos] )
            elif( next_line.lower().startswith("socket errors") ):
                lat_bw[-1].sock_conn_err    = convert_units( next_fields[sock_conn_err_pos] )
                lat_bw[-1].sock_read_err    = convert_units( next_fields[sock_read_err_pos] )
                lat_bw[-1].sock_write_err   = convert_units( next_fields[sock_write_err_pos] )
                lat_bw[-1].sock_time_err    = convert_units( next_fields[sock_time_err_pos] )
            lat_bw[-1].transfer_mb_per_sec = float(lat_bw[-1].transfer_b_per_sec) * ( 10.0 ** (-6))
            lat_bw[-1].avg_lat_ms  = str( float(lat_bw[-1].avg_lat ) * ( 10.0 ** ( 3) ) )

    lat_bw.sort( key=operator.attrgetter("transfer_mb_per_sec") )

    # Write CSV file
    header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
        "Thread_Connection_Number",
        "Thread_Number",
        "Connection_Number",
        "Configuration",
        "Transfer (MB/s)",
        "Avg_Latency (ms)",
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
        for i in range( len(lat_bw) ):
            output_file.write( "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                lat_bw[i].thread_num + "-" + lat_bw[i].conn_num,
                lat_bw[i].thread_num,
                lat_bw[i].conn_num,
                lat_bw[i].mem_topo,
                str(lat_bw[i].transfer_mb_per_sec),
                lat_bw[i].avg_lat_ms,
                lat_bw[i].avg_lat,
                lat_bw[i].std_dev_lat,
                lat_bw[i].max_lat,
                lat_bw[i].std_dev_lat_perc,
                lat_bw[i].avg_req,
                lat_bw[i].std_dev_req,
                lat_bw[i].max_req,
                lat_bw[i].std_dev_req_perc,
                lat_bw[i].tot_req,
                lat_bw[i].tot_time,
                lat_bw[i].tot_tran,
                lat_bw[i].req_per_sec,
                lat_bw[i].transfer_b_per_sec,
                lat_bw[i].sock_conn_err,
                lat_bw[i].sock_read_err,
                lat_bw[i].sock_write_err,
                lat_bw[i].sock_time_err
            ) )
            output_file.write( '\n' )
            
    sys.stdout.write( "Wrote: %s in %s\n" % (os.path.basename(output_f_name), dir_name) )

    return 0

if __name__ == "__main__": 
    sys.exit( main(sys.argv) )
