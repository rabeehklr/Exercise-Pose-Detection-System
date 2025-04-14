import csv
import datetime
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import os
import threading

# Exercise-specific state machines
class BaseExercise:
    def __init__(self):


        
        self.state = 'start'    
        self.rep_count = 0
        self.incorrect_rep_count = 0
        self.angle_buffer = []
        self.buffer_size = 10  # Adjust this value as needed
        self.previous_feedback = ""

    

    def reset(self):
        self.state = 'start'
        self.rep_count = 0
        self.incorrect_rep_count = 0
        self.angle_buffer.clear()

    def update_angle_buffer(self, angle):
        self.angle_buffer.append(angle)
        if len(self.angle_buffer) > self.buffer_size:
            self.angle_buffer.pop(0)

class LateralRaiseExercise(BaseExercise):
    def __init__(self):
        super().__init__()
        self.min_angle_shoulder_elbow_wrist = 120
        
        self.start_angle_hip_shoulder_elbow = 20
        self.end_angle_hip_shoulder_elbow = 80

    def update_state(self, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow):
        if self.state == 'start':
            if angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'start'
            elif self.start_angle_hip_shoulder_elbow < angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"

        elif self.state == 'moving_up' or self.state =="invalid":
            if angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'top'
            elif self.start_angle_hip_shoulder_elbow < angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'moving_up'
            elif angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'bottom'
            else:
                    self.state ="invalid"

        elif self.state == 'top' or self.state =="invalid":
            if self.end_angle_hip_shoulder_elbow > angle_hip_shoulder_elbow > self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'moving_down'
            elif angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'top'
            else:
                    self.state ="invalid"

        elif self.state == 'moving_down' or self.state =="invalid":
            if angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'bottom'
                self.check_repetition()
            elif angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'top'
            elif self.end_angle_hip_shoulder_elbow > angle_hip_shoulder_elbow > self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'moving_down'
            else:
                    self.state ="invalid"

        elif self.state == 'bottom' or self.state =="invalid":
            if angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'bottom'
            elif self.start_angle_hip_shoulder_elbow < angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow and angle_shoulder_elbow_wrist >= self.min_angle_shoulder_elbow_wrist:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"
            

        self.update_angle_buffer(angle_shoulder_elbow_wrist)

    def check_repetition(self):
        if len(self.angle_buffer) >= self.buffer_size:
            repetition_pattern = [self.min_angle_shoulder_elbow_wrist, self.end_angle_hip_shoulder_elbow, self.end_angle_hip_shoulder_elbow, self.min_angle_shoulder_elbow_wrist]
            for i in range(len(self.angle_buffer) - len(repetition_pattern) + 1):
                if all(abs(self.angle_buffer[i + j] - repetition_pattern[j]) < 10 for j in range(len(repetition_pattern))):
                    self.rep_count += 1
                    break
