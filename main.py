#!/usr/bin/python

import argparse
from tcpsession import *

def port_expression( string ):
    separated = string.rsplit(":", 1)
    if len(separated) != 2:
        raise argparse.ArgumentTypeError()
    return [ separated[0], int(separated[1]) ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", help="port to listen", required=True,
                        type=port_expression, metavar="[IP address]:[port]" )
    parser.add_argument("-c", "--connect", help="port to connect", required=True,
                        type=port_expression, metavar="[IP address]:[port]" )
    args = parser.parse_args()
    
    proxy = TCPProxy( args.listen[0], args.listen[1], args.connect[0], args.connect[1])
    
    proxy.start()
    proxy.run()
