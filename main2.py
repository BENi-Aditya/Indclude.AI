import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import pyttsx3
import threading

class SignLanguageDetector:
    def __init__(self, window):
        self.window = window
        self.window.title("Sign Language Detector")
        self.window.geometry("1000x700")
        self.window.configure(bg="#f0f0f0")

        self.setup_styles()
        self.create_widgets()
        self.setup_variables()

        self.cap = None
        self.camera_thread = None

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=10, font=("Arial", 12))
        style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
        style.configure("Header.TLabel", font=("Arial", 24, "bold"), foreground="#2c3e50", background="#f0f0f0")

    def create_widgets(self):
        header = ttk.Label(self.window, text="Sign Language Detector", style="Header.TLabel")
        header.pack(pady=20)

        self.video_frame = ttk.Frame(self.window, borderwidth=2, relief="groove")
        self.video_frame.pack(pady=10)

        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        control_frame = ttk.Frame(self.window)
        control_frame.pack(pady=20)

        self.start_button = ttk.Button(control_frame, text="Start Detection", command=self.toggle_detection)
        self.start_button.grid(row=0, column=0, padx=10)

        self.speak_button = ttk.Button(control_frame, text="Speak Sign", command=self.speak_sign, state="disabled")
        self.speak_button.grid(row=0, column=1, padx=10)

        self.exit_button = ttk.Button(control_frame, text="Exit", command=self.window.quit)
        self.exit_button.grid(row=0, column=2, padx=10)

        self.status_label = ttk.Label(self.window, text="Status: Not Detecting", style="TLabel")
        self.status_label.pack(pady=10)

        self.detected_sign_label = ttk.Label(self.window, text="No sign detected", font=("Arial", 18, "bold"))
        self.detected_sign_label.pack(pady=10)

    def setup_variables(self):
        self.is_detecting = False
        self.detected_sign = tk.StringVar()
        self.detected_sign.set("No sign detected")

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

        self.finger_tips = [8, 12, 16, 20]
        self.thumb_tip = 4

    def toggle_detection(self):
        if not self.is_detecting:
            self.start_detection()
        else:
            self.stop_detection()

    def start_detection(self):
        self.is_detecting = True
        self.start_button.config(text="Stop Detection")
        self.speak_button.config(state="normal")
        self.status_label.config(text="Status: Detecting")
        
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        
        if self.camera_thread is None:
            self.camera_thread = threading.Thread(target=self.update_frame)
            self.camera_thread.daemon = True
            self.camera_thread.start()

    def stop_detection(self):
        self.is_detecting = False
        self.start_button.config(text="Start Detection")
        self.speak_button.config(state="disabled")
        self.status_label.config(text="Status: Not Detecting")

    def update_frame(self):
        while self.is_detecting:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mpDraw.draw_landmarks(frame, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
                    
                    detected_sign = self.detect_sign(hand_landmarks)
                    self.detected_sign.set(detected_sign)
                    self.detected_sign_label.config(text=detected_sign)

                    # Display the detected sign on the video feed
                    cv2.putText(frame, detected_sign, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.video_label.config(image=photo)
                self.video_label.image = photo

    def detect_sign(self, hand_landmarks):
        lm_list = []
        for id, lm in enumerate(hand_landmarks.landmark):
            lm_list.append(lm)

        finger_fold_status = []
        for tip in self.finger_tips:
            if lm_list[tip].y < lm_list[tip - 2].y:
                finger_fold_status.append(True)
            else:
                finger_fold_status.append(False)

        if lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
           lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
            return 'HELP.'

        elif lm_list[4].y < lm_list[2].y and lm_list[8].y > lm_list[6].y and lm_list[12].y < lm_list[10].y and \
             lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
            return 'Perfect.'

        elif lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
             lm_list[16].y > lm_list[14].y and lm_list[20].y < lm_list[18].y:
            return 'Good to see you.'

        elif lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
             lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return 'ME'

        elif lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
             lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return 'Thank You'

        elif lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
             lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x:
            return 'Move Right'

        elif lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
             lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
            return 'Move Left'

        if all(finger_fold_status):
            if lm_list[self.thumb_tip].y < lm_list[self.thumb_tip - 1].y < lm_list[self.thumb_tip - 2].y:
                return 'I Like it'
            elif lm_list[self.thumb_tip].y > lm_list[self.thumb_tip - 1].y > lm_list[self.thumb_tip - 2].y:
                return 'I dont like it.'

        return 'No sign detected'

    def speak_sign(self):
        engine = pyttsx3.init()
        engine.say(self.detected_sign.get())
        engine.runAndWait()

if __name__ == "__main__":
    root = tk.Tk()
    app = SignLanguageDetector(root)
    root.mainloop()