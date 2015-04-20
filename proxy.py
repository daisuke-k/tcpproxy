import socket
import select

TCP_CONNECT_TIMEOUT = 3

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
        

class ConnProxy():
    def __init__(self, listen_addr, listen_port, connect_addr, connect_port,
            conn, connpair ):
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.connect_addr = connect_addr
        self.connect_port = connect_port
        
        if conn is None:
            self.conn = TCPConn
        else:
            self.conn = conn
        
        if connpair is None:
            self.connpair = TCPConnPair
        else:
            self.connpair = connpair

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
        newpair = self.connpair()

        clientsock, address = sock.accept()
        newpair.conn_add( self.conn( clientsock ) )
       
        try: 
            sock_connect = socket.create_connection(
                (self.connect_addr, self.connect_port), TCP_CONNECT_TIMEOUT )
        except OSError as msg:
            self.on_close( newpair )
            return

        newpair.conn_add( self.conn( sock_connect ) )
        
        self.pairs.add( newpair )
        self.read_socks.extend( newpair.socks )
    
    def on_close(self, pair ):
        for sock in pair.socks:
            if sock in self.read_socks:
                self.read_socks.remove( sock )

        pair.close()
        self.pairs.remove( pair )
