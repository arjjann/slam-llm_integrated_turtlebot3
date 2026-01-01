#!/usr/bin/env python3

import subprocess
import sys

def main():
    try:
        # Call ROS 2 launch to start TurtleBot3 world
        subprocess.run([
            "ros2", "launch", "turtlebot3_gazebo", "turtlebot3_house.launch.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching TurtleBot3 world: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