# Shoulder Press Exercise
class ShoulderPressExercise(BaseExercise):
    def __init__(self):
        super().__init__()
        self.start_angle_shoulder_elbow_wrist = 60
        self.end_angle_shoulder_elbow_wrist = 150
        self.start_angle_hip_shoulder_elbow = 80
        self.end_angle_hip_shoulder_elbow = 160


    def update_state(self, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow):
        if self.state == 'start':
            if angle_shoulder_elbow_wrist < self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow < self.start_angle_hip_shoulder_elbow:
                self.state = 'start'
            elif self.start_angle_shoulder_elbow_wrist <= angle_shoulder_elbow_wrist < self.end_angle_shoulder_elbow_wrist and self.start_angle_hip_shoulder_elbow <= angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"

        elif self.state == 'moving_up' or self.state =="invalid":
            if angle_shoulder_elbow_wrist >= self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow:
                self.state = 'top'
            elif self.start_angle_shoulder_elbow_wrist <= angle_shoulder_elbow_wrist < self.end_angle_shoulder_elbow_wrist and self.start_angle_hip_shoulder_elbow <= angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            elif self.start_angle_shoulder_elbow_wrist > angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow:
                self.state = 'bottom'
            elif angle_shoulder_elbow_wrist >= 140 and angle_hip_shoulder_elbow <=120 or  angle_shoulder_elbow_wrist <= 140 and angle_hip_shoulder_elbow >=120 :
                    self.state ="invalid"
            
        elif self.state == 'top' or self.state =="invalid":
            if self.end_angle_shoulder_elbow_wrist > angle_shoulder_elbow_wrist > self.start_angle_shoulder_elbow_wrist and self.start_angle_hip_shoulder_elbow < angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow:
                self.state = 'moving_down'
            elif angle_shoulder_elbow_wrist >= self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow:
                self.state = 'top'
            elif angle_shoulder_elbow_wrist <= 100 and angle_hip_shoulder_elbow >=160:
                self.state ="invalid"
            
        elif self.state == 'moving_down' or self.state =="invalid":
            if angle_shoulder_elbow_wrist <=self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.start_angle_hip_shoulder_elbow:
                self.state = 'bottom'
                self.check_repetition()
            elif self.end_angle_shoulder_elbow_wrist < angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow >= self.end_angle_hip_shoulder_elbow:
                self.state = 'top'
            elif self.end_angle_shoulder_elbow_wrist > angle_shoulder_elbow_wrist > self.start_angle_shoulder_elbow_wrist and self.start_angle_hip_shoulder_elbow < angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow:
                self.state = 'moving_down'
            elif angle_shoulder_elbow_wrist >= 140 and angle_hip_shoulder_elbow <=120 or  angle_shoulder_elbow_wrist <= 140 and angle_hip_shoulder_elbow >=120 :
                    self.state ="invalid"

        elif self.state == 'bottom' or self.state =="invalid":
            if angle_shoulder_elbow_wrist < self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow < self.start_angle_hip_shoulder_elbow:
                self.state = 'bottom'
            elif self.start_angle_shoulder_elbow_wrist <= angle_shoulder_elbow_wrist < self.end_angle_shoulder_elbow_wrist and self.start_angle_hip_shoulder_elbow <= angle_hip_shoulder_elbow < self.end_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"
            
        
        self.update_angle_buffer(angle_shoulder_elbow_wrist)

    def check_repetition(self):
        if len(self.angle_buffer) >= self.buffer_size:
            repetition_pattern = [self.start_angle_shoulder_elbow_wrist, self.end_angle_shoulder_elbow_wrist, self.end_angle_shoulder_elbow_wrist, self.start_angle_shoulder_elbow_wrist]
            for i in range(len(self.angle_buffer) - len(repetition_pattern) + 1):
                if all(abs(self.angle_buffer[i + j] - repetition_pattern[j]) < 10 for j in range(len(repetition_pattern))):
                    self.rep_count += 1
                    break

# Bicep Curl Exercise
class BicepCurlExercise(BaseExercise):
    def __init__(self):
        super().__init__()
        self.start_angle_shoulder_elbow_wrist = 160
        self.end_angle_shoulder_elbow_wrist = 20
        self.max_angle_hip_shoulder_elbow = 30

    def update_state(self, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow):
        if self.state == 'start' :
            if angle_shoulder_elbow_wrist > self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'start'
            elif self.start_angle_shoulder_elbow_wrist >= angle_shoulder_elbow_wrist > self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"
        elif self.state == 'moving_up' or self.state =="invalid" :
            if angle_shoulder_elbow_wrist <= self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'top'
            elif self.start_angle_shoulder_elbow_wrist >= angle_shoulder_elbow_wrist > self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            elif self.start_angle_shoulder_elbow_wrist < angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'bottom'
            else:
                    self.state ="invalid"

        elif self.state == 'top' or self.state =="invalid":
            if self.end_angle_shoulder_elbow_wrist < angle_shoulder_elbow_wrist < self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'moving_down'
            elif angle_shoulder_elbow_wrist <= self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'top'
            else:
                    self.state ="invalid"

        elif self.state == 'moving_down' or self.state =="invalid":
            if angle_shoulder_elbow_wrist >= self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'bottom'
                self.check_repetition()
            elif self.end_angle_shoulder_elbow_wrist > angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'top'
            elif self.end_angle_shoulder_elbow_wrist < angle_shoulder_elbow_wrist < self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'moving_down'
            else:
                    self.state ="invalid"

        elif self.state == 'bottom' or self.state =="invalid":
            if angle_shoulder_elbow_wrist > self.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'bottom'
            elif self.start_angle_shoulder_elbow_wrist >= angle_shoulder_elbow_wrist > self.end_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= self.max_angle_hip_shoulder_elbow:
                self.state = 'moving_up'
            else:
                    self.state ="invalid"
            

        self.update_angle_buffer(angle_shoulder_elbow_wrist)

    def check_repetition(self):
        if len(self.angle_buffer) >= self.buffer_size:
            repetition_pattern = [self.start_angle_shoulder_elbow_wrist, self.end_angle_shoulder_elbow_wrist, self.end_angle_shoulder_elbow_wrist, self.start_angle_shoulder_elbow_wrist]
            for i in range(len(self.angle_buffer) - len(repetition_pattern) + 1):
                if all(abs(self.angle_buffer[i + j] - repetition_pattern[j]) < 10 for j in range(len(repetition_pattern))):
                    self.rep_count += 1
                    break

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()



