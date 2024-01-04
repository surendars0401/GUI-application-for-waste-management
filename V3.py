
//CAMERA AND RFID INTEGRATED

import tkinter as tk
from tkinter import messagebox
import os
import threading
import serial
import cv2
from PIL import Image, ImageTk

# Global variable for RFID data


def parse_rfid_data(raw_data):
    hex_data = [f"{byte:02X}" for byte in raw_data]
    hex_str = ''.join(hex_data)
    return hex_str

def run_rfid_reader(device_path='COM1', baud_rate=9600):
    global rfid_data_var
    encountered_tags = set()
    last_tag_name = None
    try:
        ser = serial.Serial(device_path, baud_rate)
        while True:
            raw_data = ser.read(18)
            tag_name_data = raw_data[4:16]
            current_tag_name = parse_rfid_data(tag_name_data)
            if current_tag_name != last_tag_name:
                if current_tag_name not in encountered_tags:
                    encountered_tags.add(current_tag_name)
                    rfid_data_var.set(current_tag_name)  # Update the RFID StringVar
                last_tag_name = current_tag_name
    except serial.SerialException as e:
        print(f"An error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

# Function to create a label with a larger font        create_label
def create_label(root, text, row, column, padx=10, pady=10, sticky='w', font_size=16, columnspan=1):
    tk.Label(root, text=text, font=("Helvetica", font_size)).grid(row=row, column=column, padx=padx, pady=pady,
                                                                  sticky=sticky, columnspan=columnspan)


# Function to create an entry with a larger font
def create_entry(root, row, column, variable=None, state='normal', padx=10, pady=10, columnspan=1, font_size=16,
                 width=15):
    entry = tk.Entry(root, textvariable=variable, state=state, font=("Helvetica", font_size), width=width)
    entry.grid(row=row, column=column, padx=padx, pady=pady, sticky='w', columnspan=columnspan)
    return entry


# Function to create a button with a larger font
def create_button(root, text, command, row, column, columnspan=1, padx=10, pady=10, font_size=14):
    tk.Button(root, text=text, command=command, font=("Helvetica", font_size)).grid(row=row, column=column,
                                                                                    columnspan=columnspan, padx=padx,
                                                                                    pady=pady)


# Function to set up the UI with larger sizes
def setup_ui(root):
    labels = ["S.no", "Type of Waste", "Current Weight", "Cum. W"]
    Vehicle_number = tk.StringVar(value=" TN32 AK1314")

    for i, label in enumerate(labels):
        create_label(root, label, 0, i, font_size=16, padx=20, pady=10)

    for i in range(1, 10):
        create_label(root, f"{i}.", i, 0, sticky='e', font_size=17, padx=20, pady=5)
        waste_type_entry_widgets.append(create_entry(root, i, 1, font_size=17))
        weight_entry = create_entry(root, i, 2, font_size=17, width=10)
        weight_entry.bind('<KeyRelease>', auto_update_weights)
        weight_entry_widgets.append(weight_entry)

    create_label(root, "Incoming Weight", 12, 1, sticky='ew', font_size=18, pady=10)
    entry_widget = create_entry(root, 11, 1, variable=serial_data_var, state='readonly', columnspan=1, font_size=19,
                                pady=5)

    create_label(root, "Vehicle No", 0, 5, sticky='ew', font_size=16, pady=10)
    entry_widget = create_entry(root, 1, 5, variable=Vehicle_number, columnspan=2, font_size=16, padx=1, pady=5)



    # Other UI elements from your original code
    create_entry(root, 2, 3, cumulative_weights_vars[0], state='readonly', font_size=18, width=10, padx=5, pady=5)
    create_entry(root, 5, 3, cumulative_weights_vars[1], state='readonly', font_size=18, width=10, padx=5, pady=5)
    create_entry(root, 8, 3, cumulative_weights_vars[2], state='readonly', font_size=18, width=10, padx=5, pady=5)

    webcam_label = tk.Label(root)
    create_label(root, "Cam Out", 11, 5, sticky='ew', font_size=18, pady=10)
    webcam_label.grid(row=12, column=5, columnspan=2, padx=10, pady=10)  # Adjust grid parameters as needed

    # Initialize webcam capture
    global vid
    vid = cv2.VideoCapture(1)

    # Start the webcam feed update
    update_webcam_feed(webcam_label)

    # Set column weights and row weights for proper alignment and spacing
    for i in range(13):
        root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(i, weight=1)


# Function to update the webcam feed
def update_webcam_feed(label):
    ret, frame = vid.read()
    if ret:
        # Resize the frame to the desired size
        frame = cv2.resize(frame, (168, 170))

        # Convert the image from BGR (OpenCV format) to RGB (Tkinter format)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the image to PIL format and then to ImageTk format
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))

        # Keep a reference, if you don't keep the ref image will not be displayed
        label.imgtk = photo

        # Configure the label to display the new image
        label.config(image=photo)

    # Repeat this function after 10ms (for a real-time update without freezing the GUI)
    label.after(10, update_webcam_feed, label)

    create_label(root, "Net Weight", 12, 3, sticky='ew', font_size=18, pady=10)
    create_entry(root, 11, 3, net_weight_var, state='readonly', font_size=20, pady=5)

    # Set column weights and row weights for proper alignment and spacing
    for i in range(13):
        root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(i, weight=1)






