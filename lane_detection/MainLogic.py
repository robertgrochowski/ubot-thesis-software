import time
import numpy as np
import cv2 as cv

from picamera.array import PiRGBArray
from picamera import PiCamera
from .DetectedLine import DetectedLine

class MainLogic:
    # ---- Constants ---
    height = 480
    width = 640

    region_of_interest_vertices = [
        (0, height),
        (30, height//2),
        (width-30, height//2),
        (width, height),
    ]

    def __init__(self, movement, engines):
        self.movement = movement
        self.engines = engines

        self.camera = PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size=(self.width, self.height))


    def start(self):
        # allow the camera to warmup
        time.sleep(0.3)

        #movement.moveForward()

        fourcc = cv.VideoWriter_fourcc(*'MP4V')
        out = cv.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

        # capture frames from the camera
        for img in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            frame = img.array

            # Process image (Blur, Range, Canny, Crop)
            processed_image = self.transform_input_image(frame)

            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)

            # monitor for quit
            k = cv.waitKey(1) & 0xFF
            if k == ord('q'):
                return

            # Get Edge Lines
            edge_lines = cv.HoughLinesP(
                processed_image,
                rho=2,
                theta=np.pi / 180,
                threshold=60,
                lines=np.array([]),
                minLineLength=40,
                maxLineGap=5
            )
            frame_lines = frame.copy()

            # Draw middle line
            cv.line(frame_lines, (int(self.width//2), int(self.height)), (int(self.width//2), int(self.height//2)), [255, 0, 0], 2)

            if edge_lines is None:
                continue

            # Group lines to left and right
            # Calculate score fore each line
            # If score >= 0.8: draw this line

            computed_lines = []

            for rawLine in edge_lines:
                for x1, y1, x2, y2 in rawLine:
                    line = DetectedLine((x1, y1), (x2, y2))
                    computed_lines.append(line)

                    # Draw lines
                    color = [255, 0, 255] if line.side == DetectedLine.SIDE_LEFT < 0.8 else [0, 255, 0]
                    if line.score < 0.8:
                        continue

                    cv.line(frame_lines, line.point1, line.point2, color, 2)

            accurate_lines = list(filter(lambda x: x.score >= 0.8, computed_lines))
            accurate_lines_left = list(filter(lambda x: x.side == DetectedLine.SIDE_LEFT, accurate_lines))
            accurate_lines_right = list(filter(lambda x: x.side == DetectedLine.SIDE_RIGHT, accurate_lines))
            # inaccurate_lines = filter(lambda x: x.score < 0.8, computed_lines)

            print(len(accurate_lines_right))

            if not accurate_lines_left or not accurate_lines_right:
                self.movement.stop()
                # self.movement.moveRight()
                print("Left line not found: "+ str(not accurate_lines_left))
                print("Right line not found: "+ str(not accurate_lines_right))
                cv.putText(frame_lines, "No accurate line found", (self.width // 2, self.height // 2), cv.FONT_HERSHEY_SIMPLEX, 1,
                           (0, 0, 255), 2, cv.LINE_AA)
                continue

            left_x = np.array([[_line.point1[0], _line.point2[0]] for _line in accurate_lines_left]).flatten()
            left_y = np.array([[_line.point1[1], _line.point2[1]] for _line in accurate_lines_left]).flatten()

            right_x = np.array([[_line.point1[0], _line.point2[0]] for _line in accurate_lines_right]).flatten()
            right_y = np.array([[_line.point1[1], _line.point2[1]] for _line in accurate_lines_right]).flatten()

            accurate_lines_left_poly = np.poly1d(np.polyfit(
                left_y,
                left_x,
                deg=1
            ))

            accurate_lines_right_poly = np.poly1d(np.polyfit(
                right_y,
                right_x,
                deg=1
            ))

            edge_lines = []
            min_y = frame.shape[0] * (3 / 5)  # Just below the horizon
            max_y = frame.shape[0]  # The bottom of the image

            approx_left_line = self.get_line_from_poly(accurate_lines_left_poly, max_y, min_y)
            approx_right_line = self.get_line_from_poly(accurate_lines_right_poly, max_y, min_y)
            middle_lines_avg = [(approx_left_line[0]+approx_right_line[0])//2, max_y, (approx_left_line[2]+approx_right_line[2])//2, min_y]

            edge_lines.append(middle_lines_avg)
            edge_lines.append(approx_right_line)
            edge_lines.append(approx_left_line)

            dest_x = (middle_lines_avg[0] + middle_lines_avg[2]) // 2
            diff = self.width // 2 - dest_x
            # slop = (max_y - min_y) / (right_x_end - right_x_start)
            # cv.putText(frame_lines, str(int(slop)), (self.width // 2 - 30, self.height - 20), cv.FONT_HERSHEY_SIMPLEX, 1,
            #            (255, 255, 255), 2, cv.LINE_AA)

            line_image = self.draw_lines_on_frame(
                frame_lines,
                [edge_lines],
                thickness=5,
            )

            # Center line
            cv.line(line_image, (int(self.width // 2), int(self.height)), (int(self.width // 2), int(self.height // 2)), [255, 0, 0], 2)

            ### MOVING ###

            self.movement.moveForward()
            left_additional_speed = 0
            right_additional_speed = 0
            if diff < -30:
                left_additional_speed = abs(diff)*0.08
            elif diff > 30:
                right_additional_speed = abs(diff)*0.08

            self.engines.setRightSpeed(10+int(right_additional_speed))
            self.engines.setLeftSpeed(10+int(left_additional_speed))

            if (10+int(right_additional_speed)) > 100 or (10+int(left_additional_speed)):
                print("invalid set speed!")
                cv.imshow("uBot poly", line_image)
                cv.waitKey(0)

            cv.putText(line_image, str(10+int(left_additional_speed)), (40, self.height - 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv.LINE_AA)
            cv.putText(line_image, str(10+int(right_additional_speed)), (self.width - 40, self.height - 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv.LINE_AA)

            cv.imshow("uBot poly", line_image)
            out.write(line_image)

        out.release()
        cv.destroyAllWindows()

    def get_line_from_poly(self, poly, x1, x2):
        return [int(poly(x1)), x1, int(poly(x2)), x2]

    def transform_input_image(self, frame):
        # Blur
        kernel_size = 5
        blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        # Range
        frame_HSV = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        in_rng = cv.inRange(frame_HSV, (0, 0, 0), (180, 255, 50))
        # Canny
        canny_image = cv.Canny(in_rng, 200, 0)
        # Crop Canny
        cropped_cannyed = self.region_of_interest(
            canny_image,
            np.array([self.region_of_interest_vertices], np.int32),
        )

        cv.imshow("test", cropped_cannyed)
        return cropped_cannyed

    def region_of_interest(self, img, vertices):
        # Define a blank matrix that matches the image height/width.
        mask = np.zeros_like(img)
        # Retrieve the number of color channels of the image.
        channel_count = 1 # img.shape[2]
        # Create a match color with the same color channel counts.
        match_mask_color = (255,) * channel_count

        # Fill inside the polygon
        cv.fillPoly(mask, vertices, match_mask_color)

        # Returning the image only where mask pixels match
        masked_image = cv.bitwise_and(img, mask)
        return masked_image

    def draw_lines_on_frame(self, img, lines, color=[0, 255, 0], thickness=3):
        # If there are no lines to draw, exit.
        if lines is None:
            return

        # Make a copy of the original image.
        img = np.copy(img)
        # Create a blank image that matches the original in size.
        line_img = np.zeros(
            (
                img.shape[0],
                img.shape[1],
                3
            ),
            dtype=np.uint8,
        )

        colors = ([255, 0, 0], [0, 255, 0], [0, 0, 255], [128, 128, 128], [64, 64, 64], [255, 128, 64])
        colorid = 0

        # Loop over all lines and draw them on the blank image.
        for line in lines:
            for x1, y1, x2, y2 in line:
                colorid += 1
                if colorid >= len(colors):
                    colorid = 0
                cv.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), colors[colorid], thickness)
        # Merge the image with the lines onto the original.
        img = cv.addWeighted(img, 0.8, line_img, 1.0, 0.0)
        # Return the modified image.
        return img