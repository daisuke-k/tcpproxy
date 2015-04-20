class Conn():
    def __init__(self, sock):
        self.sock = sock
        pass

    def recv(self):
        pass

    def send(self, msg):
        pass

class ConnPair():
    def __init__(self):
        self.connections = []
        self._socks = []
        self._sock_to_conn = {}
        pass

    def conn_add(self, conn):
        if conn not in self.connections:
            self.connections.append( conn )
            self._socks.append( conn.sock )
            self._sock_to_conn[conn.sock] = conn

    def recv(self, sock):
        pass

    def close(self):
        for conn in self.connections:
            self._socks.remove( conn.sock )
            del self._sock_to_conn[conn.sock]

    @property
    def socks(self):
        return None

    @socks.getter
    def socks(self):
        if len(self._socks) == 1:
            return []
        return self._socks

    def _find_conn(self, sock):
        if sock in self._sock_to_conn:
            return self._sock_to_conn[sock]
        return None

