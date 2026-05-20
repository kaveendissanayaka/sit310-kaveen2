#!/usr/bin/env python3

import rospy
import math

from geometry_msgs.msg import Twist, Point
from turtlesim.msg import Pose
from std_msgs.msg import Float64


class TurtleController:
    def __init__(self):
        rospy.init_node("straights_and_turns_turtle")

        self.pose = None
        self.total_distance = 0.0

        self.cmd_pub = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)

        rospy.Subscriber("/turtle1/pose", Pose, self.pose_callback)
        rospy.Subscriber("/turtle_dist", Float64, self.distance_callback)

        rospy.Subscriber("/goal_distance", Float64, self.goal_distance_callback)
        rospy.Subscriber("/goal_angle", Float64, self.goal_angle_callback)
        rospy.Subscriber("/goal_position", Point, self.goal_position_callback)

        self.mode = "idle"

        self.start_x = 0.0
        self.start_y = 0.0
        self.start_theta = 0.0

        self.goal_distance = 0.0
        self.goal_angle = 0.0

        self.goal_x = 0.0
        self.goal_y = 0.0

        self.linear_speed = 1.0
        self.angular_speed = 1.0

        self.distance_tolerance = 0.05
        self.angle_tolerance = 0.03
        self.position_tolerance = 0.08

        rospy.loginfo("Turtle controller ready.")
        rospy.loginfo("Publish goals using /goal_distance, /goal_angle, or /goal_position.")

    def pose_callback(self, msg):
        self.pose = msg

    def distance_callback(self, msg):
        self.total_distance = msg.data

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def stop_turtle(self):
        msg = Twist()
        self.cmd_pub.publish(msg)

    def goal_distance_callback(self, msg):
        if self.pose is None:
            rospy.logwarn("No pose received yet.")
            return

        self.goal_distance = msg.data

        if abs(self.goal_distance) < 0.001:
            rospy.loginfo("Distance goal is 0. Turtle will not move.")
            self.mode = "idle"
            self.stop_turtle()
            return

        self.start_x = self.pose.x
        self.start_y = self.pose.y
        self.mode = "distance"

        rospy.loginfo("New distance goal: %.2f", self.goal_distance)

    def goal_angle_callback(self, msg):
        if self.pose is None:
            rospy.logwarn("No pose received yet.")
            return

        self.goal_angle = msg.data

        if abs(self.goal_angle) < 0.001:
            rospy.loginfo("Angle goal is 0. Turtle will not rotate.")
            self.mode = "idle"
            self.stop_turtle()
            return

        self.start_theta = self.pose.theta
        self.mode = "angle"

        rospy.loginfo("New angle goal: %.2f radians", self.goal_angle)

    def goal_position_callback(self, msg):
        if self.pose is None:
            rospy.logwarn("No pose received yet.")
            return

        self.goal_x = msg.x
        self.goal_y = msg.y

        self.mode = "position_rotate"

        rospy.loginfo("New position goal: x=%.2f, y=%.2f", self.goal_x, self.goal_y)

    def control_distance(self):
        msg = Twist()

        travelled = math.sqrt(
            (self.pose.x - self.start_x) ** 2 +
            (self.pose.y - self.start_y) ** 2
        )

        if travelled >= abs(self.goal_distance) - self.distance_tolerance:
            rospy.loginfo("Distance goal reached.")
            self.mode = "idle"
            self.stop_turtle()
            return

        if self.goal_distance > 0:
            msg.linear.x = self.linear_speed
        else:
            msg.linear.x = -self.linear_speed

        self.cmd_pub.publish(msg)

    def control_angle(self):
        msg = Twist()

        turned = self.normalize_angle(self.pose.theta - self.start_theta)

        error = self.goal_angle - turned

        if abs(error) <= self.angle_tolerance:
            rospy.loginfo("Angle goal reached.")
            self.mode = "idle"
            self.stop_turtle()
            return

        if error > 0:
            msg.angular.z = self.angular_speed
        else:
            msg.angular.z = -self.angular_speed

        self.cmd_pub.publish(msg)

    def control_position_rotate(self):
        msg = Twist()

        dx = self.goal_x - self.pose.x
        dy = self.goal_y - self.pose.y

        target_angle = math.atan2(dy, dx)
        angle_error = self.normalize_angle(target_angle - self.pose.theta)

        if abs(angle_error) <= self.angle_tolerance:
            rospy.loginfo("Facing target position. Moving straight.")
            self.mode = "position_straight"
            self.stop_turtle()
            return

        if angle_error > 0:
            msg.angular.z = self.angular_speed
        else:
            msg.angular.z = -self.angular_speed

        self.cmd_pub.publish(msg)

    def control_position_straight(self):
        msg = Twist()

        dx = self.goal_x - self.pose.x
        dy = self.goal_y - self.pose.y

        distance_error = math.sqrt(dx ** 2 + dy ** 2)

        if distance_error <= self.position_tolerance:
            rospy.loginfo("Position goal reached.")
            self.mode = "idle"
            self.stop_turtle()
            return

        target_angle = math.atan2(dy, dx)
        angle_error = self.normalize_angle(target_angle - self.pose.theta)

        if abs(angle_error) > 0.15:
            rospy.loginfo("Angle drift detected. Rotating again.")
            self.mode = "position_rotate"
            self.stop_turtle()
            return

        msg.linear.x = self.linear_speed
        self.cmd_pub.publish(msg)

    def run(self):
        rate = rospy.Rate(20)

        while not rospy.is_shutdown():
            if self.pose is None:
                rate.sleep()
                continue

            if self.mode == "distance":
                self.control_distance()

            elif self.mode == "angle":
                self.control_angle()

            elif self.mode == "position_rotate":
                self.control_position_rotate()

            elif self.mode == "position_straight":
                self.control_position_straight()

            else:
                self.stop_turtle()

            rate.sleep()


if __name__ == "__main__":
    controller = TurtleController()
    controller.run()
