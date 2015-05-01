import tornado.tcpserver
import tornado.tcpclient
import tornado.gen
import logging

LOG=logging.getLogger(__name__)

class StreamPairs():
    def __init__(self):
        self.pairs = []
    
    def add(self, pair):
        if pair not in self.pairs:
            self.pairs.append( pair )
    
    def remove(self, pair):
        if pair in self.pairs:
            self.pairs.remove( pair )
        
class ProxyServer(tornado.tcpserver.TCPServer):
   def __init__(self, connect_addr, connect_port, streamhandler, streampair, streampairs):
       super().__init__()
       self.connect_addr = connect_addr
       self.connect_port = connect_port
       self.streamhandler = streamhandler
       self.streampair = streampair
       self.streampairs = streampairs()
       self.tcpclient = tornado.tcpclient.TCPClient()

   @tornado.gen.coroutine
   def handle_stream(self, stream, address ):
        newpair = self.streampair()
        newpair.set_close_handler( self.handle_close )
        self.streampairs.add( newpair )
        
        stream_handler = self.streamhandler( newpair )
        stream_handler.set_stream( stream, address )
        newpair.stream_add( stream_handler )
        LOG.debug("A new connection is accepted from {0}".format(address))

        new_stream_handler = self.streamhandler( newpair )
        newpair.stream_add( new_stream_handler )
        LOG.debug("Trying to establish a new connection to {0}".format( (self.connect_addr, self.connect_port) ) )
        try:
            stream_connect = yield self.tcpclient.connect( self.connect_addr, self.connect_port )
            LOG.debug("Established a new connection to {0}".format( (self.connect_addr, self.connect_port) ) )

            new_stream_handler.set_stream( stream_connect, (self.connect_addr, self.connect_port) )
        except ConnectionError:
            LOG.debug("Failed to establish a new connection to {0}:{1}".format( self.connect_addr, self.connect_port) )
            newpair.close()
        
        LOG.debug("Created a new pair for {0}".format(address))
    
   def handle_close(self, pair ):
        self.streampairs.remove( pair )