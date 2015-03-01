import cv2
from cv2.cv import *
import cv2.cv as cv
import math


class Target:
    def __init__(self):
        self.capture = cv.CaptureFromFile("People.mp4")
        frame = cv.QueryFrame(self.capture)
        self.frame_size = cv.GetSize(frame)
        self.grey_image = cv.CreateImage(self.frame_size, cv.IPL_DEPTH_8U, 1)
        self.moving_average = cv.CreateImage(self.frame_size, cv.IPL_DEPTH_32F, 3)
        self.distance_max = 25
        self.distance_min = 2
        self.tracks_id = 0
        self.min_area = 1800
        self.frame_width = self.frame_size[0]
        self.frame_height = self.frame_size[1]
        self.list_of_tracks = [["track %d" % self.tracks_id, [(147, 223)]]]
        self.list_of_points = []

    def image_difference(self, first):
        global temp, moving_difference
        color_image = cv.QueryFrame(self.capture)
        if first:
            moving_difference = cv.CloneImage(color_image)
            temp = cv.CloneImage(color_image)
            first = False
        cv.AbsDiff(color_image, temp, moving_difference)
        cv.CvtColor(moving_difference, self.grey_image, cv.CV_RGB2GRAY)
        cv.Threshold(self.grey_image, self.grey_image, 70, 255, cv.CV_THRESH_BINARY)
        cv.Dilate(self.grey_image, self.grey_image, None, 18)
        return color_image, first

    def add_contour_in_storage(self):
        storage = cv.CreateMemStorage(0)
        contour = cv.FindContours(self.grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
        return contour

    @staticmethod
    def get_rectangle_parameters(bound_rect, color_image):
        pt1 = (bound_rect[0], bound_rect[1])
        pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
        x_center = abs(pt1[0] - pt2[0]) / 2 + pt1[0]
        y_center = abs(pt1[1] - pt2[1]) / 2 + pt1[1]
        point = (x_center, y_center)
        y_length = abs(pt1[0] - pt2[0])
        x_length = abs(pt1[1] - pt2[1])
        area = x_length * y_length
        return pt1, pt2, point, area

    def get_points_tracking(self, point, area, color_image):
        if area > self.min_area:
            cv.Circle(color_image, point, 2, cv.CV_RGB(255, 255, 0), 6)
            self.list_of_points.append(point)
            for point_temp in self.list_of_points:
                for track_temp in self.list_of_tracks:
                    last_index_of_track_temp = len(track_temp) - 1
                    last_element_coord_list = track_temp[last_index_of_track_temp]
                    last_element_coord = last_element_coord_list[0]
                    last_coord_x = last_element_coord[0]
                    last_coord_y = last_element_coord[1]
                    distance_between = math.hypot(last_coord_x - point_temp[0], last_coord_y - point_temp[1])
                    if (distance_between < self.distance_max) and (distance_between > self.distance_min) and (last_element_coord_list != point_temp):
                        last_element_coord_list.append(point_temp)
        return self.list_of_tracks

    def run(self):
        first = True
        while True:
            color_image, first = self.image_difference(first)
            contour = self.add_contour_in_storage()
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 1, 1)
            cv.Line(color_image, (0, self.frame_height / 2), (self.frame_width, self.frame_height / 2), (250, 0, 0), 1)
            cv.PutText(color_image, "up", (0, self.frame_height / 2 - 5), font, (250, 0, 0))
            cv.PutText(color_image, "down", (0, self.frame_height / 2 + 25), font, (250, 0, 0))
            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()
                pt1, pt2, point, area = self.get_rectangle_parameters(bound_rect, color_image)
                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255, 0, 0), 1)
                self.list_of_tracks = self.get_points_tracking(point, area, color_image)
            cv.ShowImage("target", color_image)
            c = cv.WaitKey(1) % 0x100
            if c == 27:
                break


if __name__ == "__main__":
    t = Target()
    t.run()