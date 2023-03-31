import zmq
import argparse

from client import Client

from drive import FourWheelDrivetrain, MockFourWheelDrivetrain
from camera import Camera, MockCamera

# Initialize parser
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help = "IP Address of the primary server", default='10.0.0.5')
    parser.add_argument("--mock", action='store_true', help = "True if we should open in testing mode", default=False)
    return parser.parse_args()

def main(args):
    client = Client(
        drive = FourWheelDrivetrain(),
        camera = Camera(),
        args = args
    ) if not args.mock else Client(
        drive = MockFourWheelDrivetrain(),
        camera = MockCamera(),
        args = args
    )

    print("Client ready!")

    try:
        while True:
            client.execute()        

    except zmq.error.ZMQError as e:
        print(f"Socket error: {e}")

    except KeyboardInterrupt:
        print("Interrupted")

    except TimeoutError:
        print("Server Timeout")

    finally:
        print("Closing Client")
        client.close()


main(getArguments())
print("Exiting")