import pygame
import time

import math

def convert_joystick_to_throttle(x, y):
    # Calculate the overall speed of the car based on the X position of the joystick
    speed = -y

    # Calculate the degree to which the car turns left or right based on the Y position of the joystick
    turn = -x

    # Calculate the left and right motor throttle values based on the speed and turn values
    left_throttle = speed - turn
    right_throttle = speed + turn

    # Clip the throttle values to the range of -1 to 1
    left_throttle = max(min(left_throttle, 1), -1)
    right_throttle = max(min(right_throttle, 1), -1)

    # Return the left and right motor throttle values as a tuple
    return (left_throttle, right_throttle)

def format_percentage(number):
    # Convert the number to a percentage
    percentage = number * 100

    # Round the percentage to the nearest whole number
    rounded_percentage = round(percentage)

    # Format the percentage as a string with a percent sign
    formatted_percentage = "{:.0f}%".format(rounded_percentage)

    # Return the formatted percentage
    return formatted_percentage

# Initialize Pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

def getThrottle():

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
            
     # Get the joystick axis values
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    # Print the joystick position to the console
    #print("Joystick X Position: {}".format(x_axis))
    #print("Joystick Y Position: {}".format(y_axis))

    left, right = convert_joystick_to_throttle(x_axis, y_axis)

    return left, right
