
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

##  Installation

1. Clone the repository:
```bash
git clone https://github.com/OWSJodie/INF2009-G27.git
cd INF2009-G27
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run posture detection:
After you navgiate to the posture detection folder 
```bash
python3 main.py
```

4. Start the Flask server:

After you navgiate to the smart-gym folder 
```bash
python run.py
```

##  Usage

- User scans RFID card to begin session.
- System tracks posture and provides real-time corrections.
- Summary is logged and displayed post-session.

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
