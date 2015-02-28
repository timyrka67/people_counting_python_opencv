__author__ = 'timur'
import cv2
import cv2.cv as cv
import math
from cv2.cv import *
class Target:

    def __init__(self):
        self.capture = cv.CaptureFromFile("People.mp4")
        #self.capture
        #self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow("Target", 1)

    def run(self):
        # Capture first frame to get size
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        color_image = cv.CreateImage(cv.GetSize(frame), 8, 3)
        grey_image = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_32F, 3)
        list_of_tracks = [["track %d"%(0),[(147,223)]]]
        print list_of_tracks.__len__()
        #track = []
        tracks_id = 0
        distance_max = 25
        distance_min = 2
        schet = 0
        #track = ("track %d"%(tracks_id),[(147,223)])

        #list_of_tracks.append(track)
        list_of_points= []


        first = True

        while True:
            closest_to_left = cv.GetSize(frame)[0]
            closest_to_right = cv.GetSize(frame)[1]

            color_image = cv.QueryFrame(self.capture)

            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

            if first:
                difference = cv.CloneImage(color_image)
                temp = cv.CloneImage(color_image)
                cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
                first = False
            else:
                cv.RunningAvg(color_image, moving_average, 0.020, None)

            # Convert the scale of the moving average.
            cv.ConvertScale(moving_average, temp, 1.0, 0.0)

            # Minus the current frame from the moving average.
            cv.AbsDiff(color_image, temp, difference)

            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)

            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)

            # Dilate and erode to get people blobs
            cv.Dilate(grey_image, grey_image, None, 18)
            cv.Erode(grey_image, grey_image, None, 10)

            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            points = []


            #line characteristic
            frame_width  = frame_size[0]
            frame_height = frame_size[1]
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 1, 1)
            #print 'The x size of frame =', frame_width, 'and y = ', frame_height
            cv.Line(color_image,(0,frame_height/2),(frame_width,frame_height/2),(250,0,0),1)
            cv.PutText(color_image,"up",(0,frame_height/2 -5),font,(250,0,0))
            cv.PutText(color_image,"down",(0,frame_height/2 +25),font,(250,0,0))

            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()

                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                points.append(pt1)
                points.append(pt2)

                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255,0,0), 1)
                x_center = abs(pt1[0]-pt2[0])/2+pt1[0]
                y_center = abs(pt1[1]-pt2[1])/2+pt1[1]

                point = (x_center ,y_center)
                #print pt1,pt2
                schet =schet +1
                print schet,"Frame"
                y_length = abs(pt1[0]-pt2[0])
                x_length = abs(pt1[1]-pt2[1])
                area = x_length*y_length
                if area > 1800:            #coefficient of object size
                    cv.Circle(color_image, point, 2, cv.CV_RGB(255, 255, 0), 6)
                    list_of_points.append(point)
                    objects_number = list_of_points.__len__()
                    cv.PutText(color_image,'Objects %x '%objects_number,(0,frame_height),font,(250,0,0))

                    for point_temp in list_of_points:
                        print "We in for point_temp in list_of_points: current point ",point_temp
                        for track_temp in list_of_tracks:
                            print "We in for track_temp in list_of_tracks: track_temp:",track_temp
                            last_index_of_track_temp = len(track_temp) - 1
                            last_element_coord_list = track_temp[last_index_of_track_temp]
                            last_element_coord = last_element_coord_list[0]
                            last_coord_x = last_element_coord[0]
                            last_coord_y = last_element_coord[1]
                            distance_between = math.hypot(last_coord_x-point_temp[0],last_coord_y-point_temp[1])
                            print "distance_between",distance_between
                            if (distance_between < distance_max) and (distance_between > distance_min) and (last_element_coord_list != point_temp):
                                print "distance less then ",distance_max
                                last_element_coord_list.append(point_temp)
                                print track_temp

                            """else:
                                print"Wrong distance"
                                tracks_id = tracks_id + 1
                                track = ("track %d"%(tracks_id),[point_temp])
                                list_of_tracks.append(track)"""
                        """        track_temp_points = track_temp[1]
                                last_index_of_points = len(track_temp_points) - 1
                            #    print last_index_of_points
                                track_last_point = track_temp_points[last_index_of_points]
                                distance_between = math.hypot(track_last_point[0]-point_temp[0],track_last_point[1]-point_temp[1])
                                if distance_between < distance_max:
                             #       print "distance less then ",distance_max
                                    track_temp_points.append(point_temp)
                              #      print track_temp_points
                                else:
                               #     print "distance more then ",distance_max
                                    tracks_id = tracks_id + 1
                                    track = ("track %d"%(tracks_id),[point])
                                    list_of_tracks.append(track)
                                #    print "add_new_track"
                                 #   print track"""

            if len(points):
                center_point = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
                """cv.Circle(color_image, center_point, 40, cv.CV_RGB(255, 255, 255), 1)
                cv.Circle(color_image, center_point, 30, cv.CV_RGB(255, 100, 0), 1)
                cv.Circle(color_image, center_point, 20, cv.CV_RGB(255, 255, 255), 1)
                cv.Circle(color_image, center_point, 10, cv.CV_RGB(255, 1y00, 0), 1)"""
                #print center_point
            cv.ShowImage("Target", color_image)

            # Listen for ESC key
            c = cv.WaitKey(1) % 0x100
            if c == 27:
                break

if __name__=="__main__":
    t = Target()
    t.run()