def auto_update_weights(event):
    cumulative_weights = [0, 0, 0]
    for i, entry in enumerate(weight_entry_widgets):
        try:
            weight = float(entry.get())
            cumulative_weights[i // 3] += weight
        except ValueError:
            continue

    for i, weight in enumerate(cumulative_weights):
        cumulative_weights_vars[i].set(f"{weight} kg")

    net_weight_var.set(f"{sum(cumulative_weights)} kg")

def show_temporary_popup(message, duration=2000):
    popup = tk.Toplevel(root)
    popup.title("Message")
    popup.geometry("200x80")  # Adjust the size as needed

    # Label for displaying the message
    label = tk.Label(popup, text=message, font=("Helvetica", 22))
    label.pack(padx=20, pady=20)  # Increase padding for better alignment

    # Center the popup window
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    popup_x = root_x + root_width // 2 - popup.winfo_reqwidth() // 2
    popup_y = root_y + root_height // 2 - popup.winfo_reqheight() // 2
    popup.geometry(f"+{popup_x}+{popup_y}")

    # Schedule the popup to destroy itself after the duration
    popup.after(duration, popup.destroy)

def export_to_text():
    folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'garbage_project')
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, 'weights_data.txt')

    try:
        with open(filename, "a", encoding='utf-8') as file:
            file.write("{:<20} {:<20} \n".format("Type of Waste", "Current Weight"))
            for i in range(9):
                file.write("{:<20} {:<20} \n".format(
                    waste_type_entry_widgets[i].get(), weight_entry_widgets[i].get()
                ))
            file.write("{:<20} {:<20} \n".format("Net Weight", net_weight_var.get()))
            file.write("{:<20} {:<20} \n".format("RFID", rfid_data_var.get()))

        # Show custom success message popup
        show_temporary_popup(f"\U00002713 நன்றி ", 2000)

    except IOError as e:
        messagebox.showerror("Error", f"An error occurred while exporting: {e}")



def get_file_path():
    folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'garbage_project')
    os.makedirs(folder_path, exist_ok=True)

    type_of_waste_file_path = os.path.join(folder_path, 'Type_of_waste.txt')
    com_ports_file_path = os.path.join(folder_path, 'com_ports.txt')

    if not os.path.exists(type_of_waste_file_path):
        with open(type_of_waste_file_path, 'w') as file:
            file.write('')

    if not os.path.exists(com_ports_file_path):
        with open(com_ports_file_path, 'w') as file:
            # Write specific content to the "com_ports.txt" file
            file.writelines(["read_from_serial_port - \n", "read_from_keypad      - \n"])

    return type_of_waste_file_path, com_ports_file_path


def read_waste_types_from_file():
    type_of_waste_file_path, _ = get_file_path()
    try:
        with open(type_of_waste_file_path, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"File '{type_of_waste_file_path}' not found. Please create the file with waste types.")
        return []


