import socket
import select

TCP_CONNECT_TIMEOUT = 3

class TCPConn():
    def __init__(self, sock):
        self.sock = sock
        self.buf = b''
    
    def recv(self):
        self.buf = self.buf + self.sock.recv(4096)
        return len(self.buf)
        
    def send(self, msg):
        self.sock.sendall( msg ) 
        
    def cut_buf(self, cut_len ):
        if cut_len < len(self.buf):
            self.buf = self.buf[cut_len:]
        else:
            self.buf = b''

class TCPConnPair():
    def __init__ (self):
        self.connections = []
        self._socks = []

    def conn_add(self, tcpconn):
        self.connections.append( tcpconn )
        self._socks.append( tcpconn.sock )
    
    @property
    def socks(self):
        return None
     
    @socks.getter    
    def socks(self):
        if len(self._socks) == 1:
            return []
        return self._socks
    
    def recv(self, sock):
        if sock is self.connections[0].sock:
            conn = self.connections[0]
            send_conn = self.connections[1]
        else:
            conn = self.connections[1]
            send_conn = self.connections[0]
        
        msg_len = conn.recv()
        if msg_len != 0:
            send_conn.send( conn.buf )
            conn.cut_buf( msg_len )
        else:
            return False
        return True
    
    def close(self):
        for conn in self.connections:
            self._socks.remove( conn.sock )
            conn.sock.close()
    
class ConnPairs():
    def __init__(self):
        self.pairs = []
        self.sock_index = {}
    
    def add(self, pair):
        if pair not in self.pairs:
            self.pairs.append( pair )
            for sock in pair.socks:
                self.sock_index[sock] = pair
    
    def remove(self, pair):
        if pair in self.pairs:
            self.pairs.remove( pair )
            for sock in pair.socks:
                del self.sock_index[sock]
    
    def find_pair(self, sock):
        return self.sock_index[sock]
        

class TCPProxy():
    def __init__(self, listen_addr, listen_port, connect_addr, connect_port ):
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.connect_addr = connect_addr
        self.connect_port = connect_port

        self.read_socks = []
        self.pairs = ConnPairs()

    def start(self):
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.read_socks.append( self.serversock )

        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind( (self.listen_addr, self.listen_port) )
        self.serversock.listen(5)
    
    def run(self):
        while True:
            rready, wready, errready = select.select( self.read_socks, [], [] )
            for sock in rready:
                if sock is self.serversock:
                   self.on_accept( sock )
                else:
                    pair = self.pairs.find_pair( sock )
                    if not pair.recv( sock ):
                        self.on_close( pair )
                    
    def on_accept(self, sock):
        newpair = TCPConnPair()

        clientsock, address = sock.accept()
        newpair.conn_add( TCPConn( clientsock ) )
       
        try: 
            sock_connect = socket.create_connection( (self.connect_addr, self.connect_port), TCP_CONNECT_TIMEOUT )
        except OSError as msg:
            self.on_close( newpair )
            return

        newpair.conn_add( TCPConn( sock_connect ) )
        
        self.pairs.add( newpair )
        self.read_socks.extend( newpair.socks )
    
    def on_close(self, pair ):
        for sock in pair.socks:
            if sock in self.read_socks:
                self.read_socks.remove( sock )

        pair.close()

        self.pairs.remove( pair )