# Initialize previous state and row
previous_state = None
previous_row = None

def calculate_angle(a, b, c, joint_points):
    if a is None or b is None or c is None:
        return 0.0  # or handle the error in some other way

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    if joint_points == "shoulder_elbow_wrist":
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    elif joint_points == "hip_shoulder_elbow":
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    else:
        return 0.0  # or handle the error in some other way

    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle

    return angle



def provide_feedback(current_state, previous_state, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow):
    feedback_message = ""
    exercise_type = type(exercise_instance).__name__

    if exercise_type == "BicepCurlExercise":
        if current_state == "start":
            if angle_shoulder_elbow_wrist > exercise_instance.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= exercise_instance.max_angle_hip_shoulder_elbow:
                feedback_message = "Start the exercise"
            else:
                feedback_message = "Initial position is incorrect"
        elif current_state == "bottom":
            if previous_state == "moving_up":
                feedback_message = "Complete motion not achieved"
            elif previous_state == "moving_down":
                feedback_message = "Repetition completed"
        elif current_state == "top":
            if previous_state == "moving_up":
                feedback_message = "Curl up completed, now move down"
            elif previous_state == "moving_down":
                feedback_message = "Complete motion not achieved"
        elif current_state == "moving_up":
            if previous_state == "bottom":
                feedback_message = "Continue moving up"
            elif previous_state == "start":
                feedback_message = "Continue moving up"
        elif current_state == "moving_down":
            if previous_state == "top":
                feedback_message = "Continue moving down"
        elif current_state == "invalid":
            
                feedback_message = "Shoulder angle is above limit"

    elif exercise_type == "ShoulderPressExercise":
        if current_state == "start":
            if angle_shoulder_elbow_wrist < exercise_instance.start_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow < exercise_instance.start_angle_hip_shoulder_elbow:
                feedback_message = "Start the exercise"
            else:
                feedback_message = "Initial position is incorrect"
        elif current_state == "bottom":
            if previous_state == "moving_up":
                feedback_message = "Complete motion not achieved"
            elif previous_state == "moving_down":
                feedback_message = "Repetition completed"
        elif current_state == "top":
            if previous_state == "moving_up":
                feedback_message = "Press up completed, now move down"
            elif previous_state == "moving_down":
                feedback_message = "Complete motion not achieved"
        elif current_state == "moving_up":
            if previous_state == "bottom":
                feedback_message = "Continue moving up"
            elif previous_state == "start":
                feedback_message = "Continue moving up"
        elif current_state == "moving_down":
            if previous_state == "top":
                feedback_message = "Continue moving down"
        elif current_state == "invalid":
            
                feedback_message = " Angle is above limit"    

    elif exercise_type == "LateralRaiseExercise":
        if current_state == "start":
            if angle_shoulder_elbow_wrist >= exercise_instance.min_angle_shoulder_elbow_wrist and angle_hip_shoulder_elbow <= exercise_instance.start_angle_hip_shoulder_elbow:
                feedback_message = "Start the exercise"
            else:
                feedback_message = "Initial position is incorrect"
        elif current_state == "bottom":
            if previous_state == "moving_up":
                feedback_message = "Complete motion not achieved"
            elif previous_state == "moving_down":
                feedback_message = "Repetition completed"
        elif current_state == "top":
            if previous_state == "moving_up":
                feedback_message = "Raise up completed, now move down"
            elif previous_state == "moving_down":
                feedback_message = "Complete motion not achieved"
        elif current_state == "moving_up":
            if previous_state == "bottom":
                feedback_message = "Continue moving up"
            elif previous_state == "start":
                feedback_message = "Continue moving up"
        elif current_state == "moving_down":
            if previous_state == "top":
                feedback_message = "Continue moving down"
        elif current_state == "invalid":
            
                feedback_message = "Elbow angle is above limit"
    return feedback_message

