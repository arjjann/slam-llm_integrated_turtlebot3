import os
import subprocess
import time
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from llm import azure_llm 
from langchain_openai import AzureChatOpenAI
from langchain.tools import tool
from rosa import ROSA, RobotSystemPrompts

gazebo_launch = subprocess.Popen([
    "ros2", "launch", "turtlebot3_gazebo", "turtlebot3_house.launch.py"
])
time.sleep(5)

class CommandRobot(Node): 
    def __init__(self):
        super().__init__("command_robot")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)

    def send(self, lin=0.0, ang=0.0):
        msg = Twist()
        msg.linear.x = float(lin)
        msg.angular.z = float(ang)
        self.pub.publish(msg)

rclpy.init()
commander = CommandRobot()

@tool
def move_forward(distance: float) -> str:
    """Move the robot forward or backward by given meters."""
    speed = 0.5
    duration = abs(distance / speed)
    dt = 0.1
    t = 0.0

    while t < duration:
        commander.send(lin=speed if distance > 0 else -speed)
        time.sleep(dt)
        t += dt

    commander.send(0, 0)
    return f"Moved {distance} meters"


@tool
def turn(angle: float) -> str:
    """Rotate robot in degrees (positive = anticlockwise)."""
    speed = 0.5
    duration = abs(math.radians(angle) / speed)
    dt = 0.1
    t = 0.0

    while t < duration:
        commander.send(ang=speed if angle > 0 else -speed)
        time.sleep(dt)
        t += dt

    commander.send(0, 0)
    return f"Turned {angle} degrees"


@tool
def circle(radius: float) -> str:
    """Make one full circle with the given radius in meters."""
    if radius <= 0:
        return "Radius must be greater than zero"

    linear_speed = 0.5
    angular_speed = linear_speed / radius
    duration = (2 * math.pi * radius) / linear_speed
    dt = 0.1
    t = 0.0

    while t < duration:
        commander.send(lin=linear_speed, ang=angular_speed)
        time.sleep(dt)
        t += dt

    commander.send(0, 0)
    return f"Completed a circle of radius {radius} meters"


# -------------------- AGENT --------------------
prompts = RobotSystemPrompts(
    embodiment_and_persona=(
        "You control a differential-drive robot in Gazebo. "
        "You can move forward, backward, turn, and drive in a circle. "
        "You may combine multiple actions."
    )
)

agent = ROSA(
    ros_version=2,
    llm=azure_llm,
    tools=[move_forward, turn, circle],
    prompts=prompts,
)
# -------------------- MAIN LOOP --------------------
print("LLM Robot Controller running (q to quit)")

try:
    while True:
        cmd = input("Command: ")
        if cmd.lower() in ["q", "quit", "exit"]:
            break
        print("Robot:", agent.invoke(cmd))

finally:
    commander.destroy_node()
    rclpy.shutdown()
    gazebo_launch.terminate()
    print(" Shutdown complete")
