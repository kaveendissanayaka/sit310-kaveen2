#!/usr/bin/env python3

import rospy
import math

from turtlesim.msg import Pose
from std_msgs.msg import Float64


class DistanceTurtle:
    def __init__(self):
        rospy.init_node("distance_turtle")

        self.previous_x = None
        self.previous_y = None
        self.total_distance = 0.0

        rospy.Subscriber("/turtle1/pose", Pose, self.pose_callback)

        self.distance_pub = rospy.Publisher(
            "/turtle_dist",
            Float64,
            queue_size=10
        )

        rospy.loginfo("Distance turtle node started.")

    def pose_callback(self, msg):
        current_x = msg.x
        current_y = msg.y

        if self.previous_x is None or self.previous_y is None:
            self.previous_x = current_x
            self.previous_y = current_y
            return

        dx = current_x - self.previous_x
        dy = current_y - self.previous_y

        distance_step = math.sqrt(dx ** 2 + dy ** 2)
        self.total_distance += distance_step

        self.previous_x = current_x
        self.previous_y = current_y

        self.distance_pub.publish(Float64(self.total_distance))

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    node = DistanceTurtle()
    node.run()