def write_to_csv(angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow, state, si_no, timestamp):
    global previous_row, previous_state

    row = [timestamp, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow, state, si_no]

    # Check if the row is a duplicate of the previous row or if the state is the same as the previous state
    if row != previous_row and state != previous_state:
        with open('exercise_data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)

        previous_row = row
        previous_state = state

def video_stream():
    global exercise_instance
    cap = cv2.VideoCapture(0)
    angle_shoulder_elbow_wrist = 0
    angle_hip_shoulder_elbow = 0

    def video_loop():
        nonlocal cap, angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (850, 520))
            results = pose.process(image)

            shoulder = elbow = wrist = hip = None
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Check if the required landmarks are detected
                left_shoulder_visible = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility > 0.5
                left_elbow_visible = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility > 0.5
                left_wrist_visible = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility > 0.5
                left_hip_visible = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > 0.5
                right_shoulder_visible = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility > 0.5
                right_elbow_visible = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility > 0.5
                right_wrist_visible = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility > 0.5
                right_hip_visible = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility > 0.5

                if (left_shoulder_visible and left_elbow_visible and left_wrist_visible and left_hip_visible) or \
                    (right_shoulder_visible and right_elbow_visible and right_wrist_visible and right_hip_visible):
                    try:
                        # Get coordinates for the shoulder, elbow, wrist, and hip
                        if left_shoulder_visible and left_elbow_visible and left_wrist_visible and left_hip_visible:
                            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        else:
                            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                            hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                    except Exception as e:
                        display_feedback(f"An error occurred: {e}")
                else:
                    if not left_shoulder_visible and not right_shoulder_visible:
                        display_feedback("Shoulders are not visible")
                    elif not left_elbow_visible and not right_elbow_visible:
                        display_feedback("Elbows are not visible")
                    elif not left_wrist_visible and not right_wrist_visible:
                        display_feedback("Wrists are not visible")
                    elif not left_hip_visible and not right_hip_visible:
                        display_feedback("Hips are not visible")
                    else:
                        display_feedback("Initial position is incorrect")
            else:
                display_feedback("Please do exercise in front of camera.")
            
            
            if shoulder and elbow and wrist and hip:
                angle_shoulder_elbow_wrist = calculate_angle(shoulder, elbow, wrist, "shoulder_elbow_wrist")
                angle_hip_shoulder_elbow = calculate_angle(hip, shoulder, elbow, "hip_shoulder_elbow")
                
                angle_shoulder_elbow_wrist = round(angle_shoulder_elbow_wrist, 1)
                angle_hip_shoulder_elbow = round(angle_hip_shoulder_elbow, 1)

            update_angle_state_label(angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow, shoulder, elbow, wrist, hip)
            update_landmark_state_label(shoulder, elbow, wrist, hip)
            
            # Check if exercise_instance is not None before calling update_state
            if exercise_instance is not None:
                exercise_instance.update_state(angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow)
                state = exercise_instance.state
                si_no = exercise_instance.rep_count + exercise_instance.incorrect_rep_count + 1
                update_exercise_state_label(state)
                
            else:
                display_feedback("Exercise is not selected.")
                continue

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # Write data to CSV file
            write_to_csv(angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow, state, si_no, timestamp)

            # Read the last two rows from the CSV file
            with open('exercise_data.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                if len(rows) >= 2:
                    previous_row = rows[-2]
                    current_row = rows[-1]

                    previous_state = previous_row[3]
                    current_state = current_row[3]
                    

                    if current_row[2] != 'start' and current_row[3] != 'start':
                        current_angle_shoulder_elbow_wrist = float(current_row[1])
                        current_angle_hip_shoulder_elbow = float(current_row[2])
                    else:
                        current_angle_shoulder_elbow_wrist = 0.0
                        current_angle_hip_shoulder_elbow = 0.0

                    feedback_message = provide_feedback(current_state, previous_state, current_angle_shoulder_elbow_wrist, current_angle_hip_shoulder_elbow)
                elif len(rows) == 1:
                    current_row = rows[0]
                    current_state = current_row[3]
                    current_angle_shoulder_elbow_wrist = float(current_row[1])
                    current_angle_hip_shoulder_elbow = float(current_row[2])
                    feedback_message = provide_feedback(current_state, None, current_angle_shoulder_elbow_wrist, current_angle_hip_shoulder_elbow)
                else:
                    feedback_message = "Start the exercise"

            if feedback_message != exercise_instance.previous_feedback:
                # Update rep counts based on feedback
                if feedback_message == "Repetition completed":
                    exercise_instance.rep_count += 1
                elif feedback_message == "Complete motion not achieved":
                    exercise_instance.incorrect_rep_count += 1

                # Store the current feedback for the next iteration
                exercise_instance.previous_feedback = feedback_message

                # Display feedback
                display_feedback(feedback_message)

            # Update rep counts
             # Update rep counts
            root.after_idle(lambda: correct_reps_label.config(text=f"Correct Reps: {exercise_instance.rep_count}"))
            root.after_idle(lambda: incorrect_reps_label.config(text=f"Incorrect Reps: {exercise_instance.incorrect_rep_count}"))

            # Render the image with pose landmarks
            mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            photo = cv2.imencode('.png', cv_image)[1].tobytes()
            realtime_video_label.photo = tk.PhotoImage(data=photo)
            realtime_video_label.configure(image=realtime_video_label.photo)

            # Update the GUI
            root.update()

    # Start the video loop in a separate thread
    video_thread = threading.Thread(target=video_loop)
    video_thread.start()

def refresh_application():
    # Stop the video stream
    cap.release()
    cap_demo.release()

    # Close the current window
    root.destroy()

    # Restart the application
    os.system(f'python "{__file__}"')

def play_demo_video(exercise):
    global cap_demo
    if cap_demo.isOpened():
        cap_demo.release()
    cap_demo = cv2.VideoCapture(demo_videos[exercise])
    cap_demo.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Set the video position to the beginning
    update_demo_video()

def reset_exercise():
    global exercise_instance
    exercise_instance.reset()
    selected_exercise = exercise_radiobutton_var.get()
    rep_counts[selected_exercise] = 0
    incorrect_rep_counts[selected_exercise] = 0
    correct_reps_label.config(text=f"CORRECT REPS: {rep_counts[selected_exercise]}")
    incorrect_reps_label.config(text=f"INCORRECT REPS: {incorrect_rep_counts[selected_exercise]}")

def exercise_selected():
    global exercise_instance
    selected_exercise = exercise_radiobutton_var.get()
    update_exercise_label(selected_exercise)
    if selected_exercise == "Bicep Curl":
        exercise_instance = BicepCurlExercise()
        rep_counts[selected_exercise] = 0
        incorrect_rep_counts[selected_exercise] = 0
        play_demo_video(selected_exercise)
    elif selected_exercise == "Shoulder Press":
        exercise_instance = ShoulderPressExercise()
        rep_counts[selected_exercise] = 0
        incorrect_rep_counts[selected_exercise] = 0
        play_demo_video(selected_exercise)
    elif selected_exercise == "Lateral Raise":
        exercise_instance = LateralRaiseExercise()
        rep_counts[selected_exercise] = 0
        incorrect_rep_counts[selected_exercise] = 0
        play_demo_video(selected_exercise)
    
    
    else:
        display_feedback(f"select a exercise")
        return

   

def update_demo_video():
    global cap_demo
    ret, frame = cap_demo.read()
    if not ret:
        cap_demo.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Set the video position to the beginning
        ret, frame = cap_demo.read()  # Read the first frame again

    if ret:
        frame = cv2.resize(frame, (610, 520))
        cv_demo_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        photo_demo = ImageTk.PhotoImage(image=cv_demo_image)
        root.after_idle(lambda: demo_video_label.configure(image=photo_demo))
        demo_video_label.imgtk = photo_demo
        root.after(10, update_demo_video)  # Schedule the next update
    else:
        root.after(100, update_demo_video)  # Try again after 100 ms  # Try again after 100 ms

# Feedback Module
def display_feedback(feedback):
    message = f"      ( ◉o◉) :   {feedback}"
    root.after_idle(lambda: feedback_listbox.insert(tk.END, message))
    root.after_idle(feedback_listbox.yview, tk.END)

def update_exercise_state_label(state):
    exercise_state_label.config(text=f"Exercise State: {state}")

def update_exercise_label(selected_exercise):
    exercise_label.config(text=f"Exercise : {selected_exercise}")

def update_angle_state_label(angle_shoulder_elbow_wrist, angle_hip_shoulder_elbow, shoulder, elbow, wrist, hip):
    if shoulder and elbow and wrist and hip:
        angle_label.config(text=f"Angles: E:{angle_shoulder_elbow_wrist}  S:{angle_hip_shoulder_elbow}")
    else:
        angle_label.config(text="Angles: E:None  S:None")

def update_landmark_state_label(shoulder, elbow, wrist, hip):
    if shoulder and elbow and wrist and hip:
        landmark_label.config(text="Landmarks: Achieved ")
    else:
        landmark_label.config(text="Landmarks: Not Achieved ")

# ======== MAIN ========

# Initialize MediaPipe Pose class
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

exercise_instance = None
# Initialize the exercise instance




# Initialize the rep counters, incorrect rep counters, and states for each exercise
exercise_states = {}
rep_counts = {}
incorrect_rep_counts = {}

# Demo video paths
demo_videos = {
    'Bicep Curl': r'C:\Users\RABEEH\Desktop\rabeeh\bicep.mp4',
    'Shoulder Press': r'C:\Users\RABEEH\Desktop\rabeeh\shoulder.mp4',
   'Lateral Raise': r'C:\Users\RABEEH\Desktop\rabeeh\lateral.mp4'
}

# Main window
root = tk.Tk()
root.title("Exercise Pose Correction System")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width)
window_height = int(screen_height)
root.geometry(f"{window_width}x{window_height}")

