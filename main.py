from tkinter import *
from PIL import Image, ImageTk
import cv2
from tkinter import filedialog
from flask import Flask, render_template
import mediapipe as mp
import pyttsx3
import threading


app = Flask(__name__)


win = Tk()
width=win.winfo_screenwidth()
height=win.winfo_screenheight()
win.geometry("%dx%d" % (width, height))
win.configure(bg="#00ff4c")
win.title('Sign Language Converter')

global img, finalImage, finger_tips, thumb_tip, cap, image, rgb, hand, results, _, w, \
    h, status, mpDraw, mpHands, hands, label1, btn, btn2

cap = None
camera_thread = None

Label(win,text='INCLUDE.AI',font=('Helvatica',64,'italic'),bd=5,bg='#199ef3',fg='black',relief=SOLID,width=100 )\
     .pack(pady=15,padx=20)

def wine():
    global finger_tips, thumb_tip, mpDraw, mpHands, cap, w, h, hands, label1, check, img
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    w = 500
    h = 400

    if cap:
        cap.release()

    label1 = Label(win, width=w, height=h, bg="#FFFFF7")
    label1.place(x=40, y=200)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

def live():
    global v
    global upCount
    global cshow, img
    cshow = 0
    upCount = StringVar()
    while True:
        _, img = cap.read()
        img = cv2.resize(img, (w, h))
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(hand.landmark):
                    lm_list.append(lm)
                finger_fold_status = []

                for tip in finger_tips:
                    x, y = int(lm_list[tip].x * w), int(lm_list[tip].y * h)
                    if lm_list[tip].x < lm_list[tip - 2].x:
                        finger_fold_status.append(True)
                    else:
                        finger_fold_status.append(False)

                print(finger_fold_status)
                x, y = int(lm_list[8].x * w), int(lm_list[8].y * h)
                print(x, y)
                # stop
                if lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[0].x < \
                        lm_list[5].x:
                    cshow = 'HELP.'
                    upCount.set('HELP.')
                    print('HELP.')
                # okay
                elif lm_list[4].y < lm_list[2].y and lm_list[8].y > lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[0].x < \
                        lm_list[5].x:
                    cshow = 'Perfect.'
                    print('Perfect.')
                    upCount.set('Perfect.')

                # spidey
                elif lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[0].x < \
                        lm_list[5].x:
                    cshow = 'Good to see you.'
                    print('Good to see you.')
                    upCount.set('Good to see you.')

                # Point
                elif lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
                    upCount.set('ME')
                    print("ME")
                    cshow = 'ME'

                # Victory
                elif lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
                    upCount.set('Thank You')
                    print("Thank You")
                    cshow = 'Thank You'

                # Left
                elif lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
                        lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[0].x:
                    upCount.set('Move Right')
                    print("Move Right")
                    cshow = 'Move Right'
                # Right
                elif lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
                        lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
                    upCount.set('Move Left')
                    print("Move Left")
                    cshow = 'Move Left'

                if all(finger_fold_status):
                    # like
                    if lm_list[thumb_tip].y < lm_list[thumb_tip - 1].y < lm_list[thumb_tip - 2].y and lm_list[0].x < lm_list[3].y:
                        print("I like it")
                        upCount.set('I Like it')
                        cshow = 'I Like it'
                    # Dislike
                    elif lm_list[thumb_tip].y > lm_list[thumb_tip - 1].y > lm_list[thumb_tip - 2].y and lm_list[0].x < lm_list[3].y:
                        upCount.set('I dont like it.')
                        print("I dont like it.")
                        cshow = 'I dont like it.'

                mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)
            cv2.putText(rgb, f'{cshow}', (10, 50),
                        cv2.FONT_HERSHEY_COMPLEX, .75, (0, 255, 255), 2)

        image = Image.fromarray(rgb)
        finalImage = ImageTk.PhotoImage(image)
        label1.configure(image=finalImage)
        label1.image = finalImage



@app.route('/')
def index():
    return render_template('index.html')

def start_camera():
    global camera_thread
    if camera_thread is None:
        camera_thread = threading.Thread(target=live)
        camera_thread.daemon = True
        camera_thread.start()

def voice():
    engine = pyttsx3.init()
    engine.say((upCount.get()))
    engine.runAndWait()

def video():
    global cap, ex, label1

    if cap:
        cap.release()
        cap = None
        label1.configure(image=None)

    filename = filedialog.askopenfilename(initialdir="/", title="Select file ",
                                          filetypes=(("mp4 files", ".mp4"), ("all files", ".")))
    cap = cv2.VideoCapture(filename)
    w = 500
    h = 400
    label1 = Label(win, width=w, height=h, relief=GROOVE)
    label1.place(x=40, y=200)
    live()

wine()

Button(win, text='Live', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'),
       command=start_camera).place(x=width - 250, y=400)
#Button(win, text='Video', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'),
#       command=video).place(x=width - 250, y=450)
#Button(win, text='Sound', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'),
 #      command=voice).place(x=width - 250, y=500)
#Button(win, text='Change Vid', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5,
 #      font=('Helvatica', 12, 'bold'), command=video).place(x=width - 250, y=550)
Button(win, text='Exit', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'),
       command=win.destroy).place(x=width - 250, y=600)

win.mainloop()