def populate_waste_type_entries(waste_types):
    for i, waste_type in enumerate(waste_types):
        if i < len(waste_type_entry_widgets):
            waste_type_entry_widgets[i].delete(0, tk.END)
            waste_type_entry_widgets[i].insert(0, waste_type)

def read_from_serial_port(baud_rate=9600):
    com_ports = get_com_ports()
    com_port = com_ports.get('read_from_serial_port', 'COM9')  # Default to 'COM9' if not found

    with serial.Serial(com_port, baud_rate, timeout=4) as ser:
        print(f"Reading data from {com_port} at {baud_rate} baud...")
        while True:
            data = ser.readline().decode('utf-8').strip()
            serial_data_var.set(data)

def read_from_keypad(baud_rate=9600):
    global popup_window
    com_ports = get_com_ports()
    com_port = com_ports.get('read_from_keypad', 'COM6')  # Default to 'COM6' if not found

    with serial.Serial(com_port, baud_rate, timeout=4) as ser:
        print(f"Reading keypad input from {com_port} at {baud_rate} baud...")
        while True:
            key_input = ser.readline().decode('utf-8').strip()
            if key_input.isdigit():
                key_number = int(key_input)
                if popup_window:  # If the popup is active
                    if key_number == 10:
                        reset_and_close_popup()
                    elif key_number == 6:
                        cancel_popup()
                    elif key_number == 9:
                        export_to_text()  # Call the export function
                        reset_and_close_popup()
                else:
                    if 1 <= key_number <= 9:
                        current_weight = serial_data_var.get()
                        update_current_weight(key_number, current_weight)
                    elif key_number == 10:
                        show_popup()

def reset_all_values():
    # Reset the Current Weight and Cumulative Weight entries
    for entry in weight_entry_widgets:
        entry.delete(0, tk.END)
        entry.insert(0, "")

    # Reset the Cumulative Weights and Net Weight variables
    for var in cumulative_weights_vars:
        var.set("0 kg")
    net_weight_var.set("0 kg")

    # Reset the RFID input field
    rfid_data_var.set("")  # Add this line to clear the RFID input field

    serial_data_var.set("")


def update_current_weight(key_number, weight):
    if 0 < key_number <= len(weight_entry_widgets):
        weight_entry = weight_entry_widgets[key_number - 1]

        weight_entry.delete(0, tk.END)  # Clear the existing value
        weight_entry.insert(0, weight)  # Insert the new weight



        auto_update_weights(None)
def get_com_ports():
    _, com_ports_file_path = get_file_path()
    com_ports = {}
    try:
        with open(com_ports_file_path, 'r') as file:
            for line in file:
                if '-' in line:
                    function_name, com_port = line.split('-')
                    com_ports[function_name.strip()] = com_port.strip()
    except FileNotFoundError:
        print(f"File '{com_ports_file_path}' not found. Please create the file with COM port settings.")
    return com_ports

def show_popup():
    global popup_window
    if popup_window is not None:  # If popup is already open, don't create a new one
        return

    popup_window = tk.Toplevel(root)
    popup_window.title("Review and Confirm")
    popup_window.geometry("550x580")  # Adjust the size of the popup to accommodate the layout

    # Scrollable frame inside the popup
    frame = tk.Frame(popup_window)
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Displaying the entered values
    for i, (waste_entry, weight_entry) in enumerate(zip(waste_type_entry_widgets, weight_entry_widgets)):
        if weight_entry.get():
            tk.Label(scrollable_frame, text=f"{i+1}. {waste_entry.get()}", font=("Helvetica", 20)).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            tk.Label(scrollable_frame, text=f"{weight_entry.get()}", font=("Helvetica", 20)).grid(row=i, column=1, sticky="w", padx=10, pady=5)

    # Add net weight at the bottom
    tk.Label(scrollable_frame, text="Net Weight:", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets), column=0, sticky="w", padx=10, pady=10)
    tk.Label(scrollable_frame, text=f"{net_weight_var.get()}", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets), column=1, sticky="w", padx=10, pady=10)

    tk.Label(scrollable_frame, text="Rfid no:", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets)+1, column=0, sticky="w", padx=10, pady=10)
    tk.Label(scrollable_frame, text=f"{rfid_data_var.get()}", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets)+1, column=1, sticky="w", padx=10, pady=10)



    frame.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)


    # Buttons at the bottom of the popup
    buttons_frame = tk.Frame(popup_window)
    tk.Button(buttons_frame, text="Cancel", command=cancel_popup).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(buttons_frame, text="Reset", command=reset_and_close_popup).pack(side=tk.RIGHT, padx=10, pady=10)
    buttons_frame.pack(fill="x")

    popup_window.transient(root)  # Make the window modal
    popup_window.grab_set()  # Give focus to the popup

    # Center the popup window
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    popup_x = root_x + root_width // 2 - popup_window.winfo_reqwidth() // 2
    popup_y = root_y + root_height // 2 - popup_window.winfo_reqheight() // 2
    popup_window.geometry(f"+{popup_x}+{popup_y}")

    popup_window.protocol("WM_DELETE_WINDOW", cancel_popup)

