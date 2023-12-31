from flask import Flask, render_template, Response
import cv2
import mediapipe as mp # Import mediapipe

import pickle 

## to create our dataset 
import csv 
import os
import numpy as np

# to create the model
import pandas as pd
from sklearn.model_selection import train_test_split


mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

### CLASSIFIER
def load_model(exercise):
    with open(exercise+'.pkl', 'rb') as f:
            return pickle.load(f)


app=Flask(__name__)

cap = cv2.VideoCapture(1)

def gen_frames(exercise):
    model = load_model(exercise)
    #exercise="right-curl"
    exercise_down=exercise+"-down"
    exercise_up=exercise+"-up"
    counter = 0
    stage = None
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            
            # Recolor Feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False        
            
            # Make Detections
            results = holistic.process(image)
            # print(results.face_landmarks)
            
            # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks
            
            # Recolor image back to BGR for rendering
            image.flags.writeable = True   
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 1. Draw face landmarks
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                    mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                                    )
            
            # 2. Right hand
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                    )

            # 3. Left Hand
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                    )

            # 4. Pose Detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )
            
            
            
            # export coordinates
            try:
                # extracting pose landmarks
                pose = results.pose_landmarks.landmark
                pose_row = list(np.array([[landmark.x,landmark.y,landmark.y,landmark.visibility] for landmark in pose]).flatten())
                # extracting face landmarks
                face = results.face_landmarks.landmark
                face_row = list(np.array([[landmark.x,landmark.y,landmark.y,landmark.visibility] for landmark in face]).flatten())

                # Concate rows
                row = pose_row+face_row

                # MAKE DETECTIONS
                X = pd.DataFrame([row])
                body_language_class = model.predict(X)[0]
                body_language_prob = model.predict_proba(X)[0]
                print(body_language_class, body_language_prob)
                
                print(model.predict(X))
                prob = round(body_language_prob[np.argmax(body_language_prob)],2)
                blue, green, red = 34, 200, 203
                if(prob>0.75):
                    blue, green, red = 34, 203, 48

                # Grab ear coords
                coords = tuple(np.multiply(
                                np.array(
                                    (results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].x, 
                                    results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].y))
                            , [640,480]).astype(int))
                
                cv2.rectangle(image, 
                            (coords[0], coords[1]+5), 
                            (coords[0]+len(body_language_class)*20, coords[1]-30), 
                            (245, 117, 16), -1)
                cv2.putText(image, body_language_class, coords, 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (blue, green, red), 2, cv2.LINE_AA)
                
                # Get status box
                cv2.rectangle(image, (0,0), (image.shape[1], 60), (0, 0, 0), -1)
                
                
                # Display Class
                # cv2.putText(image, 'CLASS'
                #             , (95,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                # cv2.putText(image, body_language_class.split(' ')[0]
                #             , (90,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Display Probability
                cv2.putText(image, 'PROB'
                            , (15,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(round(body_language_prob[np.argmax(body_language_prob)],2))
                            , (10,42), cv2.FONT_HERSHEY_SIMPLEX, 1, (blue, green, red), 2, cv2.LINE_AA)
                
                # display reps
                cv2.putText(image, 'REPS', (image.shape[1]-60,15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(image, str(counter), 
                        (image.shape[1]-51,42), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                

                if stage == exercise_down and body_language_class == exercise_up:
                    counter += 1

                stage = body_language_class

                print(counter)

                
                
            except:
                cv2.rectangle(image, (0,0), (image.shape[1], 60), (0, 0, 0), -1)
                cv2.putText(image, 'Posicionate en la imagen'
                            , (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)

            

            ret, buffer = cv2.imencode('.jpg', image)                
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # while True:
    #     success, frame = camera.read()  # read the camera frame
    #     if not success:
    #         break
    #     else:
    #         ret, buffer = cv2.imencode('.jpg', frame)
    #         frame = buffer.tobytes()
    #         yield (b'--frame\r\n'
    #                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed/<exercise>')
def video_feed(exercise):
    return Response(gen_frames(exercise), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=='__main__':
    app.run(debug=True)