# Load background image
bg_image = Image.open(r"C:\Users\RABEEH\Desktop\rabeeh\bg.jpg")
bg_photo = ImageTk.PhotoImage(bg_image)

# Create background label
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


# About Window
def open_about_window():
    about_window = tk.Toplevel(root)
    about_window.title("About Us")
    about_window.geometry("800x600")

    # Load and set background image
    about_bg_image = Image.open(r"C:\Users\RABEEH\Desktop\rabeeh\bg.jpg")
    about_bg_photo = ImageTk.PhotoImage(about_bg_image)
    about_bg_label = tk.Label(about_window, image=about_bg_photo)
    about_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Keep a reference to the PhotoImage object
    about_bg_label.image = about_bg_photo

# Exit window
def close_application():
    root.destroy()

# Frames
title_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
title_frame.place(x=19, y=5, width=1480.5, height=40)

realtime_video_frame = tk.Frame(root, bg="gray", bd=2, relief=tk.SOLID)
realtime_video_frame.place(x=20, y=50, width=850, height=520)

demo_video_frame = tk.Frame(root, bg="gray", bd=2, relief=tk.SOLID)
demo_video_frame.place(x=890, y=50, width=610, height=520)

your_activity_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
your_activity_frame.place(x=20, y=580, width=350, height=200)

