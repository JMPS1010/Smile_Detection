import cv2
import dlib
import numpy as np
import threading
import time
import os
import csv
import tkinter as tk
from datetime import datetime
from win10toast import ToastNotifier
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageTk

notifier = ToastNotifier()
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

smile_factor = 1.3
head_tilt_threshold = 15
neutral_lip_distance = None
last_smile_check = 0
log_interval = 10
cap = None
running = True

gui_window = None
video_label = None
icon_ref = None

def get_lip_distance(landmarks):
    top_lip = landmarks[50:53] + landmarks[61:64]
    bottom_lip = landmarks[56:59] + landmarks[65:68]
    return np.linalg.norm(np.mean(top_lip, axis=0) - np.mean(bottom_lip, axis=0))

def get_head_tilt(landmarks):
    dx = landmarks[45][0] - landmarks[36][0]
    dy = landmarks[45][1] - landmarks[36][1]
    return np.degrees(np.arctan2(dy, dx))

def log_not_smiling_event():
    now = datetime.now()
    date_str = now.strftime("%m-%d-%Y")
    time_str = now.strftime("%I:%M %p")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, f"smile_log_{date_str}.csv")
    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date_str, time_str, "Not Smiling"])

def smile_monitor_loop():
    global cap, neutral_lip_distance, last_smile_check, running

    for i in range(10):
        test_cap = cv2.VideoCapture(i)
        if test_cap.read()[0]:
            cap = test_cap
            break
        test_cap.release()
    if cap is None:
        print("No camera available.")
        return

    while running:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            landmarks = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]
            lip_distance = get_lip_distance(landmarks)
            head_tilt = get_head_tilt(landmarks)

            if neutral_lip_distance is None and lip_distance > 10:
                neutral_lip_distance = lip_distance

            smile_threshold = neutral_lip_distance * smile_factor
            is_smiling = lip_distance > smile_threshold and abs(head_tilt) < head_tilt_threshold

            if time.time() - last_smile_check >= log_interval:
                last_smile_check = time.time()
                if not is_smiling:
                    log_not_smiling_event()
                    notifier.show_toast("Smile Reminder", "Serve with a smile 😊", duration=5, threaded=True)

        time.sleep(0.1)

    if cap:
        cap.release()
    cv2.destroyAllWindows()

def update_gui_frame():
    global neutral_lip_distance
    if not (cap and video_label and gui_window and gui_window.winfo_exists()):
        return
    ret, frame = cap.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

            landmarks = predictor(gray, face)
            landmarks = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

            lip_distance = get_lip_distance(landmarks)
            head_tilt = get_head_tilt(landmarks)

            if neutral_lip_distance is None and lip_distance > 10:
                neutral_lip_distance = lip_distance

            smile_threshold = neutral_lip_distance * smile_factor
            is_smiling = lip_distance > smile_threshold and abs(head_tilt) < head_tilt_threshold

            label_text = "Smiling" if is_smiling else "Not Smiling"
            label_color = (0, 255, 0) if is_smiling else (0, 0, 255)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, label_color, 2)

            for (x, y) in landmarks:
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        frame = cv2.resize(frame, (video_label.winfo_width(), video_label.winfo_height()))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    gui_window.after(10, update_gui_frame)

def create_gui():
    global gui_window, video_label
    gui_window = tk.Tk()
    gui_window.title("Smile Monitor")
    gui_window.geometry("800x600")
    video_label = tk.Label(gui_window)
    video_label.pack(fill="both", expand=True)
    update_gui_frame()
    gui_window.protocol("WM_DELETE_WINDOW", hide_gui)
    gui_window.mainloop()

def show_gui(icon, item):
    if gui_window and gui_window.winfo_exists():
        gui_window.deiconify()
    else:
        threading.Thread(target=create_gui, daemon=True).start()

def hide_gui():
    if gui_window and gui_window.winfo_exists():
        gui_window.withdraw()

def on_exit(icon, item):
    global running
    running = False
    if gui_window and gui_window.winfo_exists():
        gui_window.destroy()
    icon.stop()

def run_tray():
    global icon_ref
    image = Image.open("smiling.png")  # Ensure you have a valid image file
    image = image.resize((64, 64), Image.Resampling.LANCZOS)
    menu = Menu(
        MenuItem("Show Window", show_gui),
        MenuItem("Hide Window", lambda icon, item: hide_gui()),
        MenuItem("Quit", on_exit)
    )
    icon_ref = Icon("SmileMonitor", image, "Smile Monitoring System", menu)
    threading.Thread(target=smile_monitor_loop, daemon=True).start()
    icon_ref.run()

if __name__ == "__main__":
    run_tray()