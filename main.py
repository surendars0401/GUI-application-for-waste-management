import tkinter as tk
from tkinter import messagebox
import os
import threading
import serial


def create_label(root, text, row, column, padx=10, pady=10, sticky='w', font_size=18):
    tk.Label(root, text=text, font=("Helvetica", font_size)).grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)


def create_entry(root, row, column, variable=None, state='normal', padx=9, pady=18, columnspan=1, font_size=20, height=8, width=None):
    entry = tk.Entry(root, textvariable=variable, state=state, font=("Helvetica", font_size), width=width)
    entry.grid(row=row, column=column, padx=padx, pady=pady, sticky='ew', columnspan=columnspan)
    return entry


def create_button(root, text, command, row, column, columnspan=1, padx=10, pady=20, font_size=16):
    tk.Button(root, text=text, command=command, font=("Helvetica", font_size)).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady)


def setup_ui(root):
    labels = ["S.no", "Type of Waste", "Current Weight", "Cum. Weight"]
    for i, label in enumerate(labels):
        create_label(root, label, 0, i, font_size=16)

    for i in range(1, 10):
        create_label(root, f"{i}.", i, 0, sticky='e', font_size=14)
        waste_type_entry_widgets.append(create_entry(root, i, 1, font_size=14))
        weight_entry = create_entry(root, i, 2, font_size=14, width=10)
        weight_entry.bind('<KeyRelease>', auto_update_weights)
        weight_entry_widgets.append(weight_entry)


    create_label(root, "Incoming Weight", 12, 1, sticky='ew', font_size=18)
    entry_widget = create_entry(root, 11, 1, variable=serial_data_var, state='readonly', columnspan=1, font_size=19)



    create_entry(root, 2, 3, cumulative_weights_vars[0], state='readonly', font_size=18)
    create_entry(root, 5, 3, cumulative_weights_vars[1], state='readonly', font_size=18)
    create_entry(root, 8, 3, cumulative_weights_vars[2], state='readonly', font_size=18)

    create_label(root, "Net Weight", 12, 3, sticky='ew', font_size=18)
    create_entry(root, 11, 3, net_weight_var, state='readonly', font_size=20)






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
    popup.geometry("600x72")


    label = tk.Label(popup, text=message, font=("Helvetica", 12))
    label.pack(padx=20, pady=20)

    # Center the popup window
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    popup_x = root_x + root_width // 2 - popup.winfo_reqwidth() // 2
    popup_y = root_y + root_height // 2 - popup.winfo_reqheight() // 2
    popup.geometry(f"+{popup_x}+{popup_y}")


    popup.after(duration, popup.destroy)

def export_to_text():
    folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'garbage_project')
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, 'weights_data.txt')

    try:
        with open(filename, "w", encoding='utf-8') as file:
            file.write("{:<20} {:<20} \n".format("Type of Waste", "Current Weight"))
            for i in range(9):
                file.write("{:<20} {:<20} \n".format(waste_type_entry_widgets[i].get(), weight_entry_widgets[i].get()))
            file.write("{:<20} {:<20}\n".format("Net Weight", net_weight_var.get()))

        # Show custom success message popup
        show_temporary_popup(f"Data exported to {filename}", 2000)

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
    com_port = com_ports.get('read_from_serial_port', 'COM9')

    with serial.Serial(com_port, baud_rate, timeout=4) as ser:
        print(f"Reading data from {com_port} at {baud_rate} baud...")
        while True:
            data = ser.readline().decode('utf-8').strip()
            serial_data_var.set(data)

def read_from_keypad(baud_rate=9600):
    global popup_window
    com_ports = get_com_ports()
    com_port = com_ports.get('read_from_keypad', 'COM6')

    with serial.Serial(com_port, baud_rate, timeout=4) as ser:
        print(f"Reading keypad input from {com_port} at {baud_rate} baud...")
        while True:
            key_input = ser.readline().decode('utf-8').strip()
            if key_input.isdigit():
                key_number = int(key_input)
                if popup_window:
                    if key_number == 10:
                        reset_and_close_popup()
                    elif key_number == 6:
                        cancel_popup()
                    elif key_number == 9:
                        export_to_text()
                else:
                    if 1 <= key_number <= 9:
                        current_weight = serial_data_var.get()
                        update_current_weight(key_number, current_weight)
                    elif key_number == 10:
                        show_popup()

def reset_all_values():

    for entry in weight_entry_widgets:
        entry.delete(0, tk.END)
        entry.insert(0, "")


    for var in cumulative_weights_vars:
        var.set("0 kg")
    net_weight_var.set("0 kg")


    serial_data_var.set("")


def update_current_weight(key_number, weight):
    if 0 < key_number <= len(weight_entry_widgets):
        weight_entry = weight_entry_widgets[key_number - 1]
        print(f"Before updating widget {key_number - 1}: {weight_entry.get()}")  
        weight_entry.delete(0, tk.END)  
        weight_entry.insert(0, weight)  
        print(f"After updating widget {key_number - 1}: {weight_entry.get()}")  


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
    if popup_window is not None:
        return

    popup_window = tk.Toplevel(root)
    popup_window.title("Review and Confirm")
    popup_window.geometry("580x550")


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


    for i, (waste_entry, weight_entry) in enumerate(zip(waste_type_entry_widgets, weight_entry_widgets)):
        if weight_entry.get():
            tk.Label(scrollable_frame, text=f"{i+1}. {waste_entry.get()}", font=("Helvetica", 20)).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            tk.Label(scrollable_frame, text=f"{weight_entry.get()}", font=("Helvetica", 20)).grid(row=i, column=1, sticky="w", padx=10, pady=5)


    tk.Label(scrollable_frame, text="Net Weight:", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets), column=0, sticky="w", padx=10, pady=10)
    tk.Label(scrollable_frame, text=f"{net_weight_var.get()}", font=("Helvetica", 18, "bold")).grid(row=len(waste_type_entry_widgets), column=1, sticky="w", padx=10, pady=10)

    frame.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    buttons_frame = tk.Frame(popup_window)
    tk.Button(buttons_frame, text="Cancel", command=cancel_popup).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(buttons_frame, text="Reset", command=reset_and_close_popup).pack(side=tk.RIGHT, padx=10, pady=10)
    buttons_frame.pack(fill="x")

    popup_window.transient(root)
    popup_window.grab_set()

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
        popup_window.grab_release()  
        popup_window.destroy()
        popup_window = None

def reset_and_close_popup():
    reset_all_values()
    cancel_popup()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Garbage Weight UI")
    root.geometry("1024x768")

    popup_window = None

    serial_data_var = tk.StringVar(value="")
    cumulative_weights_vars = [tk.StringVar(value="0 kg") for _ in range(3)]
    net_weight_var = tk.StringVar(value="0 kg")
    waste_type_entry_widgets = []
    weight_entry_widgets = []

    setup_ui(root)


    waste_types = read_waste_types_from_file()
    populate_waste_type_entries(waste_types)

    threading.Thread(target=read_from_serial_port, args=(9600,), daemon=True).start()
    threading.Thread(target=read_from_keypad, args=(9600,), daemon=True).start()
    type_of_waste_file_path, com_ports_file_path = get_file_path()
    root.mainloop()
