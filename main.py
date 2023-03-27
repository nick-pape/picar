import zmq
from server import Server

server = Server()

try:
    while True:
        server.execute()
        
except zmq.error.ZMQError:
    print("Client disconnected")

except KeyboardInterrupt:
    print("Interrupted")

finally:
    server.close()