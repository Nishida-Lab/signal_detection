#!/usr/bin/env python
import cv2
import numpy as np
import os
import copy
import rospkg

class SignalDetecor:

    #generating diff image
    def diffimg(self, after, before):

        blue_before  = before[:,:,0]
        green_before = before[:,:,1]
        red_before   = before[:,:,2]

        blue_after  = after[:,:,0]
        green_after = after[:,:,1]
        red_after   = after[:,:,2]

        blue_final  = blue_after.astype(np.int32) - blue_before.astype(np.int32) + 255
        green_final = green_after.astype(np.int32)- green_before.astype(np.int32) + 255
        red_final   = red_after.astype(np.int32) - red_before.astype(np.int32) + 255

        output=np.zeros((after.shape[0],after.shape[1],3))
        output[:,:,0]=blue_final
        output[:,:,1]=green_final
        output[:,:,2]=red_final

        return (output/2.0).astype(np.uint8)


    def __init__(self,template_path):

        print template_path
        # load template images
        self.temp0 = cv2.imread(template_path+'red2green.png')
        self.temp1 = cv2.imread(template_path+'red2black.png')
        self.temp2 = cv2.imread(template_path+'black2green.png')
        self.temp3 = cv2.imread(template_path+'green2red.png')
        # self.temp0 = cv2.imread('templates/red2green.png')
        # self.temp1 = cv2.imread('templates/red2black.png')
        # self.temp2 = cv2.imread('templates/black2green.png')
        # self.temp3 = cv2.imread('templates/green2red.png')


        self.temp0_h = self.temp0.shape[0]
        self.temp0_w = self.temp0.shape[1]
        self.temp3_h = self.temp3.shape[0]
        self.temp3_w = self.temp3.shape[1]

        self.frame4=0
        self.frame3=0
        self.frame2=0
        self.frame1=0

        self.ok_desu=0
        self.output=np.zeros((600,600,3))

        self.green_cnt=0
        self.red_cnt=0

        # threshold of template matching
        self.green_th = 0.65 #stable:0.65
        self.red_th = 0.7 #stable:0.7

        # number of detections
        self.nd = 3

        # signal states (0:unkown, 1:green, 2:red)
        self.state = 0


    def __call__(self, frame):

        new_frame = frame
        display_frame = copy.deepcopy(new_frame)

        if self.ok_desu>4:

            output=self.diffimg(new_frame,self.frame4)
            result0=cv2.matchTemplate(output,self.temp0,method=cv2.TM_CCOEFF_NORMED)
            result1=cv2.matchTemplate(output,self.temp1,method=cv2.TM_CCOEFF_NORMED)
            result2=cv2.matchTemplate(output,self.temp2,method=cv2.TM_CCOEFF_NORMED)
            result3=cv2.matchTemplate(output,self.temp3,method=cv2.TM_CCOEFF_NORMED)

            mmlr0=cv2.minMaxLoc(result0)
            mmlr1=cv2.minMaxLoc(result1)
            mmlr2=cv2.minMaxLoc(result2)
            mmlr3=cv2.minMaxLoc(result3)

            # condition1: RED to GREEN
            if mmlr0[1]>self.green_th and mmlr0[1] > mmlr2[1]:
                self.green_cnt+=1
            else:
                self.green_cnt=0

            if self.green_cnt==self.nd:
                self.state = 1
                print "The signal turned from RED to GREEN !"
                cv2.rectangle(display_frame,
                              (mmlr0[3][0],mmlr0[3][1]),
                              (mmlr0[3][0]+temp0_w,mmlr0[3][1]+temp0_h),
                              (0,255,0),3)
                self.green_cnt=0

            # condition2: GREEN to RED
            if mmlr3[1]>self.red_th and mmlr3[1] > mmlr1[1]:
                self.red_cnt+=1
            else:
                self.red_cnt=0

            if self.red_cnt==self.nd:
                self.state = 2
                print "The signal turned from GREEN to RED !"
                cv2.rectangle(display_frame,
                              (mmlr3[3][0],mmlr3[3][1]),
                              (mmlr3[3][0]+temp3_w,mmlr3[3][1]+temp3_h),
                              (0,0,255),3)
                self.red_cnt = 0

            # display the signal state
            if self.state == 0:
                signal_state = "UNKOWN"
                color = (0,0,0)
            elif self.state == 1:
                signal_state = "GREEN"
                color = (0,255,0)
            else:
                signal_state = "RED"
                color = (0,0,255)

            message = "signal state "+str(self.state)+": "+signal_state
            #print message
            cv2.putText(display_frame, signal_state, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # display the resulting frame
            cv2.imshow('frame',display_frame)
            cv2.imshow('diff4',output)
            cv2.waitKey(3)

        self.frame4=self.frame3
        self.frame3=self.frame2
        self.frame2=self.frame1
        self.frame1=new_frame
        self.ok_desu+=1

        return self.state
