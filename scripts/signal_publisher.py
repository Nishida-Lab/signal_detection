#!/usr/bin/env python
import rospy
from std_msgs.msg import Int8
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2

from detection_class import *

class SignalDetecorNode:

    def __init__(self):
        rospy.init_node('signal_detector', anonymous=True)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("center_cam/image_raw",Image,self.callback, queue_size=1, buff_size=2**24)
        self.signal_pub = rospy.Publisher('signal_info', Int8, queue_size=1)
        self.detection = SignalDetecor()

    def callback(self,data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            state = self.detection(cv_image)
            self.signal_pub.publish(state)
            rospy.loginfo(str(state)+" is published.")
        except CvBridgeError as e:
            print(e)

def main():
    SignalDetecorNode()
    try:
        rospy.spin()
    except KeyboardInterrupt:
         print("Shutting down")

if __name__ == '__main__':
    main()
