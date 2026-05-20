# Import Dependencies
import rospy
import math
from std_msgs.msg import Float64
from turtlesim.msg import Pose


class DistanceReader:
    def __init__(self):

        # Initialize the node
        rospy.init_node('turtlesim_distance_node', anonymous=True)

        # Variables to store previous position and total distance
        self.prev_x = None
        self.prev_y = None
        self.total_distance = 0.0

        # Initialize subscriber: input the topic name, message type and callback signature
        rospy.Subscriber("/turtle1/pose", Pose, self.callback)

        # Initialize publisher: input the topic name, message type and msg queue size
        self.distance_publisher = rospy.Publisher('/turtle_dist', Float64, queue_size=10)

        # Printing to the terminal, ROS style
        rospy.loginfo("Initialized node!")

        # This blocking function call keeps python from exiting until node is stopped
        rospy.spin()

    # Whenever a message is received from the specified subscriber, this function will be called
    def callback(self, msg):
        rospy.loginfo("Turtle Position: %s %s", msg.x, msg.y)

        current_x = msg.x
        current_y = msg.y

        # First message: just store the initial position
        if self.prev_x is None or self.prev_y is None:
            self.prev_x = current_x
            self.prev_y = current_y
            return

        # Calculate distance moved since last pose
        dx = current_x - self.prev_x
        dy = current_y - self.prev_y
        step_distance = math.sqrt(dx**2 + dy**2)

        # Add to total distance
        self.total_distance += step_distance

        # Publish total distance
        distance_msg = Float64()
        distance_msg.data = self.total_distance
        self.distance_publisher.publish(distance_msg)

        # Update previous position
        self.prev_x = current_x
        self.prev_y = current_y


if __name__ == '__main__':
    try:
        distance_reader_class_instance = DistanceReader()
    except rospy.ROSInterruptException:
        pass
