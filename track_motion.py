import cv2
from cv2.cv import *
import cv2.cv as cv
import math

first_point = 0
cur_track_id = 0
point_with_no_track = ()
list_of_tracks = []


class Visualization():
    def __init__(self):
        self.line_color = (250, 200, 0)

    def add_line(self, color_image, frame_height, frame_width, font, line_p1_x=0, line_p2_x=200, line_p1_y=200, line_p2_y=200, line_color=(100, 200, 0), line_width=10):
        cv.Line(color_image, (line_p1_x, line_p1_y), (line_p2_x, line_p2_y), line_color, line_width)

    def add_text_up_down_to_line(self, color_image, frame_height, frame_width, font):
        cv.PutText(color_image, "up", (0, frame_height / 2 - 5), font, self.line_color)
        cv.PutText(color_image, "down", (0, frame_height / 2 + 25), font, self.line_color)


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
        self.max_distance_between = 60
        self.min_distance_between = 0
        self.min_record_step = 5
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
            for track in list_of_tracks:
                if track:
                    last_track_coord = len(track.coordinates) - 1
                    distance_between = math.hypot(track.coordinates[last_track_coord][0] - point[0],
                                                  track.coordinates[last_track_coord][1] - point[1])
                    if (distance_between <= self.max_distance_between) and (
                                    distance_between >= (self.min_distance_between + self.min_record_step) and
                                    track.coordinates[last_track_coord] != point):
                        track.add_point(point)
                        we_found_nearest_track = True
                    if (distance_between <= self.max_distance_between) and (
                                distance_between >= self.min_distance_between):
                        we_found_nearest_track = True
            if not we_found_nearest_track:
                print "This point have no track", point, "Current track number", cur_track_id + 1
                point_with_no_track = point
        return first_point, point_with_no_track

    def add_points_to_tracks(self, point):
        global first_point, cur_track_id, point_with_no_track
        first_point, point_with_no_track = self.find_nearest_track(point)
        if point_with_no_track:
            if first_point == 1:
                print "We will add first_point", point, "To track = ", cur_track_id
                self.track.set_track_id(cur_track_id)
                self.track.add_point(point_with_no_track)
                list_of_tracks.append(self.track)
                cur_track_id += 1
                first_point = 2
                print "First point was added. Current number of tracks =", len(list_of_tracks)
            else:
                self.track.set_track_id(cur_track_id)
                self.track.add_point(point_with_no_track)
                list_of_tracks.append(self.track)
                cur_track_id += 1


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
            line_and_text = Visualization()
            #line_and_text.add_line(color_image, self.frame_height, self.frame_width, font, line_color=(0,0,0))
            #line_and_text.add_text_up_down_to_line(color_image, self.frame_height, self.frame_width, font)

            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()
                pt1, pt2, point, area = self.get_rectangle_parameters(bound_rect, color_image)
                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255, 0, 0), 1)
                self.list_of_points = []
                self.get_points_tracking(point, area, color_image)
                tracking = Tracking()
                for point in self.list_of_points:
                    tracking.add_points_to_tracks(point)
                for track in list_of_tracks:
                    x_first = track.coordinates[len(track.coordinates) - 2][0]
                    y_first = track.coordinates[len(track.coordinates) - 2][1]
                    x = track.coordinates[len(track.coordinates) - 1][0]
                    y = track.coordinates[len(track.coordinates) - 1][1]
                    line_and_text.add_line(color_image, self.frame_height, self.frame_width, font,line_p1_x=x_first, line_p1_y=y_first, line_p2_x=x, line_p2_y=y, line_width=4,line_color=(0, 222, 322))
            cv.ShowImage("target", color_image)
            c = cv.WaitKey(1) % 0x100
            if c == 27:
                break


if __name__ == "__main__":
    t = Target()
    t.run()