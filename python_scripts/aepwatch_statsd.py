#!/usr/bin/python
from __future__ import with_statement
import os
import sys
import time
import statsd

def main( argv ):

    statsd_host = "localhost"
    statsd_port = 8125
    init_sleep_time = 1
    num_args = 2
    
    if ( len(argv) < num_args ):
        sys.stdout.write( "%s aep_watch_dir\n" % (argv[0]) )
        return 1
        
    aepwatch_dir = os.path.realpath( os.path.expanduser(argv[1]) )
    aepwatch_file = os.path.join( aepwatch_dir, "aepwatch_data.csv" )

    # Wait for file to be created
    while ( not os.path.isfile(aepwatch_file) ): 
        time.sleep( init_sleep_time )

    # Avoid race condition. Read all lines from file.
    time.sleep( init_sleep_time )        
    with open ( aepwatch_file, "r" ) as input_file:
        lines = input_file.readlines( )
    
    sys.stdout.write( "Processing: %s\n" % (aepwatch_file) )
    # Advance past comments
    i = 0 
    while lines[i].strip().startswith( "#" ):
        i += 1
            
    # Determine number of timestamp fields
    fields = lines[i].strip().split( ";" )
    j = 0
    num_tstamp_fields = 0
    while not fields[j].lower().startswith( "dimm" ):
        num_tstamp_fields += 1
        j += 1
    sys.stdout.write( "Number of time stamp fields: %d\n" % (num_tstamp_fields) )
    
    # First DIMM. Determine number of fields per DIMM
    num_dimms = 1
    num_fields_per_dimm = 0
    j += 1
    while j < len( fields ):
        if fields[j].lower().startswith("dimm"):
            # Second DIMM.
            num_dimms += 1
            break
        num_fields_per_dimm += 1
        j += 1
    sys.stdout.write( "Number of fields per DIMM: %d\n" % (num_fields_per_dimm) )
    
    j += 1
    # Determine total number of DIMMs.
    while j < len( fields ):
        if fields[j].lower().startswith("dimm"):
            num_dimms += 1
        j += 1
    sys.stdout.write( "Number of DIMMs: %d\n" % (num_dimms) )
        
    # Advance past timestamp field names
    i += 1
    fields = lines[i].strip().split( ";" )    
    j = 0
    while j < num_tstamp_fields:
        j += 1
        
    # Determine DIMM fields names
    sys.stdout.write( "Collecting per DIMM field names\n" )
    dimm_fields = []
    k = 0
    while k < num_fields_per_dimm:
        dimm_fields.append( fields[j] )
        k += 1
        j += 1    
    # Open connection to statsd
    sys.stdout.write( "Opening statsd connection\n" )
    conn = statsd.StatsClient( statsd_host, statsd_port )

    # Continually collect latest data
    poll_interval = 30
    prev_mod_time = os.stat( aepwatch_file )
    try:
        while True:
            time.sleep( poll_interval )
            curr_mod_time = os.stat( aepwatch_file )
            if curr_mod_time != prev_mod_time:
                sys.stdout.write( "File modified, opening file\n" )
                with open( aepwatch_file, "r" ) as input_file:
                    lines = input_file.readlines()
                last_line = lines[len(lines)-1]
                fields = last_line.split( ";" )
                j = 0
                # Advance past time stamp fields
                while j < num_tstamp_fields:
                    j += 1
                # Iterate over all DIMMs
                i = 0
                while i < num_dimms:
                    # Iterate over all fields for current DIMM
                    k = 0
                    while k < num_fields_per_dimm:
                        next_field_name = "%s%d-%s" % ( "DDRT", i, dimm_fields[k] )
                        conn.gauge( next_field_name, fields[j] )
                        sys.stdout.write( "Sent: %s - %s\n" % (next_field_name, fields[j]) )                        
                        k += 1
                        j += 1
                    i += 1
                sys.stdout.write( "Sent data to statsd\n" )                
                prev_mod_time = curr_mod_time            
    except KeyboardInterrupt:
        sys.stdout.write( "Exiting\n" )
    
    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )
