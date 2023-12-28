# GUI-application-for-waste-management

Garbage Weight Tracking System

Overview

This Python script provides a simple graphical user interface (GUI) for tracking and recording weights of different types of waste. The application utilizes the Tkinter library for the GUI, threading for concurrent serial port communication, and the PySerial library for communication with external devices.

Features

Data Input: Enter weights for different types of waste manually or through serial port communication.
Real-time Updates: Automatically calculates cumulative weights and net weight as you input data.
Export to Text: Save the recorded data to a text file for future reference.
Popup Confirmation: Review and confirm the entered data before finalizing the record.
Customizable: Easily configure COM ports and waste types through external text files.
Dependencies
Python 3.x
Tkinter
PySerial

Usage

Run the Script: Execute the script in a Python environment.

GUI Interface:

Enter weights for different waste types.
Real-time updates for cumulative weights and net weight.

Popup Confirmation:

Press the designated key on the keypad to review and confirm the entered data.
Cancel or reset the data if needed.

Export Data:

Click the "Export" button to save the recorded data to a text file.

Configuration

COM Ports: Configure COM ports for serial communication in the com_ports.txt file.
Waste Types: Define waste types in the Type_of_waste.txt file.

External Files

com_ports.txt: Specifies COM ports for serial communication. (you need to fill these by manually)
Type_of_waste.txt: Lists different types of waste. (you need to fill these by manually)

Note

Ensure that the required COM ports are available and properly configured.
The script includes threading for concurrent serial port communication to ensure responsiveness.

