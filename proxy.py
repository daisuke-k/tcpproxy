import tornado.tcpserver
import tornado.tcpclient
import tornado.gen

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
        newpair.stream_add( stream_handler )
        stream_handler.set_stream( stream )
       
        new_stream_handler = self.streamhandler( newpair )
        newpair.stream_add( new_stream_handler )
        try:
            stream_connect = yield self.tcpclient.connect( self.connect_addr, self.connect_port )
            new_stream_handler.set_stream( stream_connect )
        except ConnectionError:
            newpair.close()
    
   def handle_close(self, pair ):
        self.streampairs.remove( pair )