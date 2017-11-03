#!/usr/bin/env python
import rospy
from std_msgs.msg import Int8

def callback(data):

    if data.data == 0:
        signal_state = "UNKOWN"
    elif data.data == 1:
        signal_state = "GREEN"
    else:
        signal_state = "RED"

    message = " signal state : "+signal_state
    rospy.loginfo(rospy.get_caller_id() + '%s', message)


def signal_subscriber():

    rospy.init_node('signal_subscriber', anonymous=True)
    rospy.Subscriber('signal_info', Int8, callback)
    rospy.spin()

if __name__ == '__main__':
    signal_subscriber()
