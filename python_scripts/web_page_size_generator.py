#!/usr/bin/python
from __future__ import with_statement

import os
import sys
import random
import pickle
import numpy as np
import argparse

def calc_tot_demand( link_bw, test_duration ):
    """ Estimates total demand in B of next test based on 
        maximum link BW in GB/s along with test duration in seconds.
    """

    GiB_to_B = 1073741824
    bits_per_byte = 8

    link_bw_GBps = float( link_bw ) / float( bits_per_byte )
    max_demand_GB = link_bw_GBps * test_duration
    tot_demand = int( round(max_demand_GB * GiB_to_B) )

    return tot_demand

def gauss_dist( tot_demand, default_web_page_sizes ):
    """ Generates an object size distribution that follows
        a Gaussian distribution.
    """

    min_size = min( default_web_page_sizes )
    max_size = max( default_web_page_sizes )
    mu = ( min_size + max_size ) / 2.0
    index_mu = min( range(len(default_web_page_sizes)), key=lambda x: abs(default_web_page_sizes[x] - mu) )
    sigma = 1.75

    web_page_size_dist = []
    curr_demand = 0
    while ( curr_demand < tot_demand ):
        sys.stdout.write( "Bytes left: %d\n" % (tot_demand - curr_demand) )
        if( curr_demand + min_size <= tot_demand ):
            index = int( round(np.random.normal(loc=index_mu, scale=sigma)) )
            index = min( index, len(default_web_page_sizes) - 1)
            index = max( 0, index )
            obj_size = default_web_page_sizes[index]
        else:
            obj_size = min_size
        web_page_size_dist.append( obj_size )
        curr_demand += obj_size
    
    return web_page_size_dist, mu, sigma

def zipf_dist( tot_demand, default_web_page_sizes ):
    """ Generates an object size distribution that follows
        a Zipfian distribution.
    """

    a = 2.0 
    min_size = min( default_web_page_sizes )
    # Append additional element and reverse array to force
    # Zipfian distribution to skew towards the first element of the original array
    default_web_page_sizes.append( 0 )    
    default_web_page_sizes.reverse()
    
    web_page_size_dist = []
    curr_demand = 0
    while ( curr_demand < tot_demand ):
        sys.stdout.write( "Bytes left: %d\n" % (tot_demand - curr_demand) )
        if( curr_demand + min_size <= tot_demand ):
            index = np.random.zipf( a ) % len( default_web_page_sizes )
            obj_size = default_web_page_sizes[index]
        else:
            obj_size = min_size
        if( obj_size > 0 ):
            web_page_size_dist.append( obj_size )
            curr_demand += obj_size

    default_web_page_sizes.reverse()
    del default_web_page_sizes[-1]
    
    return web_page_size_dist

def real_dist( x, y, tot_demand, default_web_page_sizes ):
    """ Initialize web page size distribution s.t. an object size in bytes is ordered s.t.
        x % of the objects selected represent y % of the total demand in bytes.

        E.g., Given the constraint: 0.5 % of the objects requested should 
        represent 10% of the total demand.
        Let the total demand = 100 MB.
        Then 10 % of total demand = 10 MB.
        Then 0.5 % of the object sizes available for selection should be 10 MB.
        In which case, a suitable set of object sizes requested would be given by: 
        { 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 1 MB, 22 MB, 10 MB }
    """    
    y_perc_tot = float( tot_demand ) * ( y / 100.0 )
    x_obj_size = min( default_web_page_sizes, key=lambda a : abs(float(a) - y_perc_tot) )
    
    curr_demand = 0
    web_page_size_dist = []
    while( curr_demand < tot_demand ):
        x_calc = 0.0
        obj_size = x_obj_size
        
        sys.stdout.write( "Bytes left: %d\n" % (tot_demand - curr_demand) )        
        if( len(web_page_size_dist) > 0 ) :
            num_x_obj_size = web_page_size_dist.count( x_obj_size )
            x_calc = (float(num_x_obj_size) / float(len(web_page_size_dist))) * 100.0
        if( x_calc >= x ):
            # x % criteria has been satisfied, populate the rest of the list
            while obj_size == x_obj_size:
                # Need to incorporate test that obj_size contribution to curr_demand remains <= tot_demand
                obj_size = random.choice( default_web_page_sizes )
                if( curr_demand + obj_size > tot_demand ):
                    bytes_left = tot_demand - obj_size
                    obj_size = min( default_web_page_sizes, key=lambda a : abs(float(a) - bytes_left) )
                    break                
        web_page_size_dist.append( obj_size )
        curr_demand += obj_size
            
    return web_page_size_dist

def create_hist_of_web_page_sizes( web_page_sizes, csv_file_name ):
    """ Generate a histogram of the web page sizes generated.
    """
        
    hist_data = zip( *np.histogram(web_page_sizes, bins="auto", density=True) )
    np.savetxt( csv_file_name, hist_data, delimiter=',' )
    
    with open( csv_file_name, "r" ) as input_file:
        lines = input_file.readlines( )
        
    with open( csv_file_name, "w" ) as output_file:
        output_file.write( "Frequency,Bin\n" )
        output_file.writelines( lines )

    return

