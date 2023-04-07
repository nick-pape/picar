import zmq
import argparse

from server import Server

# Initialize parser
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help = "IP Address of the client (Raspberry Pi)", default='10.0.0.26')
    parser.add_argument("--mock", action='store_true', help = "True if we should open in testing mode", default=False)
    return parser.parse_args()


def main(args):
    server = Server()

    print("Server ready!")

    try:
        while True:
            server.execute()
            
    except zmq.error.ZMQError:
        print("Client disconnected")

    except KeyboardInterrupt:
        print("Interrupted")

    except TimeoutError:
        print("Server Timeout")

    finally:
        print("Closing Server")
        server.close()

main(getArguments())
print("Exiting")