import cv2
from cv2.cv import *
import cv2.cv as cv
import math

first_point = 0
cur_track_id = 0
point_with_no_track = ()


class Track:
    def __init__(self):
        self.track_id = ""
        self.coordinates = []
        self.velocity = 0

    def add_point(self, point):
        self.coordinates.append(point)

    def set_track_id(self, track_id):
        self.track_id = "track %d" % track_id

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y


class Tracking:
    def __init__(self):
        self.max_distance_between = 50
        self.min_distance_between = 0
        self.list_of_points = []
        self.track = Track()

    def find_nearest_track(self, point):
        global first_point, point_with_no_track
        point_with_no_track = ()
        we_found_nearest_track = False
        if first_point == 0:
            print "First point was detected"
            point_with_no_track = point
            first_point = 1
        if first_point == 2:
            for track in self.track.coordinates:
                print "we have  a track", track
                if track:
                    distance_between = math.hypot(track.x - point[0], track.y - point[1])
                    print "We compare point", point, "with last in track = ", "Distance between = ", distance_between
                    if (distance_between <= self.max_distance_between) and (distance_between >= (self.min_distance_between +5)):
                        print "Add point to track", track.x, track.y
                        self.track.add_point(Track.Point(point[0], point[1]))
                        print "We added point to track=", track
                        we_found_nearest_track = True
                    elif (distance_between <= self.max_distance_between) and (distance_between >= self.min_distance_between):
                        print "We found point in track but is the same as was. Point:", point
                        we_found_nearest_track = True
            if not we_found_nearest_track:
                print "This point have no track", point
                point_with_no_track = point
        return first_point, point_with_no_track

    def add_points_to_tracks(self, point):
        global first_point, cur_track_id, point_with_no_track
        first_point, point_with_no_track = self.find_nearest_track(point)
        print "point_with_no_track after using self.find_nearest_track(point)= ", point_with_no_track
        if point_with_no_track:
            if first_point == 1:
                print "We will add first_point", point, "To track = ", cur_track_id
                self.track.set_track_id(cur_track_id)
                self.track.add_point(point_with_no_track)
                print "self.track.coordinates", self.track.coordinates, "self.track.track_id", self.track.track_id
                for i in self.track.coordinates:
                    print "x coord", i.x, "y coord", i.y
                cur_track_id += 1
                first_point = 2
                print "First point was added. Current number of tracks ="
                point_with_no_track = ()
            else:
                print "We will add new track for point", point_with_no_track, "Track ID = ", cur_track_id
                self.track.set_track_id(cur_track_id)
                self.track.add_point(point_with_no_track)
                print "+1 track",
                cur_track_id += 1
                point_with_no_track = ()
                #print "We deleted this point. Now point_with_no_track = ", point_with_no_track


class Target:
    def __init__(self):
        self.capture = cv.CaptureFromFile("People.mp4")
        frame = cv.QueryFrame(self.capture)
        self.frame_size = cv.GetSize(frame)
        self.grey_image = cv.CreateImage(self.frame_size, cv.IPL_DEPTH_8U, 1)
        self.moving_average = cv.CreateImage(self.frame_size, cv.IPL_DEPTH_32F, 3)
        self.min_area = 1800
        self.frame_width = self.frame_size[0]
        self.frame_height = self.frame_size[1]
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
                self.get_points_tracking(point, area, color_image)
                tracking = Tracking()
                for point in self.list_of_points:
                    tracking.add_points_to_tracks(point)
            cv.ShowImage("target", color_image)
            c = cv.WaitKey(1) % 0x100
            if c == 27:
                break


if __name__ == "__main__":
    t = Target()
    t.run()