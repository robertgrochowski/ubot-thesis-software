import numpy as np
import cv2 as cv

from main.config import SIDE_RIGHT, SIDE_LEFT


def region_of_interest(img, vertices):
    # Define a blank matrix
    mask = np.zeros_like(img)
    # Create only one color mask
    match_mask_color = (255,)
    # Fill inside the polygon
    cv.fillPoly(mask, vertices, match_mask_color)
    # Returning the image only where mask pixels match
    masked_image = cv.bitwise_and(img, mask)
    return masked_image


def draw_lines_on_frame(img, lines, thickness=3):
    # If there are no lines to draw, exit
    if lines is None:
        return None

    # pick different color for each line
    colors = ([255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [64, 255, 255], [255, 128, 64])
    color_id = 0

    # Loop over all lines and draw them on the blank image.
    for line in lines:
        for x1, y1, x2, y2 in line:
            color_id += 1
            if color_id >= len(colors):
                color_id = 0

            cv.line(img, (int(x1), int(y1)), (int(x2), int(y2)), colors[color_id], thickness)
    return img


def get_opposite_side(side):
    return SIDE_LEFT if side == SIDE_RIGHT else SIDE_RIGHT