def cancel_popup():
    global popup_window
    if popup_window:
        popup_window.grab_release()  # Release the focus
        popup_window.destroy()
        popup_window = None

def reset_and_close_popup():
    reset_all_values()
    cancel_popup()

# Function to capture and save an image
def capture_and_save_image(row_index):
    ret, frame = vid.read()
    if ret:
        # Resize the frame to the desired size
        frame = cv2.resize(frame, (168, 170))

        # Save the image with a filename based on the row index in the specified folder
        folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'garbage_project')
        image_filename = os.path.join(folder_path, f"image_row_{row_index}.png")
        cv2.imwrite(image_filename, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        print(f"Image saved: {image_filename}")  # Add this line for debugging

        return image_filename
    else:
        print("Failed to capture image")  # Add this line for debugging
        return None



# Function to update the webcam feed and capture image when a key is pressed
def update_webcam_feed_and_capture(event):
    row_index = int(event.char)
    if 1 <= row_index <= 9:
        # Capture and save image
        image_filename = capture_and_save_image(row_index)

        # Update the RFID and weight values for the corresponding row
        current_rfid_value = rfid_data_var.get()
        current_weight_value = weight_entry_widgets[row_index - 1].get()

        # Display the captured image filename, RFID, and weight in the console
        print(f"Image: {image_filename}, RFID: {current_rfid_value}, Weight: {current_weight_value}")


# Main function
# Main function
if __name__ == "__main__":
    root = tk.Tk()
    root.title("RTS Garbage UI ")

    root.geometry("1024x705")
    root.configure(bg='light green')
    # Global variable for the popup reference
    popup_window = None
    rfid_data_var = tk.StringVar()
    serial_data_var = tk.StringVar(value="")
    cumulative_weights_vars = [tk.StringVar(value="0 kg") for _ in range(3)]
    net_weight_var = tk.StringVar(value="0 kg")
    waste_type_entry_widgets = []
    weight_entry_widgets = []

    # Set up the UI
    setup_ui(root)

    # Populate waste type entries
    waste_types = read_waste_types_from_file()
    populate_waste_type_entries(waste_types)

    threading.Thread(target=read_from_serial_port, args=(9600,), daemon=True).start()
    threading.Thread(target=read_from_keypad, args=(9600,), daemon=True).start()
    type_of_waste_file_path, com_ports_file_path = get_file_path()

    # Example row and column indices
    row_index = 3  # Replace with the actual row index
    column_index = 5  # Replace with the actual column index

    # RFID display region in the GUI
    tk.Label(root, text="RFID Tag", font=("Helvetica", 16)).grid(row=3, column=5, padx=10, pady=10)
    tk.Entry(root, textvariable=rfid_data_var, font=("Helvetica", 14), state='readonly').grid(row=4,
                                                                                              column=5,
                                                                                              padx=1, pady=1)

    for i in range(1, 10):
        root.bind(str(i), update_webcam_feed_and_capture)


    # Start the RFID reader thread
    threading.Thread(target=run_rfid_reader, args=('COM1', 9600), daemon=True).start()

    root.mainloop()
    vid.release()
