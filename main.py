#!/usr/bin/python

import argparse
import logging
import signal

import tornado.ioloop

import proxy
import tcp

def on_sigint():
    print("Shutdown by keyboard interruption")
    tornado.ioloop.IOLoop.instance().stop()

def port_expression( string ):
    separated = string.rsplit(":", 1)
    if len(separated) != 2:
        raise argparse.ArgumentTypeError()
    return [ separated[0], int(separated[1]) ]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", help="port to listen", required=True,
                        type=port_expression, metavar="[IP address]:[port]" )
    parser.add_argument("-c", "--connect", help="port to connect", required=True,
                        type=port_expression, metavar="[IP address]:[port]" )
    args = parser.parse_args()
    
    server = proxy.ProxyServer( args.connect[0], args.connect[1], tcp.TCPStreamHandler,
                         tcp.TCPStreamPair, proxy.StreamPairs )
    server.listen( args.listen[1], address=args.listen[0] )

    ioloop = tornado.ioloop.IOLoop.instance()

    signal.signal( signal.SIGINT, lambda sig, froame: ioloop.add_callback_from_signal(on_sigint) )

    ioloop.start()