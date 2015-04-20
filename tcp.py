import connection

class TCPConn(connection.Conn):
    def __init__(self, sock):
        connection.Conn.__init__(self, sock )
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

class TCPConnPair(connection.ConnPair):
    def recv(self, sock):
        conn = self._find_conn( sock )
        send_conn = self.connections[1] if conn is self.connections[0] \
                else self.connections[0]
        
        msg_len = conn.recv()
        if msg_len != 0:
            send_conn.send( conn.buf )
            conn.cut_buf( msg_len )
        else:
            return False
        return True
    
    def close(self):
        for conn in self.connections:
            conn.sock.close()
        super(TCPConnPair, self).close()
