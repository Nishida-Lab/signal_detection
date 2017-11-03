#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Int8
from cv_bridge import CvBridge, CvBridgeError
import cv2

class SignalDisplayNode:

    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("center_cam/image_raw",Image,self.image_callback,queue_size=1)
        self.signal_sub = rospy.Subscriber('signal_info', Int8, self.signal_callback,queue_size=1)
        self.is_update_image = False

    def image_callback(self,data):
        self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        self.is_update_image = True
        
    def signal_callback(self,data):
        self.output = data.data
        if not self.is_update_image:
            return
        self.once()

    def once(self):
        frame = self.cv_image

        if self.output == 0:
            signal_state = "UNKOWN"
            color = (0,0,0)
        elif self.output == 1:
            signal_state = "GREEN"
            color = (0,255,0)
        else:
            signal_state = "RED"
            color = (0,0,255)

        message = " signal state : "+signal_state
        rospy.loginfo(rospy.get_caller_id() + '%s', message)

        cv2.putText(frame, signal_state, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('output_frame',frame)
        cv2.waitKey(3)

def main():
    signal_display_node = SignalDisplayNode()
    rospy.init_node('signal_detection_result', anonymous=True)
    rospy.spin()

if __name__ == '__main__':
    main()
