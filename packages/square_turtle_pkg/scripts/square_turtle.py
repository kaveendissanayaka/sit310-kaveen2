#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

current_pose = None

def pose_callback(msg):
    global current_pose
    current_pose = msg

def move_forward(pub, speed, distance):
    global current_pose

    while current_pose is None and not rospy.is_shutdown():
        rospy.sleep(0.1)

    start_x = current_pose.x
    start_y = current_pose.y

    vel = Twist()
    vel.linear.x = speed

    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        travelled = math.sqrt((current_pose.x - start_x) ** 2 + (current_pose.y - start_y) ** 2)

        if travelled >= distance:
            break

        pub.publish(vel)
        rate.sleep()

    vel.linear.x = 0
    pub.publish(vel)
    rospy.sleep(0.3)

def turn_90_degrees(pub, angular_speed):
    vel = Twist()
    vel.angular.z = angular_speed

    duration = math.pi / 2 / angular_speed
    start_time = rospy.Time.now().to_sec()

    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        current_time = rospy.Time.now().to_sec()
        if current_time - start_time >= duration:
            break

        pub.publish(vel)
        rate.sleep()

    vel.angular.z = 0
    pub.publish(vel)
    rospy.sleep(0.3)

def draw_square():
    rospy.init_node("square_turtle_node", anonymous=True)

    pub = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
    rospy.Subscriber("/turtle1/pose", Pose, pose_callback)

    rospy.sleep(1)

    side_length = 2.0
    forward_speed = 1.0
    angular_speed = 1.0

    rospy.loginfo("Square turtle node started. Drawing squares forever...")

    while not rospy.is_shutdown():
        for i in range(4):
            move_forward(pub, forward_speed, side_length)
            turn_90_degrees(pub, angular_speed)

if __name__ == "__main__":
    try:
        draw_square()
    except rospy.ROSInterruptException:
        pass
