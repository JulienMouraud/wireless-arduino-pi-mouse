# 🖱️ Wireless Accelerometer Mouse (Arduino + Raspberry Pi)

This project implements a wireless computer mouse controlled by tilting a hardware module. The system bridges physical sensors with network communication to control a computer cursor in real-time.

## 🏗️ Architecture

The system is distributed across three distinct hardware components:

1. **Arduino UNO (Data Acquisition):** Reads a Grove BMA400 3-axis accelerometer via I2C to determine tilt, and a potentiometer on an analog pin to simulate the scroll wheel. It sends this raw data over a USB Serial connection at 115200 bauds.
2. **Raspberry Pi (Gateway & Server):** Connected to the Arduino via USB, it reads the serial data. It also reads two physical push buttons (Left and Right click) connected to GPIO 17 and GPIO 27. It runs a multithreaded Flask web server to expose all sensor and button data as a JSON API over the local network.
3. **Computer (Client):** Runs a Python script that continuously polls the Raspberry Pi's API. It processes the data (filtering, deadzone application) and translates it into actual mouse movements, scrolling, and clicks using the `pyautogui` library.

## 🛠️ Hardware Requirements

*   Arduino UNO
*   Grove BMA400 Accelerometer ($\pm16~g$)
*   Potentiometer
*   Raspberry Pi
*   2x Push Buttons

## 🚀 Features & Technical Solutions

*   **Proportional Control:** The cursor speed is proportional to the tilt angle.
*   **Signal Processing:** Implements an exponential smoothing filter (20% new reading, 80% previous value) to reduce accelerometer noise and prevent cursor jitter.
*   **Deadzone Management:** A threshold ignores minor tilts to prevent cursor drift when the device is held flat.
*   **Multithreading:** The Raspberry Pi handles Serial reading and the Flask server in separate threads to eliminate lag and cursor stuttering.
*   **Fail-Safe:** Built-in `pyautogui.FAILSAFE` halts the program if the cursor becomes uncontrollable and hits the screen corners.
*   **Web Dashboard:** The Raspberry Pi serves a dark-themed monitoring page to visualize real-time X/Y axes, potentiometer values, and button states.

## 📦 Installation & Usage

### 1. Arduino
*   Flash the `souris_arduino.ino` sketch to your Arduino UNO. The code uses the standard `Wire.h` library to communicate with the BMA400 directly via registers.

### 2. Raspberry Pi
*   Connect the Arduino via USB and the two buttons to GPIO 17 and 27.
*   Install dependencies: `pip install flask pyserial gpiozero`
*   Run the server: `python serveur_pi.py` 

### 3. Computer
*   Update the `URL_RASPBERRY` variable in `client_pc.py` with your Pi's local IP address.
*   Install dependencies: `pip install requests pyautogui`
*   Run the client: `python client_pc.py`

## 👥 Authors
Project realized by Julien MOURAUD.
