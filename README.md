# Smart Gym Buddy (T27)

Smart Gym Buddy is an edge-computing based system designed to assist gym-goers in maintaining proper posture and tracking workout performance in real time. It combines **computer vision**, **audio feedback**, and **dashboard analytics** to support both **users** and **gym owners** in enhancing training safety and operational efficiency.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Posture Detection Configuration](#posture-detection-configuration)
- [Optimization Note](#optimization-note)
- [Demo](#demo)
- [Contributors](#contributors)
- [Firebase Setup](#firebase-setup)
- [Raspberry Pi 5 Compatibility Note](#raspberry-pi-5-compatibility-note)

## Introduction

Smart Gym Buddy leverages AI-driven posture analysis using MediaPipe and OpenCV to detect incorrect bench press form and guide users via real-time audio alerts. It also logs workout data and provides analytics for gym owners on equipment usage.

## Features

### User Features
- Real-time posture feedback using MediaPipe
- Audio alerts for incorrect form
- Automatic rep and set counting
- Session summary after each workout

### Gym Owner Features
- Equipment usage tracking (daily, weekly, monthly)
- Dashboard displaying user activity and equipment analytics

## System Architecture

- **Camera Input**: Captures user during bench press
- **Raspberry Pi**: Runs pose detection locally using MediaPipe
- **Flask Server**: Runs in a separate thread to handle RFID authentication and logs session data to Firebase
- **Dashboard**: Visualizes equipment usage analytics

**Threading**:
- Flask server, RFID scanner, and audio playback run in separate threads for responsiveness.
- Audio playback uses a thread lock to prevent multiple overlapping alerts when incorrect posture is detected.

## Technologies Used

- Raspberry Pi 3 / 5
- Python, OpenCV, MediaPipe, pygame (for audio playback with thread locking)
- Flask (for web server)
- Firebase (for session logging)
- Chart.js / Bootstrap (for dashboard)
- RFID Scanner (user authentication)

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

## Usage

Smart Gym Buddy uses Python's `threading` module to ensure real-time, non-blocking operation across components:

- **Flask Server** runs on a thread for handling RFID-based login and communication with Firebase.
- **Audio Alerts** are triggered on a separate thread and use a **thread lock** to avoid overlapping or repeated posture alerts.
- **RFID Scanner** operates independently in its own thread for smooth scanning and session handling.

## Posture Detection Configuration

### Configuration Options (`config.json`)

The posture detection module uses a configuration file (`config.json`) to fine-tune sensitivity and behavior. Below is a breakdown of each parameter:

```json
{
  "web_server_ip": "192.168.0.230",
  "thresholds": {
    "WRIST_TILT_THRESHOLD": 0.1,
    "SHOULDER_TILT_THRESHOLD": 0.10,
    "HEAD_TILT_ADJUSTMENT": 0.02,
    "TOP_THRESHOLD": 0.20,
    "BOTTOM_THRESHOLD": 0.30
  },
  "rolling_frames": 8,
  "stability_threshold": 5,
  "mode_stability_threshold": 5,
  "ready_frames": 3
}
```

### Threshold Notes

- `WRIST_TILT_THRESHOLD`: Determines how sensitive the system is to wrist misalignment. Smaller values make the system stricter.
- `TOP_THRESHOLD` / `BOTTOM_THRESHOLD`: Define the virtual Y-axis boundary for rep counting.
  - **Smaller values = higher vertical line**
  - These thresholds help detect whether the user has completed a full rep by checking if the wrist crosses these lines.

### Mode Detection

The posture detection system automatically classifies user posture into one of four modes:
- `lying` (e.g., bench press)
- `standing`
- `sitting`
- `unknown` (when pose data is insufficient or not detectable)

## Optimization Note

The posture detection module was optimized and tested primarily using the **bench press exercise** video:
[Bench Press Demo – YouTube](https://www.youtube.com/watch?v=EUjh50tLlBo)

This video was chosen to validate the system's accuracy under the `lying` mode. Modes such as `standing`, `sitting`, and `unknown` are supported and can be expanded in future versions for additional exercises or use cases.

## Contributors

- Ong Wei Song Jodie
- Hoe Jessaryn
- Tan Zining
- Lee Ying Zhen

## Firebase Setup

To enable session logging and authentication, you must set up your own Firebase project:

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. In the project settings, add a new Web App to retrieve your Firebase config.
3. Replace the placeholder configuration in the codebase with your actual Firebase credentials.
4. Make sure Firebase Authentication and Firestore Database are enabled.

**Note**: Do not share your Firebase keys publicly. Keep them secure using environment variables or a secure config file.

## Raspberry Pi 5 Compatibility Note

If you're using **Raspberry Pi 5**, note the following:

- Raspberry Pi 5 requires the use of the **`lgpio`** library instead of the deprecated RPi.GPIO.
- For RFID functionality, use the updated library forked by PiMyLifeUp:  
  https://github.com/pimylifeup/MFRC522-python  
  This version ensures compatibility with Pi 5 and provides more reliable GPIO access.

Make sure to follow the installation instructions in that repo when setting up your RFID scanner.

