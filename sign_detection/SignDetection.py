

# Detecting Objects in Real Time with OpenCV deep learning library
#
# Algorithm:
# Reading stream video from camera --> Loading YOLO v3 Network -->
# --> Reading frames in the loop --> Getting blob from the frame -->
# --> Implementing Forward Pass --> Getting Bounding Boxes -->
# --> Non-maximum Suppression --> Drawing Bounding Boxes with Labels -->
# --> Showing processed frames in OpenCV Window
#
# Result:
# Window with Detected Objects, Bounding Boxes and Labels in Real Time


# Importing needed libraries
import numpy as np
import cv2

class SignDetection:

    """
    Start of:
    Loading YOLO v3 network
    """

    def __init__(self):
        # Preparing variables for spatial dimensions of the frames
        self.height = None
        self.width = None

        # Loading COCO class labels from file
        # Opening file
        # Pay attention! If you're using Windows, yours path might looks like:
        # r'yolo-coco-data\coco.names'
        # or:
        # 'yolo-coco-data\\coco.names'
        with open('classes.names') as f:
            # Getting labels reading every line
            # and putting them into the list
            self.labels = [line.strip() for line in f]

        # Loading trained YOLO v3 Objects Detector
        # with the help of 'dnn' library from OpenCV
        # Pay attention! If you're using Windows, yours paths might look like:
        # r'yolo-coco-data\yolov3.cfg'
        # r'yolo-coco-data\yolov3.weights'
        # or:
        # 'yolo-coco-data\\yolov3.cfg'
        # 'yolo-coco-data\\yolov3.weights'
        self.network = cv2.dnn.readNetFromDarknet('yolov3_ts_test.cfg',
                                             'yolov3_ts_train_last.weights')

        # Getting list with names of all layers from YOLO v3 network
        self.layers_names_all = self.network.getLayerNames()

        # Getting only output layers' names that we need from YOLO v3 algorithm
        # with function that returns indexes of layers with unconnected outputs
        self.layers_names_output = \
            [self.layers_names_all[i[0] - 1] for i in self.network.getUnconnectedOutLayers()]

        # Setting minimum probability to eliminate weak predictions
        self.probability_minimum = 0.85

        # Setting threshold for filtering weak bounding boxes
        # with non-maximum suppression
        self.threshold = 0.3

        # Generating colours for representing every detected object
        # with function randint(low, high=None, size=None, dtype='l')
        self.colours = np.random.randint(150, 255, size=(len(self.labels), 3), dtype='uint8')

        """
        End of:
        Loading YOLO v3 network
        """


    """
    Start of:
    Reading frames in the loop
    """
    def process(self, frame):

        # Getting spatial dimensions of the frame
        # we do it only once from the very beginning
        # all other frames have the same dimension
        if self.width is None or self.height is None:
            # Slicing from tuple only first two elements
            self.height, self.width = frame.shape[:2]

        """
        Start of:
        Getting blob from current frame
        """

        # Getting blob from current frame
        # The 'cv2.dnn.blobFromImage' function returns 4-dimensional blob from current
        # frame after mean subtraction, normalizing, and RB channels swapping
        # Resulted shape has number of frames, number of channels, width and height
        # E.G.:
        # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                     swapRB=True, crop=False)

        """
        End of:
        Getting blob from current frame
        """

        """
        Start of:
        Implementing Forward pass
        """

        # Implementing forward pass with our blob and only through output layers
        # Calculating at the same time, needed time for forward pass
        self.network.setInput(blob)  # setting blob as input to the network
        # start = time.time()
        output_from_network = self.network.forward(self.layers_names_output)
        # end = time.time()

        # Showing spent time for single current frame
        # print('Current frame took {:.5f} seconds'.format(end - start))

        """
        End of:
        Implementing Forward pass
        """

        """
        Start of:
        Getting bounding boxes
        """

        # Preparing lists for detected bounding boxes,
        # obtained confidences and class's number
        bounding_boxes = []
        confidences = []
        class_numbers = []

        # Going through all output layers after feed forward pass
        for result in output_from_network:
            # Going through all detections from current output layer
            for detected_objects in result:
                # Getting 80 classes' probabilities for current detected object
                scores = detected_objects[5:]
                # Getting index of the class with the maximum value of probability
                class_current = np.argmax(scores)
                # Getting value of probability for defined class
                confidence_current = scores[class_current]

                # # Check point
                # # Every 'detected_objects' numpy array has first 4 numbers with
                # # bounding box coordinates and rest 80 with probabilities
                # # for every class
                # print(detected_objects.shape)  # (85,)

                # Eliminating weak predictions with minimum probability
                if confidence_current > self.probability_minimum:
                    # Scaling bounding box coordinates to the initial frame size
                    # YOLO data format keeps coordinates for center of bounding box
                    # and its current width and height
                    # That is why we can just multiply them elementwise
                    # to the width and height
                    # of the original frame and in this way get coordinates for center
                    # of bounding box, its width and height for original frame
                    box_current = detected_objects[0:4] * np.array([self.width, self.height, self.width, self.height])

                    # Now, from YOLO data format, we can get top left corner coordinates
                    # that are x_min and y_min
                    x_center, y_center, box_width, box_height = box_current
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))

                    # Adding results into prepared lists
                    bounding_boxes.append([x_min, y_min,
                                           int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)

        """
        End of:
        Getting bounding boxes
        """

        """
        Start of:
        Non-maximum suppression
        """

        # Implementing non-maximum suppression of given bounding boxes
        # With this technique we exclude some of bounding boxes if their
        # corresponding confidences are low or there is another
        # bounding box for this region with higher confidence

        # It is needed to make sure that data type of the boxes is 'int'
        # and data type of the confidences is 'float'
        # https://github.com/opencv/opencv/issues/12789
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences,
                                   self.probability_minimum, self.threshold)

        """
        End of:
        Non-maximum suppression
        """

        """
        Start of:
        Drawing bounding boxes and labels
        """

        # Checking if there is at least one detected object
        # after non-maximum suppression
        if len(results) > 0:
            # Going through indexes of results
            for i in results.flatten():
                # Getting current bounding box coordinates,
                # its width and height
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                # Preparing colour for current bounding box
                # and converting from numpy array to list
                colour_box_current = self.colours[class_numbers[i]].tolist()

                # # # Check point
                # print(type(colour_box_current))  # <class 'list'>
                # print(colour_box_current)  # [172 , 10, 127]

                # Drawing bounding box on the original current frame
                cv2.rectangle(frame, (x_min, y_min),
                              (x_min + box_width, y_min + box_height),
                              colour_box_current, 2)

                # Preparing text with label and confidence for current bounding box
                text_box_current = '{}: {:.4f}'.format(self.labels[int(class_numbers[i])],
                                                       confidences[i])

                # Putting text with label and confidence on the original image
                cv2.putText(frame, text_box_current, (x_min, y_min - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour_box_current, 2)

        """
        End of:
        Drawing bounding boxes and labels
        """

        return frame

    """
    End of:
    Reading frames in the loop
    """
