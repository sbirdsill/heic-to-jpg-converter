import os
import subprocess
from tkinter import Tk, Label, Button, filedialog, messagebox, Listbox, Scrollbar, Frame, HORIZONTAL, VERTICAL, Canvas, Toplevel
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import pillow_heif


# Initialize global variables for selected files
selected_files = []

# Function to convert HEIC to JPG
def convert_heic_to_jpg(file_path, output_dir):
    try:
        heif_file = pillow_heif.read_heif(file_path)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.jpg")
        image.save(output_path, "JPEG")
        return output_path, None
    except Exception as e:
        return None, f"Error converting {file_path}: {e}"

# Function to handle file selection
def add_files():
    file_paths = filedialog.askopenfilenames(title="Select HEIC files", filetypes=[("HEIC files", "*.heic")])
    if file_paths:
        for file_path in file_paths:
            if file_path not in selected_files:
                selected_files.append(file_path)
                file_listbox.insert('end', file_path)

# Function to remove selected files
def remove_selected_files():
    selected_indices = file_listbox.curselection()
    for index in selected_indices[::-1]:  # Reverse order to avoid index shifting
        selected_files.pop(index)
        file_listbox.delete(index)

# Function to start the conversion process
def convert_files():
    if not selected_files:
        messagebox.showwarning("No Files", "Please select at least one HEIC file to convert.")
        return
    
    output_dir = filedialog.askdirectory(title="Select Output Folder")
    if not output_dir:
        messagebox.showwarning("No Output Folder", "Please select an output folder.")
        return

    progress['maximum'] = len(selected_files)
    converted_files = []
    failed_files = []

    for i, file_path in enumerate(selected_files):
        output_path, error = convert_heic_to_jpg(file_path, output_dir)
        if error:
            failed_files.append(error)
        else:
            converted_files.append(output_path)
        progress['value'] = i + 1
        root.update_idletasks()  # Update GUI

    # Show the summary of the conversion in a scrollable listbox
    show_conversion_results(converted_files, failed_files, output_dir)

# Function to display the conversion results in a new scrollable window
def show_conversion_results(converted_files, failed_files, output_dir):
    results_window = Toplevel(root)
    results_window.title("Conversion Results")
    results_window.geometry("600x400")

    Label(results_window, text="Conversion Results", font=("Arial", 16)).pack(pady=10)

    result_frame = Frame(results_window)
    result_frame.pack(pady=10, padx=10, expand=True, fill='both')

    # Scrollable listbox for converted files
    listbox = Listbox(result_frame, width=80, height=15)
    listbox.pack(side='left', fill='both', expand=True)

    scrollbar = Scrollbar(result_frame)
    scrollbar.pack(side='right', fill='y')

    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    # Populate the listbox with converted files and failed files
    for file in converted_files:
        listbox.insert('end', f"Converted: {file}")

    if failed_files:
        listbox.insert('end', "\nFailed to convert:")
        for error in failed_files:
            listbox.insert('end', error)

    # Button to open the output folder
    Button(results_window, text="Open Output Folder", command=lambda: open_output_folder(output_dir), width=20).pack(pady=10)

# Function to open the output folder
def open_output_folder(folder_path):
    if os.name == 'nt':  # Windows
        os.startfile(folder_path)
    elif os.name == 'posix':  # macOS and Linux
        subprocess.Popen(['open', folder_path])

# Function to update the preview when a file is selected
def update_preview(event):
    selected_indices = file_listbox.curselection()
    if selected_indices:
        file_path = selected_files[selected_indices[0]]
        show_image_preview(file_path)

# Function to display the HEIC image preview
def show_image_preview(file_path):
    try:
        heif_file = pillow_heif.read_heif(file_path)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
        image.thumbnail((250, 250))
        img = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor='nw', image=img)
        canvas.image = img
    except Exception as e:
        messagebox.showerror("Preview Error", f"Error loading image preview: {e}")

# Function to display the "About" window
def show_about():
    about_window = Toplevel(root)
    about_window.title("About HEIC to JPG Converter")
    about_window.geometry("400x200")
    Label(about_window, text="HEIC to JPG Converter", font=("Arial", 16)).pack(pady=10)
    Label(about_window, text="Version 1.0").pack(pady=5)
    Label(about_window, text="This application allows you to convert HEIC files to JPG format.").pack(pady=5)
    Label(about_window, text="You can select multiple files, preview them, and convert them all at once.").pack(pady=5)
    Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

# Function to exit the application
def exit_app():
    root.destroy()

# Initialize GUI
root = Tk()
root.title("HEIC to JPG Converter")
root.geometry("800x650")

# Main Title
Label(root, text="HEIC to JPG Converter", font=("Arial", 20)).pack(pady=10)

# Frame for file list and preview
frame = Frame(root)
frame.pack(pady=10, padx=10, expand=True, fill='both')

# Listbox description
Label(frame, text="Selected HEIC Files:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Scrollable listbox for selected files with horizontal and vertical scrollbars
file_listbox = Listbox(frame, width=50, height=15, selectmode='extended')
file_listbox.grid(row=1, column=0, padx=10)

# Vertical scrollbar
v_scrollbar = Scrollbar(frame, orient=VERTICAL)
v_scrollbar.grid(row=1, column=1, sticky='ns')
file_listbox.config(yscrollcommand=v_scrollbar.set)
v_scrollbar.config(command=file_listbox.yview)

# Horizontal scrollbar
h_scrollbar = Scrollbar(frame, orient=HORIZONTAL)
h_scrollbar.grid(row=2, column=0, sticky='ew')
file_listbox.config(xscrollcommand=h_scrollbar.set)
h_scrollbar.config(command=file_listbox.xview)

file_listbox.bind('<<ListboxSelect>>', update_preview)

# Canvas for HEIC image preview
Label(frame, text="Preview:", font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=5, sticky='w')
canvas = Canvas(frame, width=250, height=250, bg='lightgray')
canvas.grid(row=1, column=2, padx=10)

# Buttons frame
button_frame = Frame(root)
button_frame.pack(pady=10)

# Buttons to add/remove files
Button(button_frame, text="Add HEIC Files", command=add_files, width=20).grid(row=0, column=0, padx=10, pady=5)
Button(button_frame, text="Remove Selected", command=remove_selected_files, width=20).grid(row=0, column=1, padx=10, pady=5)

# Convert button description
Label(root, text="Click 'Convert' to start the conversion process:", font=("Arial", 12)).pack(pady=5)

# Progress bar for the conversion process
progress = Progressbar(root, orient=HORIZONTAL, length=500, mode='determinate')
progress.pack(pady=10)

# Convert and Exit buttons
Button(root, text="Convert", command=convert_files, width=20).pack(pady=5)
Button(root, text="Exit", command=exit_app, width=20).pack(pady=5)

# About button at the bottom
Button(root, text="About", command=show_about, width=20).pack(pady=5)

# Start the GUI loop
root.mainloop()
