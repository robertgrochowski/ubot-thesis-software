import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2 as cv
import math
from statistics import mean


def region_of_interest(img, vertices):
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

def draw_lines(img, lines, color=[0, 255, 0], thickness=3):
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

def main():
    # vid = cv.VideoCapture("pivideo.mp4")
    # if vid is None:
    #     print('Unable to open target video')
    #     return
    #
    # ret, frame = vid.read()

    height = 640
    width = 480

    region_of_interest_vertices = [
        (0, height),
        ((width / 2) - 200, height//2),
        ((width / 2) + 200, height//2),
        (width, height),
    ]

    middle_lines = []
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 25
    rawCapture = PiRGBArray(camera, size=(640,480))

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        frame = frame.array

        # Greyscale
        gray_image = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)

        # Blur
        blur = cv.blur(gray_image,(3,3))

        # Canny
        canny_image = cv.Canny(blur, 150, 200)

        # Crop Canny
        cropped_cannyed = region_of_interest(
            canny_image,
            np.array([region_of_interest_vertices], np.int32),
        )

        # Lines
        lines = cv.HoughLinesP(
            cropped_cannyed,
            rho=5,
            theta=np.pi / 60,
            threshold=150,
            lines=np.array([]),
            minLineLength=30,
            maxLineGap=25
        )

        lines_img = frame.copy()
        cv.line(lines_img, (int(width//2), int(height)), (int(width//2), int(height//2)), [255, 0, 0], 2)

        left_line_x = []
        left_line_y = []
        right_line_x = []
        right_line_y = []
        if lines is None:
            continue

        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (y2 - y1) / (x2 - x1)  # <-- Calculating the slope.
                if math.fabs(slope) < 0.5:  # <-- Only consider extreme slope
                    continue

                # ---
                if x1 < width//2 and x2 < width//2:
                    if slope > 0:
                        continue # left
                elif x1 > width//2 and x2 > width//2:
                    if slope < 0:
                        continue # left
                else: # cross the middle
                    continue

                if slope <= 0:  # <-- If the slope is negative, left group.
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                    cv.line(lines_img, (int(x1), int(y1)), (int(x2), int(y2)), [0,255,0], 2)
                else:  # <-- Otherweise, right group.
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])
                    cv.line(lines_img, (int(x1), int(y1)), (int(x2), int(y2)), [0, 0,255], 2)

        if not left_line_x or not right_line_x:
            continue

        min_y = frame.shape[0] * (3 / 5)  # <-- Just below the horizon
        max_y = frame.shape[0]  # <-- The bottom of the image
        poly_left = np.poly1d(np.polyfit(
            left_line_y,
            left_line_x,
            deg=1
        ))

        left_x_start = int(poly_left(max_y))
        left_x_end = int(poly_left(min_y))
        poly_right = np.poly1d(np.polyfit(
            right_line_y,
            right_line_x,
            deg=1
        ))
        right_x_start = int(poly_right(max_y))
        right_x_end = int(poly_right(min_y))

        middle_lines.append([(left_x_start+right_x_start)//2, max_y, (left_x_end+right_x_end)//2, min_y])

        if len(middle_lines) > 5:
            middle_lines.pop(0)

        middle_lines_avg = [sum(col) / float(len(col)) for col in zip(*middle_lines)]

        line_image = draw_lines(
            frame,
            [[
                [left_x_start, max_y, left_x_end, min_y],
                [right_x_start, max_y, right_x_end, min_y],
                middle_lines_avg
            ]],
            thickness=5,
        )

        a = middle_lines_avg[2] - middle_lines_avg[0]

        print("offset: "+str(a))

        k = cv.waitKey(0)
        if k == ord('q'):
            return

        cv.imshow("uBot Caynned", cropped_cannyed)
        cv.imshow("uBot final lines", line_image)
        cv.imshow("uBot final lines2", lines_img)
        # cv.imshow("conturs", conturs_img)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)


if __name__ == '__main__':
    main()