import tornado.ioloop
import logging

LOG=logging.getLogger(__name__)

class TCPStreamHandler():
    def __init__(self, stream, streampair ):
        self.streampair = streampair
        self._write_buf = b''
       
        if isinstance(stream, tornado.concurrent.Future):
            tornado.ioloop.IOLoop.current().add_future( stream, self.handle_connection_established )
            self.stream = None
        else:
            self.stream = stream
            self._set_handlers()
    
    def handle_connection_established(self, f):
        if f.exception() is not None:
            self.handle_close()
            return
        
        self.stream = f.result()
        self._set_handlers()
        self.write() 
    
    def handle_read(self, data):
        LOG.debug("Read: {0}".format(repr(data)))
        self.stream.read_bytes(4096, callback=self.handle_read, partial=True)
        self.streampair.handle_read( self, data )
    
    def write(self, data=None):
        if data is not None:
            LOG.debug("Write: {0}".format(repr(data)))
            self._write_buf = self._write_buf + data
        if self.stream is not None:
            self.stream.write( self._write_buf )
            self._write_buf = b''
    
    def close(self):
        if self.stream is not None:
            self.stream.close(self)
        
    def handle_close(self):
        self.streampair.close(self)

    def _set_handlers(self):
        self.stream.read_bytes(4096, callback=self.handle_read, partial=True)
        self.stream.set_close_callback( self.handle_close )
        

class TCPStreamPair():
    def __init__(self):
        self.streams = []
        self.close_handler = None
    
    def stream_add(self, streamhandler ):
        self.streams.append( streamhandler )
    
    def handle_read(self, stream, data ):
        send_stream = self.streams[1] if stream is self.streams[0] \
                            else self.streams[0]
        
        send_stream.write( data )
    
    def close(self, stream ):
        for s in self.streams:
            s.close()
        if self.close_handler is not None:
            self.close_handler( self )
    
    def set_close_handler(self, handler ):
        self.close_handler = handler