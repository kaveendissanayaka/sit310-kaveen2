#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped, FSMState


class DriveSquare:
    def __init__(self):
        rospy.init_node("drive_square_node", anonymous=False)

        self.robot_name = "akandb"

        self.cmd_topic = "/" + self.robot_name + "/car_cmd_switch_node/cmd"
        self.fsm_topic = "/" + self.robot_name + "/fsm_node/mode"

        self.cmd_msg = Twist2DStamped()
        self.is_moving = False

        self.pub = rospy.Publisher(self.cmd_topic, Twist2DStamped, queue_size=1)
        rospy.Subscriber(self.fsm_topic, FSMState, self.fsm_callback, queue_size=1)

        # Tune these values for your robot
        self.forward_speed = 0.3
        self.turn_speed = 4.0

        # These are the wait parameters for the task
        self.straight_time = 3.5
        self.turn_time = 1.5

        rospy.on_shutdown(self.stop_robot)

    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING" and not self.is_moving:
            self.is_moving = True
            rospy.sleep(1)
            self.move_robot()
            self.is_moving = False

    def publish_cmd(self, v, omega):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = v
        self.cmd_msg.omega = omega
        self.pub.publish(self.cmd_msg)

    def stop_robot(self):
        self.publish_cmd(0.0, 0.0)
        rospy.sleep(0.2)

    def move_forward(self):
        rospy.loginfo("Moving forward")
        start = rospy.Time.now().to_sec()

        while not rospy.is_shutdown():
            if rospy.Time.now().to_sec() - start >= self.straight_time:
                break

            self.publish_cmd(self.forward_speed, 0.0)
            rospy.sleep(0.05)

        self.stop_robot()

    def turn_left(self):
        rospy.loginfo("Turning left")
        start = rospy.Time.now().to_sec()

        while not rospy.is_shutdown():
            if rospy.Time.now().to_sec() - start >= self.turn_time:
                break

            self.publish_cmd(0.0, self.turn_speed)
            rospy.sleep(0.05)

        self.stop_robot()

    def move_robot(self):
        rospy.loginfo("Starting open loop square")

        for i in range(4):
            rospy.loginfo("Side %d", i + 1)
            self.move_forward()
            rospy.sleep(0.5)

            self.turn_left()
            rospy.sleep(0.5)

        self.stop_robot()
        rospy.loginfo("Finished square")

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        duckiebot_movement = DriveSquare()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
