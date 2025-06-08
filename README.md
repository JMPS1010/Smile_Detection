# 😁 Smile Detection System

**Smile Detection System** is a desktop application that uses real-time facial landmark detection to monitor smiles.  
It logs instances when a user is **not smiling** and sends friendly Windows toast notifications as reminders.  
The system features a live camera feed with a GUI and system tray integration for background operation.

---

## ✅ Features

- Real-time smile detection using OpenCV and Dlib  
- Accurate facial landmark tracking (lip distance and head tilt)  
- Periodic logging of "Not Smiling" events to CSV  
- Toast notifications to remind users to smile  
- GUI window with live video feed using Tkinter  
- System tray functionality (show, hide, exit)

---

## 🛠️ Technologies Used

- Python  
- OpenCV  
- Dlib  
- Tkinter  
- Pillow (PIL)  
- pystray  
- win10toast

---

## 🚀 Running the Program

- Make sure you have all required libraries installed  
- (Optional) Create and activate a virtual environment  
- Run the Python script using:

  ```bash
  python smile_detection.py
  
P.S. This project was developed for educational purposes as part of the author's learning journey.
While it demonstrates the core functionality of smile detection and user interaction,
it is not a production-grade application and has room for a lot of improvement. Feel free to use it, explore, and improve it!
