
#  Smart Gym Buddy (T27)

Smart Gym Buddy is an edge-computing based system designed to assist gym-goers in maintaining proper posture and tracking workout performance in real time. It combines **computer vision**, **audio feedback**, and **dashboard analytics** to support both **users** and **gym owners** in enhancing training safety and operational efficiency.

##  Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Demo](#demo)
- [Contributors](#contributors)

##  Introduction

Smart Gym Buddy leverages AI-driven posture analysis using MediaPipe and OpenCV to detect incorrect bench press form and guide users via real-time audio alerts. It also logs workout data and provides analytics for gym owners on equipment usage.

##  Features

### User Features
- Real-time posture feedback using MediaPipe
- Audio alerts for incorrect form
- Automatic rep and set counting
- Session summary after each workout

### Gym Owner Features
- Equipment usage tracking (daily, weekly, monthly)
- Dashboard displaying user activity and equipment analytics

##  System Architecture

- **Camera Input**: Captures user during bench press
- **Raspberry Pi**: Runs pose detection locally using MediaPipe
- **Flask Server**: Handles RFID authentication and logs session data to Firebase
- **Dashboard**: Visualizes equipment usage analytics

##  Technologies Used

- Raspberry Pi 3
- Python, OpenCV, MediaPipe
- Flask (for web server)
- Firebase (for session logging)
- Chart.js / Bootstrap (for dashboard)
- RFID Scanner (user authentication)



- User scans RFID card to begin session.
- System tracks posture and provides real-time corrections.
- Summary is logged and displayed post-session.



## Installation

This project consists of two components that must be run in separate virtual environments:

### 1. Webserver (Flask + Firebase)

1. Navigate to the `smart-gym/webserver` folder:
```bash
cd smart-gym/webserver
```

2. Set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python run.py
```

### 2. Posture Detection (Camera + Pose Estimation)

1. Navigate to the `posture-detection` folder:
```bash
cd posture-detection
```

2. Set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Open the `config.json` file and replace the placeholder IP with your actual **web server's IP address**.

4. Run the posture detection script:
```bash
python main.py
```


##  Demo

- [Video Demo](https://github.com/OWSJodie/INF2009-G27)
- [Live Demo Results](Refer to Poster PDF)

##  Contributors

- Ong Wei Song Jodie
- Hoe Jessaryn
- Tan Zining
- Lee Ying Zhen


##  Raspberry Pi 5 Compatibility Note

If you're using **Raspberry Pi 5**, note the following:

- Raspberry Pi 5 requires the use of the **`lgpio`** library instead of the deprecated RPi.GPIO.
- For RFID functionality, use the updated library forked by PiMyLifeUp:  
   https://github.com/pimylifeup/MFRC522-python  
  This version ensures compatibility with Pi 5 and provides more reliable GPIO access.

Make sure to follow the installation instructions in that repo when setting up your RFID scanner.


## Firebase Setup

To enable session logging and authentication, you must set up your own Firebase project:

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. In the project settings, add a new Web App to retrieve your Firebase config.
3. Replace the placeholder configuration in the codebase with your actual Firebase credentials.
4. Make sure Firebase Authentication and Firestore Database are enabled.

**Note**: Do not share your Firebase keys publicly. Keep them secure using environment variables or a secure config file.


## Posture Detection Configuration

Before running the posture detection module, make sure to:

1. Navigate to the `posture_detection` folder.
2. Open the `config.json` file and replace the placeholder IP with your actual **web server's IP address** to ensure proper data communication.
3. Then run the posture detection module:

```bash
python main.py
```
