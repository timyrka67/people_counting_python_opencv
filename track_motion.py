__author__ = 'timur'
import cv2
import cv2.cv as cv
import math
from cv2.cv import *

class target:
    def __init__(self):
        self.capture = cv.CaptureFromFile("People.mp4")
        cv.NamedWindow("target", 1)
    def run(self):
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)

        list_of_points= []
        list_of_tracks = [["track %d"%(0),[(147,223)]]]
        tracks_id = 0
        distance_max = 25
        distance_min = 2

        first = True

        while True:
            color_image = cv.QueryFrame(self.capture)

            if first:
                moving_difference = cv.CloneImage(color_image)
                temp = cv.CloneImage(color_image)
                cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
                first = False
            else:
                cv.RunningAvg(color_image, moving_average, 0.020, None)

            cv.AbsDiff(color_image, temp, moving_difference )
            cv.CvtColor(moving_difference, grey_image, cv.CV_RGB2GRAY)
            cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)
            cv.Dilate(grey_image, grey_image, None, 18)
            cv.Erode(grey_image, grey_image, None, 10)

            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            frame_width  = frame_size[0]
            frame_height = frame_size[1]
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 1, 1)
            cv.Line(color_image,(0,frame_height/2),(frame_width,frame_height/2),(250,0,0),1)
            cv.PutText(color_image,"up",(0,frame_height/2 -5),font,(250,0,0))
            cv.PutText(color_image,"down",(0,frame_height/2 +25),font,(250,0,0))

            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()
                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255,0,0), 1)

                x_center = abs(pt1[0]-pt2[0])/2+pt1[0]
                y_center = abs(pt1[1]-pt2[1])/2+pt1[1]
                point = (x_center ,y_center)

                y_length = abs(pt1[0]-pt2[0])
                x_length = abs(pt1[1]-pt2[1])
                area = x_length*y_length

                if area > 1800:
                    cv.Circle(color_image, point, 2, cv.CV_RGB(255, 255, 0), 6)
                    list_of_points.append(point)
                    for point_temp in list_of_points:
                        for track_temp in list_of_tracks:
                            last_index_of_track_temp = len(track_temp) - 1
                            last_element_coord_list = track_temp[last_index_of_track_temp]
                            last_element_coord = last_element_coord_list[0]
                            last_coord_x = last_element_coord[0]
                            last_coord_y = last_element_coord[1]
                            distance_between = math.hypot(last_coord_x-point_temp[0],last_coord_y-point_temp[1])
                            if (distance_between < distance_max) and (distance_between > distance_min) and (last_element_coord_list != point_temp):
                                last_element_coord_list.append(point_temp)
            cv.ShowImage("target", color_image)
            c = cv.WaitKey(1) % 0x100
            if c == 27:
                break
if __name__=="__main__":
    t = target()
    t.run()