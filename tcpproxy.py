import socket
import select

class TCPConnPair():
    def __init__ (self):
        self.connections = []

    def sock_add(self, sock):
        self.connections.append( sock )
        
    def socks(self):
        if len(self.connections) != 2:
            return []
        return self.connections
    
    def recv(self, sock):
        send_sock = self.connections[0] if sock is self.connections[1] else self.connections[1]
        
        msg = sock.recv(4096)
        if len(msg) != 0:
            send_sock.sendall( msg )
        else:
            return False
        return True
    
    def close(self):
        for sock in self.connections:
            sock.close()
    
class TCPConnPairs():
    def __init__(self):
        self.pairs = []
        self.sock_index = {}
    
    def add(self, pair):
        self.pairs.append( pair )
        for sock in pair.socks():
            self.sock_index[sock] = pair
    
    def remove(self, pair):
        self.pairs.remove( pair )
        for sock in pair.socks():
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
        self.pairs = TCPConnPairs()

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
        newpair.sock_add( clientsock )
        
        sock_connect = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        sock_connect.connect( (self.connect_addr, self.connect_port) )
        newpair.sock_add( sock_connect )
        
        self.pairs.add( newpair )
        self.read_socks.extend( newpair.socks() )
        return
    
    def on_close(self, pair ):
        pair.close()
        for sock in pair.socks():
            self.read_socks.remove( sock )
        self.pairs.remove( pair )