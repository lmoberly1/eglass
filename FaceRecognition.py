import dlib
import csv
import numpy as np
import pandas as pd
from PIL import Image as im
import cv2 as cv


class FaceRecognition():
    """
    Given image path, return name of the person in the image.
    """

    def __init__(self, pred_model_path=None, rec_model_path=None):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(pred_model_path)
        self.recognizer = dlib.face_recognition_model_v1(rec_model_path)        


    def get_distance(self, new_encodings, known_encodings, threshold=0.6):
        """
        Calculate the distance between the new encoding and the known encodings.
        :param new_encodings: encodings of faces in the image, shape (n, 128)
        :param known_encodings: encodings of faces in the database, shape (m, 128)
        """
        distances = (new_encodings - known_encodings[:, np.newaxis])
        return np.linalg.norm(distances, axis=2).T
        

    def get_encodings(self, img):
        """
        Given image path, return encoding for faces of each person in the image
        :param img_path: numpy array of rgb image
        """

        # Detect faces in image
        dets = self.detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))

        # Get location and encoding for each face
        detection_encodings = []
        locations = []
        for i, detection in enumerate(dets):
            shape = self.predictor(img, detection)
            # Get aligned face
            face_chip = dlib.get_face_chip(img, shape)
            # Encode face
            face_descriptor_from_prealigned_image = self.recognizer.compute_face_descriptor(face_chip)
            detection_encodings.append(tuple(face_descriptor_from_prealigned_image))
            locations.append(detection)
        
        return np.array(detection_encodings), np.array(locations)

    def draw_frame(self, frame, names, locations, color=(0, 255, 0), thickness=2):
        """
        Draw bounding box and name of person on frame
        :param frame: numpy array of rgb image
        :param names: list of names of people in the image
        :param locations: list of bounding boxes of people in the image
        """
        for i in range(len(names)):
            frame = cv.rectangle(frame, (locations[i].left(), locations[i].top()), (locations[i].right(), locations[i].bottom()), color, thickness)
            frame = cv.putText(frame, names[i], (locations[i].left(), locations[i].top()), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA)
        return frame


