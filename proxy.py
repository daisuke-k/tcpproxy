import tornado.tcpserver
import tornado.tcpclient

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

   def handle_stream(self, stream, address ):
        newpair = self.streampair()
        newpair.set_close_handler( self.handle_close )

        newpair.stream_add( self.streamhandler( stream, newpair ) )
       
        stream_connect = self.tcpclient.connect( self.connect_addr, self.connect_port )
        newpair.stream_add( self.streamhandler( stream_connect, newpair ) )
        
        self.streampairs.add( newpair )
    
   def handle_close(self, pair ):
        self.streampairs.remove( pair )