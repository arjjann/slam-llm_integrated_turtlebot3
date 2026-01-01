#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node

def generate_launch_description():
    # Configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='3.0')
    y_pose = LaunchConfiguration('y_pose', default='4.0')
    
    # Paths
    pkg_share = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    world_path = os.path.join(pkg_share, 'worlds', 'turtlebot3_house.world')
    robot_xacro_path = os.path.join(pkg_share, 'urdf', 'turtlebot3_burger.urdf.xacro')
    
    # Robot description
    robot_description = ParameterValue(
        Command(['xacro ', robot_xacro_path]),
        value_type=str
    )
    
    # Gazebo server (with GUI enabled)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'world': world_path,
            'gz_args': '-r',  # Run immediately
        }.items()
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Spawn robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-entity', 'turtlebot3_burger',
            '-topic', '/robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.15'
        ],
        output='screen'
    )
    
    # Bridge for joint states (critical!)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/turtlebot3_burger/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        output='screen'
    )
    
    # Environment variables
    set_env_vars = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(pkg_share, 'models')
    )
    
    # Assemble launch description
    ld = LaunchDescription()
    ld.add_action(set_env_vars)
    ld.add_action(gz_sim)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_robot)
    ld.add_action(bridge)
    
    return ld