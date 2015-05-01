#import tornado.ioloop
import tornado.gen
import tornado.iostream
import logging

LOG=logging.getLogger(__name__)

class TCPStreamHandler():
    def __init__(self, streampair ):
        self.streampair = streampair
        self.stream = None
        self.address = ""
        
    def set_stream(self, stream, address ):
        self.stream = stream
        self.address = address
        LOG.debug("Set a stream for {0}".format(address))
        self.run_read()
        
    def receive(self, data ):
        return data
    
    @tornado.gen.coroutine 
    def run_read(self):
        while True:
            try:
                LOG.debug("Waiting for data...")
                data = yield self.stream.read_bytes(8, partial=True)
                LOG.debug("Read: {0}".format(repr(data)))

                msg = self.receive( data )
                self.streampair.handle_read( self, msg )
            except tornado.iostream.StreamClosedError:
                LOG.debug("Connection to {0} is closed".format(self.address))
                self.streampair.close()
                break

    def send(self, data ):
        self.write( data )
         
    def write(self, data=None):
        LOG.debug("Write: {0}".format(repr(data)))
        if self.stream is not None:
            self.stream.write( data )
    
    def close(self):
        if self.stream is not None:
            self.stream.close(self)

class TCPStreamPair():
    def __init__(self):
        self.streams = []
        self.close_handler = None
    
    def stream_add(self, streamhandler ):
        self.streams.append( streamhandler )
    
    def handle_read(self, stream, data ):
        send_stream = self.streams[1] if stream is self.streams[0] \
                            else self.streams[0]
        
        send_stream.send( data )
    
    def close(self ):
        for s in self.streams:
            s.close()
        if self.close_handler is not None:
            self.close_handler( self )
    
    def set_close_handler(self, handler ):
        self.close_handler = handler