def analyze_dist( web_page_sizes, default_web_page_sizes, tot_demand, csv_file_name ):
    """ Calculate percentages of the occurrences for each of the object sizes 
        with respect to the total number of available objects.
    """
    
    tot_obj = len( web_page_sizes )

    obj_perc = []
    for next_size in default_web_page_sizes:
        obj_perc.append( float(web_page_sizes.count(next_size)) / float(tot_obj) )
        
    with open( csv_file_name, "w" ) as output_file:
        output_file.write( "Object Size (B),Percentage (%)\n" )
        for i in range( len(default_web_page_sizes) ):
            output_file.write( "%d: %d,%0.2f\n" % (i + 1, default_web_page_sizes[i], obj_perc[i]) )

    return

def validate_gauss_dist( tot_demand, web_page_sizes, mu_dist, sigma_dist ):

    curr_demand = 0
    obj_sizes = []
    while ( curr_demand < tot_demand ):
        obj_sizes.append( random.choice(web_page_sizes) )
        curr_demand += obj_sizes[-1]
    mu = np.mean( obj_sizes )
    sigma = np.std( obj_sizes )

    if ( abs(mu - mu_dist) < 0.01 ):
        if( abs(sigma - sigma_dist) < 0.01 ):
            return True
    
    return False

def validate_real_dist( x, y, tot_demand, web_page_sizes, default_web_page_sizes ):
    """ Validate that the simulated real-world scenario distribution 
        satisfies the user specified criteria for the values of x and y.
    """

    y_perc_tot = float( tot_demand ) * ( y / 100.0 )
    x_obj_size = min( default_web_page_sizes, key=lambda a : abs(float(a) - y_perc_tot) )
    tot_obj = len( web_page_sizes )
    x_perc_tot = ( float(web_page_sizes.count(x_obj_size)) / float(tot_obj) ) * 100.0
    epsilon = 1.0

    if( (x_perc_tot - x) > epsilon ):
        return False
    
    return True

def main( argv ):
    """ Main function """
    
    KB = 1024
    MB = 1048576
    default_web_page_sizes = [ 32  * KB,
                               64  * KB,
                               256 * KB,
                               512 * KB,
                               768 * KB,
                               1   * MB,
                               int( round(2.7 * MB) ),
                             ]

    parser = argparse.ArgumentParser( description="Generate various object size distributions for HTTP performance benchmarking." )
    parser.add_argument( "--obj-dist", dest="obj_dist", choices=["fixed", "gauss", "zipf", "real"], help="Object Distribution Type" )
    parser.add_argument( "--perc-obj", dest="x", type=float, help="Set percentage of objects for real distribution" )
    parser.add_argument( "--perc-tot", dest="y", type=float, help="Set percentage of total demand for real distribution" )
    parser.add_argument( "--time", dest="test_duration", type=int, help="Test duration per iteration (s)" )
    parser.add_argument( "--bw", dest="link_bw", type=float, help="Link BW (Gbps)" )
    parser.add_argument( "--output", dest="output_file_dir", help="Destination directory" )
    args = parser.parse_args()    

    output_file_dir = os.path.realpath( os.path.expanduser(args.output_file_dir) )
    
    output_file_name = os.path.join( args.output_file_dir, "web_pages.pickle" )
    hist_csv_file_name = os.path.join( args.output_file_dir, "obj_hist.csv" )
    obj_dist_csv_file_name = os.path.join( args.output_file_dir, "obj_size_dist.csv" )
    args.obj_dist = args.obj_dist.lower()
    
    sys.stdout.write( "Generating a %s object size distribution.\n" % (args.obj_dist) )
    default_web_page_sizes.sort()
    if( args.obj_dist == "fixed" ):
        web_page_sizes = [ random.choice(default_web_page_sizes) ]
    else:
        tot_demand = calc_tot_demand( args.link_bw, args.test_duration )
        if ( args.obj_dist == "gauss" ):
            web_page_sizes, mu, sigma = gauss_dist( tot_demand, default_web_page_sizes )
            valid_dist = validate_gauss_dist( tot_demand, default_web_page_sizes, mu, sigma )
        elif ( args.obj_dist == "zipf" ):
            web_page_sizes = zipf_dist( tot_demand, default_web_page_sizes )
            valid_dist = True
        elif ( args.obj_dist == "real" ):
            web_page_sizes = real_dist( args.x, args.y, tot_demand, default_web_page_sizes )
            valid_dist = validate_real_dist( args.x, args.y, tot_demand, web_page_sizes, default_web_page_sizes )
        if( not valid_dist ):
            sys.stderr.write( "Error: Object size distribution is invalid\n" )
        create_hist_of_web_page_sizes( web_page_sizes, hist_csv_file_name )
        sys.stdout.write( "Wrote: %s\n" % (hist_csv_file_name) )
        analyze_dist( web_page_sizes, default_web_page_sizes, tot_demand, obj_dist_csv_file_name )
        sys.stdout.write( "Wrote: %s\n" % (obj_dist_csv_file_name) )        

    with open( output_file_name, "wb" ) as output_file:
        pickle.dump( web_page_sizes, output_file, protocol=pickle.HIGHEST_PROTOCOL )
    sys.stdout.write( "Wrote: %s\n" % (output_file_name) )
    
    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )
