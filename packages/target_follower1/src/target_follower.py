#!/usr/bin/env python3


import rospy

from duckietown_msgs.msg import Twist2DStamped

from duckietown_msgs.msg import AprilTagDetectionArray



class Target_Follower:


    def __init__(self):


        # Initialize ROS node

        rospy.init_node('target_follower_node', anonymous=True)


        # Shutdown handler

        rospy.on_shutdown(self.clean_shutdown)


        # CHANGE THIS TO YOUR ROBOT NAME

        self.robot_name = "mybota002413an"


        # Publisher

        self.cmd_vel_pub = rospy.Publisher(

            f'/{self.robot_name}/car_cmd_switch_node/cmd',

            Twist2DStamped,

            queue_size=1

        )


        # Subscriber

        rospy.Subscriber(

            f'/{self.robot_name}/apriltag_detector_node/detections',

            AprilTagDetectionArray,

            self.tag_callback,

            queue_size=1

        )


        rospy.loginfo("Target follower node started.")


        rospy.spin()



    # Callback function

    def tag_callback(self, msg):


        self.move_robot(msg.detections)



    # Clean shutdown

    def clean_shutdown(self):


        rospy.loginfo("Shutting down. Stopping robot...")

        self.stop_robot()



    # Stop robot completely

    def stop_robot(self):


        cmd_msg = Twist2DStamped()

        cmd_msg.header.stamp = rospy.Time.now()


        cmd_msg.v = 0.0

        cmd_msg.omega = 0.0


        self.cmd_vel_pub.publish(cmd_msg)



    # Main movement function

    def move_robot(self, detections):


        cmd_msg = Twist2DStamped()

        cmd_msg.header.stamp = rospy.Time.now()


        ###################################################

        # TASK 1 - SEEK OBJECT FEATURE

        ###################################################


        # If no object/tag detected

        if len(detections) == 0:


            rospy.loginfo("No object detected. Seeking object...")


            # Rotate slowly to search

            cmd_msg.v = 0.0

            cmd_msg.omega = 1.0


            self.cmd_vel_pub.publish(cmd_msg)


            return



        ###################################################

        # TASK 2 - LOOK AT OBJECT FEATURE

        ###################################################


        # Get tag position

        x = detections[0].transform.translation.x

        y = detections[0].transform.translation.y

        z = detections[0].transform.translation.z


        rospy.loginfo("Object detected")

        rospy.loginfo("x: %f", x)

        rospy.loginfo("y: %f", y)

        rospy.loginfo("z: %f", z)


        ###################################################

        # Proportional Controller

        ###################################################


        # Error is horizontal displacement

        error = x


        # Proportional gain

        k_p = 3.0


        # Compute angular velocity

        omega = -k_p * error


        ###################################################

        # Velocity Limits

        ###################################################


        # Maximum turning speed

        if omega > 3.0:

            omega = 3.0


        elif omega < -3.0:

            omega = -3.0


        ###################################################

        # Dead Zone

        ###################################################


        # Prevent shaking when object is centered

        if abs(error) < 0.03:

            omega = 0.0


        ###################################################

        # Publish Velocity

        ###################################################


        # No forward/backward motion

        cmd_msg.v = 0.0


        # Only rotation

        cmd_msg.omega = omega


        self.cmd_vel_pub.publish(cmd_msg)



if __name__ == '__main__':


    try:

        target_follower = Target_Follower()


    except rospy.ROSInterruptException:

        pass
