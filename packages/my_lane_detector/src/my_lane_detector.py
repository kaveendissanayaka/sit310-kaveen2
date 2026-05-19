#!/usr/bin/env python3

import os
import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage


class LaneDetector:
    def __init__(self):
        rospy.init_node("my_lane_detector", anonymous=True)
        self.bridge = CvBridge()

        # Default topic for the provided some_lane_images.bag file.
        # For your own robot bag, run with:
        # python3 my_lane_detector.py _image_topic:=/<robot_name>/camera_node/image/compressed
        self.image_topic = rospy.get_param("~image_topic", "/akandb/camera_node/image/compressed")
        self.save_dir = rospy.get_param("~save_dir", "/data/task6_outputs")
        os.makedirs(self.save_dir, exist_ok=True)

        rospy.Subscriber(self.image_topic, CompressedImage, self.image_callback, queue_size=1)
        rospy.loginfo("Lane detector subscribing to: %s", self.image_topic)
        rospy.loginfo("Press 's' in an OpenCV window to save screenshots, or 'q' to quit.")

    def draw_lines(self, image, lines, color, thickness=3):
        if lines is None:
            return image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
            cv2.circle(image, (x1, y1), 3, color, -1)
            cv2.circle(image, (x2, y2), 3, color, -1)
        return image

    def image_callback(self, msg):
        # ROS compressed image -> OpenCV BGR image
        frame = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

        # Crop lower road area only
        h, w = frame.shape[:2]
        crop_start = int(h * 0.45)
        cropped = frame[crop_start:h, 0:w]

        # HSV conversion for colour filtering
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

        # White lane threshold in HSV
        lower_white = np.array([0, 0, 170])
        upper_white = np.array([180, 80, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Yellow lane threshold in HSV
        lower_yellow = np.array([15, 70, 70])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Clean the masks slightly
        kernel = np.ones((5, 5), np.uint8)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
        yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)

        # Filtered images shown in BGR windows
        white_filtered = cv2.bitwise_and(cropped, cropped, mask=white_mask)
        yellow_filtered = cv2.bitwise_and(cropped, cropped, mask=yellow_mask)

        # Canny edge detection on cropped image
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
        canny_edges = cv2.Canny(gray_blur, 50, 150)

        # Hough Transform on white/yellow mask edges
        white_edges = cv2.Canny(white_mask, 50, 150)
        yellow_edges = cv2.Canny(yellow_mask, 50, 150)

        white_lines = cv2.HoughLinesP(
            white_edges, rho=1, theta=np.pi / 180, threshold=20,
            minLineLength=25, maxLineGap=10
        )
        yellow_lines = cv2.HoughLinesP(
            yellow_edges, rho=1, theta=np.pi / 180, threshold=20,
            minLineLength=25, maxLineGap=10
        )

        hough_output = cropped.copy()
        # Green = white-lane Hough lines, Red = yellow-lane Hough lines
        self.draw_lines(hough_output, white_lines, (0, 255, 0), 3)
        self.draw_lines(hough_output, yellow_lines, (0, 0, 255), 3)

        # Display windows for recording videos/screenshots
        cv2.imshow("01 Cropped Road", cropped)
        cv2.imshow("02 White Filtered", white_filtered)
        cv2.imshow("03 Yellow Filtered", yellow_filtered)
        cv2.imshow("04 Canny Edges", canny_edges)
        cv2.imshow("05 Hough Lines", hough_output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            cv2.imwrite(os.path.join(self.save_dir, "good_frame.jpg"), frame)
            cv2.imwrite(os.path.join(self.save_dir, "cropped_road.jpg"), cropped)
            cv2.imwrite(os.path.join(self.save_dir, "white_filtered.jpg"), white_filtered)
            cv2.imwrite(os.path.join(self.save_dir, "yellow_filtered.jpg"), yellow_filtered)
            cv2.imwrite(os.path.join(self.save_dir, "canny_edges.jpg"), canny_edges)
            cv2.imwrite(os.path.join(self.save_dir, "hough_lines.jpg"), hough_output)
            rospy.loginfo("Saved screenshots to %s", self.save_dir)
        elif key == ord("q"):
            rospy.signal_shutdown("User pressed q")

    def run(self):
        rospy.spin()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        LaneDetector().run()
    except rospy.ROSInterruptException:
        pass