feedback_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
feedback_frame.place(x=390, y=580, width=610, height=200)

exercise_list_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
exercise_list_frame.place(x=1020, y=580, width=230, height=200)

other_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
other_frame.place(x=1270, y=580, width=230, height=200)

# Labels
title_label = tk.Label(title_frame, text="Exercise Pose Correction System", font=("spot", 18, "bold"))
title_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

realtime_video_label = tk.Label(realtime_video_frame, text="SELECT AN EXERCISE FROM THE LIST" ,  font=("Helvetica", 14, "bold"))
realtime_video_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Define the label for displaying the video
demo_video_label = tk.Label(demo_video_frame)
demo_video_label.pack(expand=True, fill=tk.BOTH)

# Create a label for displaying the exercise state
exercise_state_label = tk.Label(realtime_video_frame, font=("Helvetica", 12, "bold"))
exercise_state_label.place(x=10, y=480)

exercise_label = tk.Label(realtime_video_frame, font=("Helvetica", 12, "bold"))
exercise_label.place(x=10, y=20)


angle_label = tk.Label(realtime_video_frame, font=("Helvetica", 12, "bold"))
angle_label.place(x=300, y=480)

landmark_label = tk.Label(realtime_video_frame, font=("Helvetica", 12, "bold"))
landmark_label.place(x=530, y=480)

