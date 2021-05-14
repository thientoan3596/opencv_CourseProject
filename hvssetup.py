from cv2 import cv2
from tracker import *
import numpy as np


# Take a screen shot and use HVS Trackbars to get the limits.
# Screenshot - screen shot file name.
screenshot = "orange.png"


def nothing(x):
    pass


# Trackbar
l_h_val = 10
l_s_val = 100
l_v_val = 100
u_h_val = 13
u_s_val = 255
u_v_val = 255
cv2.namedWindow("Trackbars")
cv2.createTrackbar("L-H", "Trackbars", l_h_val, 180, nothing)
cv2.createTrackbar("L-S", "Trackbars", l_s_val, 255, nothing)
cv2.createTrackbar("L-V", "Trackbars", l_v_val, 255, nothing)
cv2.createTrackbar("U-H", "Trackbars", u_h_val, 180, nothing)
cv2.createTrackbar("U-S", "Trackbars", u_s_val, 255, nothing)
cv2.createTrackbar("U-V", "Trackbars", u_v_val, 255, nothing)


scale_percent = 60
while (1):
    img = cv2.imread(screenshot)
    w = int(img.shape[1] * scale_percent / 100)
    h = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Frame masking for testing
    l_h = cv2.getTrackbarPos("L-H", "Trackbars")
    l_s = cv2.getTrackbarPos("L-S", "Trackbars")
    l_v = cv2.getTrackbarPos("L-V", "Trackbars")
    u_h = cv2.getTrackbarPos("U-H", "Trackbars")
    u_s = cv2.getTrackbarPos("U-S", "Trackbars")
    u_v = cv2.getTrackbarPos("U-V", "Trackbars")
    lower_color = np.array([l_h, l_s, l_v])
    upper_color = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_color, upper_color)
    res = cv2.bitwise_and(img, img, mask=mask)
    cv2.imshow('image', img)
    cv2.imshow("Mask", mask)
    cv2.imshow("Res", res)
    key = cv2.waitKey(1)

    if key == 27:
        break


cv2.destroyAllWindows()
