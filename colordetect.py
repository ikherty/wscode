# coding: utf8
import rospy
import math
from clover import srv
import cv2 as cv
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

rospy.init_node('color')
bridge = CvBridge()

image_pub = rospy.Publisher('~image', Image, queue_size=1)

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)


def dist2D(x,y,x1,y1):
    return math.sqrt((x-x1) ** 2 + (y-y1) ** 2)

def check_temp(data):
    frame = bridge.imgmsg_to_cv2(data, 'bgr8')
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    cnt_x = int(data.width/2)
    cnt_y = int(data.height / 2)
    cnt_color = hsv[cnt_y][cnt_x]
    #cv.circle(frame, (cnt_x, cnt_y), 5, (0, 0, 255), 2)
    #print(cnt_color)
    #cv.putText(frame, '%d %d %d' % (cnt_color[0], cnt_color[1], cnt_color[2]),(0, data.height), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))
    # red_low = [3,235,255]
    # red_high = [3,235,255]
    yellow_low = (0,235-30,255-30)
    yellow_high = (30+30,235+20,255)
    # green_low = [71,221,247]
    # green_high = [71,221,247]
    #masks
    yellow = cv.inRange(hsv, yellow_low, yellow_high)
    #img_thresh = cv.bitwise_or(hsv, yellow)
    image_pub.publish(bridge.cv2_to_imgmsg(yellow, 'mono8'))
    m=cv.moments(yellow)
    dM01 = m['m01']
    dM10 = m['m10']
    dArea = m['m00']
    if dArea>0:
        x = int(dM10 / dArea)
        y = int(dM01 / dArea)
        dx=cnt_x-x
        dy=cnt_y-y
        print(dx,dy)
        #print(dif)
        dif=dist2D(cnt_x,cnt_y,x,y)
        print(dif)
        if dif>0.2:
            print('qq')
            ks=0.005
            speed=ks*dif
            navigate(frame_id='body',x=dy,y=dx, speed=speed)
            
image_sub = rospy.Subscriber('main_camera/image_raw', Image, check_temp, queue_size=1)  # get capture
rospy.spin()