reset_button = tk.Button(your_activity_frame, text="   Reset    ", font=("Helvetica", 12, "bold"), command=reset_exercise)
reset_button.place(x=130, y=100)
activity_label = tk.Label(your_activity_frame, text="YOUR ACTIVITY"  , font=("Helvetica", 14, "bold"))
activity_label.pack(pady=10)

correct_reps_label = tk.Label(your_activity_frame, text="CORRECT REPS: 0", font=("Helvetica", 12, "bold"))
correct_reps_label.pack(pady=5)

incorrect_reps_label = tk.Label(your_activity_frame, text="INCORRECT REPS: 0", font=("Helvetica", 12, "bold"))
incorrect_reps_label.pack(pady=5)

feedback_label = tk.Label(feedback_frame, text="FEEDBACK", font=("Helvetica", 14, "bold"))
feedback_label.place(x=230, y=10)

exercise_list_label = tk.Label(exercise_list_frame, text="EXERCISE LIST", font=("Helvetica", 12, "bold"))
exercise_list_label.pack(pady=10)

refresh_button = tk.Button(other_frame, text="   Refresh    ", font=("Helvetica", 12, "bold"), command=refresh_application)
refresh_button.place(x=65, y=20)
about_button = tk.Button(other_frame, text="  About Us  ", font=("Helvetica", 12, "bold"), command=open_about_window)
about_button.place(x=65, y=80)
exit_button = tk.Button(other_frame, text="       Exit        ", font=("Helvetica", 12, "bold"), command=close_application)
exit_button.place(x=65, y=140)

# Exercise List
exercise_list = ["Bicep Curl","Shoulder Press","Lateral Raise"]
exercise_radiobutton_var = tk.StringVar(value=exercise_list[0])
exercise_radiobuttons = [tk.Radiobutton(exercise_list_frame, text=exercise, variable=exercise_radiobutton_var,
                                        value=exercise, command=lambda: exercise_selected()) for exercise in exercise_list]
for i, radiobutton in enumerate(exercise_radiobuttons):
    radiobutton.pack(anchor=tk.W, padx=20)

# Feedback Listbox
feedback_listbox = tk.Listbox(feedback_frame, width=46, height=1,font=("Helvetica", 16, "bold"))
feedback_listbox.place(x=300,y=90, anchor=tk.CENTER,height=30)

# Start the video stream
cap = cv2.VideoCapture(0)
no_cam_image = None
video_stream()

# Demo video capture object
cap_demo = cv2.VideoCapture()

# Run the application
root.mainloop()

# Release the video capture objects
cap.release()
cap_demo.release()