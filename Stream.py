import cv2 as cv
import numpy as np
import os
import sys
from FaceRecognition import FaceRecognition
from Data import Data
try:
    from picamera2 import Picamera2
except:
    print("Couldn't install Picamera")

class Stream():

    def __init__(self):
        self.FaceRecognition = FaceRecognition('./models/shape_predictor_5_face_landmarks.dat', './models/dlib_face_recognition_resnet_model_v1.dat')
        self.Data = Data()
        self.data = self.Data.data
        self.picam = None


    def mark_data(self, frame):
        """
        Retrieve face_encodings and locations from frame:
        :param frame: numpy array of rgb image
        """
        face_encodings, locations = self.FaceRecognition.get_encodings(frame)
        names = []
        if len(face_encodings) != 0:
            existing_encodings = np.array(list(self.data["encoding"]))
            distances = self.FaceRecognition.get_distance(face_encodings, existing_encodings)
            # Find the index of the encoding with the minimum distance for each face
            min_indices = np.argmin(distances, axis=1)
            min_distances = distances[np.arange(len(distances)), min_indices] 
            names = np.where(min_distances > 0.6, 'Unknown', self.data["name"].values[min_indices])
        return face_encodings, locations, names


    def label_image(self, path_to_data_dir):
        """
        Load images from directory for face encoding and data storage
        :param path_to_data_dir: path to directory containing images
        """
        # Load images from directory for face encoding and data storage
        for filename in os.listdir(path_to_data_dir):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                img_path = os.path.join(path_to_data_dir, filename)
                img = cv.imread(img_path)
                face_encodings, locations, names = self.mark_data(img)
                print('Names: ', names)
                for i, name in enumerate(names):
                    if name == 'Unknown':
                        frame = self.FaceRecognition.draw_frame(img, ["Unknown"], [locations[i]], color=(255, 0, 0), thickness=2)
                        cv.imshow('Label Face', frame)
                        print('Please press Enter to label face.')
                        if cv.waitKey(0) == ord('\n'):
                            cv.destroyWindow('Label Face')
                        # Wait for user to press 'enter' to move on and destroy window
                        new_name = input("Enter name: ")
                        new_encoding = face_encodings[i]
                        if (new_name):
                            self.Data.insert_data(new_encoding, new_name)   
                            print('Successfully saved data') 


    def run_video(self, webcam_id):
        """
        Capture video from webcam and run face recognition
        :param webcam_id: id of webcam
        """
        cap = cv.VideoCapture(webcam_id)
        
        if not cap.isOpened():
            exit()
        try:
            # Infinite Play Loop
            i = 0
            while (True):
                i += 1
                has_frame, frame = cap.read()
                key = cv.waitKey(1)
                if key == ord('q'):
                    break
                try:
                    # Facial detection
                    if (i % 2 == 0):
                        print('Capturing frame for detection...')
                        i = 0
                        face_encodings, locations, names = self.mark_data(frame)
                        frame = self.FaceRecognition.draw_frame(frame, names, locations) 
                        cv.imshow('Video Output', frame)
                except Exception as e:
                    print('Exception: ', e)
                    break
        except KeyboardInterrupt:
            print('End Program.')

            
    def run_pi_video(self, conn=None):
        """
        Capture video from picamera and run face recognition
        """
        print('RUNNING PI VIDEO')
        try:
            self.picam = Picamera2()
            self.picam.start()
        except:
            print("Couldn't start Picam")

        for i in range(5):
            frame = self.picam.capture_array()
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)
            face_encodings, locations, names = self.mark_data(frame) 
            conn.send([42, None, 'hello', i])
        conn.send(None)
        conn.close()
        return 

        # try:
        #     # Infinite Play Loop
        #     i = 1
        #     while (i != 0):
        #         i += 1
        #         frame = self.picam.capture_array()
        #         frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #         frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)
        #         # key = cv.waitKey(1)
        #         # if key == ord('q'):
        #         #     break
        #         try:
        #             # Facial detection
        #             if (i % 2 == 0):
        #                 print('Capturing frame for detection...')
        #                 i = 0
        #                 face_encodings, locations, names = self.mark_data(frame)
        #                 # for name in names:
        #                 #     shared_list.append(name)
        #                 shared_list[0] = 'luke'
        #                 frame = self.FaceRecognition.draw_frame(frame, names, locations) 
        #                 # cv.imshow('Video Output', frame)
        #         except Exception as e:
        #             print('Exception: ', e)
        #             break
        # except KeyboardInterrupt:
        #     print('End Program')
                    


if __name__ == '__main__':
    stream = Stream()
    program = sys.argv[1]
    if program == 'label':
        stream.label_image('./images')
    elif program == 'video':
        stream.run_video(0)
    elif program == 'pivideo':
        stream.run_pi_video()
