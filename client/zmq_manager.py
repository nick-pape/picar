import zmq

class Socket():
    def __init__(self, context, ipAddress):
        self._socket = context.socket(zmq.REQ)
        self._socket.setsockopt(zmq.LINGER, 0)
        socket_address = f"tcp://{ipAddress}:5555"
        self._socket.connect(socket_address)   # connect to server
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def recv_timeout(self, timeout=10000):
        socks = dict(self._poller.poll(timeout))  # timeout after 1s
        if self._socket in socks and socks[self._socket] == zmq.POLLIN:
            return self._socket.recv().decode()
        else:
            raise TimeoutError('Server Disconnected')
        
    def send(self, data):
        self._socket.send(data)

    def close(self):
        self._poller.unregister(self._socket)
        del self._poller
        self._socket.close()
        del self._socket

class _ZmqManager():
    def __init__(self):
        self.context = zmq.Context()
        self.sockets: list[Socket] = []

    def getSocket(self, ipAddress):
        socket = Socket(self.context, ipAddress)
        self.sockets.append(socket)
        return socket
    
    def close(self):
        for socket in self.sockets:
            socket.close()

        self.sockets = []
        self.context.term()

ZmqManager = _ZmqManager()