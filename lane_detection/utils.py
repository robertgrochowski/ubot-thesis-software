import numpy as np
import cv2 as cv


def region_of_interest(img, vertices):
    # Define a blank matrix that matches the image height/width.
    mask = np.zeros_like(img)
    # Retrieve the number of color channels of the image.
    channel_count = 1  # img.shape[2]
    # Create a match color with the same color channel counts.
    match_mask_color = (255,) * channel_count

    # Fill inside the polygon
    cv.fillPoly(mask, vertices, match_mask_color)

    # Returning the image only where mask pixels match
    masked_image = cv.bitwise_and(img, mask)
    return masked_image


def draw_lines_on_frame(img, lines, color=[0, 255, 0], thickness=3):
    # If there are no lines to draw, exit.
    if lines is None:
        return None

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

    colors = ([255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [64, 255, 255], [255, 128, 64])
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


def get_line_from_poly(poly, x1, x2):
    return [int(poly(x1)), x1, int(poly(x2)), x2]
