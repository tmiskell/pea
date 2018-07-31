#!/usr/bin/python
from __future__ import with_statement

import os
import sys
import time
import pickle
import random
import hashlib
import binascii
import datetime
import argparse
import numpy as np
import BaseHTTPServer

class WebPageParam( object ):
    
    def __init__( self, obj_dist="fixed", x=0.0, y=0.0 ):
        KB = 1024
        MB = 1048576
        self.obj_dist = obj_dist
        self.x = x
        self.y = y
        self.obj_size = 0
        self.x_n = 0
        self.x_actual = 0.0
        self.y_actual = 0.0
        self.tot_demand = 0
        self.default_web_page_sizes = [
            32  * KB,
            64  * KB,
            256 * KB,
            512 * KB,
            768 * KB,
            1   * MB,
            int( round(2.7 * MB) ),
        ]        
        self.mu = ( min(self.default_web_page_sizes) + max(self.default_web_page_sizes) ) / 2.0
        self.index_mu = min( range(len(self.default_web_page_sizes)),
                             key=lambda x: abs(self.default_web_page_sizes[x] - self.mu) )
        self.sigma = 1.0
        self.a = 2.0

class AtsGenHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    """ Customized request handler to serve up variable sized web pages
    """

    def do_HEAD( self ):
        """ Respond to a HEAD request. """
        self.send_response( 200 )
        self.send_header( "Content-type", "text/html" )
        self.send_header( "Cache-Control", "max-age=31536000" )
        self.end_headers( )

    def do_GET( self ):
        """ Respond to a GET request. """
        script_dir = os.path.dirname( os.path.realpath(__file__) )
        web_page_param_file = os.path.join( script_dir, "web_page_param.pickle" )
        obj_size = self.select_obj_size( web_page_param_file )
        web_page, hash_content = self.create_web_page( obj_size )
        content_length = len( web_page )
        # Date is included by default in response header
        self.send_response( 200 )
        self.send_header( "Cache-Control", "max-age=31536000" )
        self.send_header( "Content-Length", "%d" % (content_length) )
        self.send_header( "Content-type", "text/plain" )
        self.send_header( "Etag", "\"" + hash_content + "\"" )
        self.end_headers( )
        self.wfile.write( web_page )

    def select_obj_size( self, web_page_param_file ):
        
        with open( web_page_param_file, "rb" ) as input_file:
            web_page_param = pickle.load( input_file )
            
        obj_size = 0
        if ( web_page_param.obj_dist == "fixed" ):
            obj_size = web_page_param.obj_size
        elif ( web_page_param.obj_dist == "gauss" ):
            index = int( round(np.random.normal(loc=web_page_param.index_mu, scale=web_page_param.sigma)) )
            index = min( index, len(web_page_param.default_web_page_sizes) - 1 )
            index = max( 0, index )
            obj_size = web_page_param.default_web_page_sizes[index]
        elif ( web_page_param.obj_dist == "zipf" ):
            while ( obj_size == 0 ):
                index = np.random.zipf( web_page_param.a ) % len( web_page_param.default_web_page_sizes )
                obj_size = web_page_param.default_web_page_sizes[index]
        elif ( web_page_param.obj_dist == "real" ):
            obj_size = random.choice( web_page_param.default_web_page_sizes )
            if web_page_param.x_actual < web_page_param.x:
                obj_size = max( web_page_param.default_web_page_sizes )
                y_perc_tot = float( web_page_param.tot_demand ) * ( web_page_param.y / 100.0 )
                if ( y_perc_tot < max(web_page_param.default_web_page_sizes) ):
                    obj_size = min( web_page_param.default_web_page_sizes, key=lambda a : abs(float(a) - y_perc_tot) )
                if ( web_page_param.obj_size == obj_size ):
                    web_page_param.x_n += 1
                else:
                    web_page_param.x_n = 1
                web_page_param.obj_size = obj_size
            web_page_param.tot_demand += obj_size
            web_page_param.x_actual = float( web_page_param.x_n * web_page_param.obj_size ) / web_page_param.tot_demand
            with open( web_page_param_file, "wb" ) as output_file:
                pickle.dump( web_page_param, output_file, protocol=pickle.HIGHEST_PROTOCOL )
            
        return obj_size
    
    def create_web_page( self, page_size ):
        """ Generate web page based on a hash of the URL. 
            page_size: Web page size in bytes
        """
        md5 = hashlib.md5( )
        md5.update( b"%s" % (self.path) )
        hash_content = md5.hexdigest( )
        content = ""
        while len( content ) < page_size:
            content += hash_content
        if len( content ) > page_size:
            content = content[:page_size]
        
        return content, hash_content

def port_type( x ):

    min_port = 8888
    max_port = 65535    

    x = int( x )
    if x < min_port:
        raise argparse.ArgumentTypeError( "Minimum port is %d" % (min_port) )
    elif x > max_port:
        raise argparse.ArgumentTypeError( "Maximum port is %d" % (max_port) )        
    
    return x
    
def main( argv ):

    script_dir = os.path.dirname( os.path.realpath(__file__) )
    web_page_param_file = os.path.join( script_dir, "web_page_param.pickle" )
    MB = 1048576
        
    parser = argparse.ArgumentParser( description="Generates a web server that serves up objects according to the specified distribution." )
    parser.add_argument( "--host", dest="host_name", help="Host name/IP address to use for the server" )
    parser.add_argument( "--port", dest="port_number", type=port_type, help="Port number to use for the server" )        
    parser.add_argument( "--obj-dist", dest="obj_dist", choices=["fixed", "gauss", "zipf", "real"], help="Object Distribution Type" )
    parser.add_argument( "--perc-obj", dest="x", type=float, help="Set percentage of objects for real distribution" )
    parser.add_argument( "--perc-tot", dest="y", type=float, help="Set percentage of total demand for real distribution" )
    args = parser.parse_args()

    if ( args.obj_dist == "real" ):
        web_page_param = WebPageParam( obj_dist=args.obj_dist, x=args.x, y=args.y )
    else:
        web_page_param = WebPageParam( args.obj_dist )
        if ( args.obj_dist == "zipf" ):
            web_page_param.default_web_page_sizes.append( 0 )    
            web_page_param.default_web_page_sizes.reverse( )
        elif ( args.obj_dist == "fixed" ):
            web_page_param.obj_size = 1 * MB

    with open( web_page_param_file, "wb" ) as output_file:
        pickle.dump( web_page_param, output_file, protocol=pickle.HIGHEST_PROTOCOL )

    server = BaseHTTPServer.HTTPServer( (args.host_name, args.port_number), AtsGenHandler )
    sys.stdout.write( "[%s]: Web Server Started - %s:%s\n" % (time.asctime(), args.host_name, args.port_number) )
    try:
        server.serve_forever( )
    except KeyboardInterrupt:
        server.server_close( )
    sys.stdout.write( "[%s]: Web Server Stopped - %s:%s\n" % (time.asctime(), args.host_name, args.port_number) )
    os.remove( web_page_param_file )

    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )
