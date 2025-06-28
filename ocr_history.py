# OCR Capture and Chat History

import time
import os
import tkinter as tk
from PIL import ImageGrab
import pytesseract
import pyperclip

ocr_history = []
last_add_time = None
previous_chats = []

HISTORY_FILE = 'ocr_text_history.txt'

# Function to add OCR text to history

def add_ocr_text(text):
    global last_add_time
    if text:
        # Always save the full OCR text (no new-words logic)
        if ocr_history:
            previous_chats.append(ocr_history[-1])
            ocr_history.clear()
        ocr_history.append(text)
        last_add_time = time.time()
        save_history_to_file()
        # Always reload history after saving to ensure in-memory and file are in sync
        load_history_from_file()

# Function to clear history if inactive for too long

def clear_history_if_inactive(timeout=4.0):
    global last_add_time
    now = time.time()
    if last_add_time is not None and (now - last_add_time) > timeout:
        ocr_history.clear()
        last_add_time = None

# Function to get full OCR history

def get_ocr_history():
    clear_history_if_inactive()
    return ocr_history

# Call this to save previous chat before new OCR capture

def add_previous_chat(text):
    if text:
        previous_chats.append(text)
        save_history_to_file()
        load_history_from_file()

# Get combined previous chat and current OCR history

def get_full_history():
    clear_history_if_inactive()
    return previous_chats + ocr_history

# Get combined previous chat and current OCR history as a single string

def get_full_history_string():
    save_history_to_file()  # Ensure latest in-memory is saved
    load_history_from_file()  # Ensure in-memory is up to date with file
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

def save_history_to_file():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        for line in previous_chats + ocr_history:
            f.write(line + '\n')

def load_history_from_file():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
        previous_chats.clear()
        ocr_history.clear()
        if lines:
            previous_chats.extend(lines[:-1])
            if lines:
                ocr_history.append(lines[-1])

# On import, load history
load_history_from_file()

def ocr_capture_and_save(region):
    img = ImageGrab.grab(bbox=region)
    img.save('debug_ocr_capture.png')  # Save the captured image for debugging
    print(f"[DEBUG] Saved captured image as debug_ocr_capture.png with region: {region}")
    text = pytesseract.image_to_string(img, lang='eng').strip()
    print(f"[DEBUG] Raw OCR result: {repr(text)}")
    add_ocr_text(text)
    pyperclip.copy(text)
    return text

def show_ocr_button(region):
    def on_click():
        text = ocr_capture_and_save(region)
        btn.config(text='Copied!')
        root.after(1000, lambda: btn.config(text='Copy OCR Text'))
    root = tk.Tk()
    root.title('Cute OCR Button')
    btn = tk.Button(root, text='Copy OCR Text', font=('Arial', 16), bg='#ffb6c1', fg='#333', command=on_click)
    btn.pack(padx=40, pady=40)
    root.mainloop()

def show_ocr_hotkey(region):
    import keyboard
    print('Press Ctrl+Alt+C to copy OCR text from the selected region.')
    def on_hotkey():
        text = ocr_capture_and_save(region)
        print(f'Copied OCR text: {text}')
    keyboard.add_hotkey('ctrl+alt+c', on_hotkey)
    print('Press ESC to exit.')
    keyboard.wait('esc')

if __name__ == "__main__":
    import sys
    # Let user select region if not provided
    if len(sys.argv) == 5:
        region = tuple(map(int, sys.argv[1:5]))
    else:
        print("Select the OCR region with your mouse...")
        from tkinter import Tk
        def select_region():
            root = Tk()
            root.attributes('-alpha', 0.3)
            root.attributes('-fullscreen', True)
            root.title("Drag to select OCR region, then close window")
            rect = None
            start_x = start_y = end_x = end_y = 0
            def on_mouse_down(event):
                nonlocal start_x, start_y, rect
                start_x, start_y = event.x, event.y
                rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)
            def on_mouse_move(event):
                nonlocal rect
                if rect:
                    canvas.coords(rect, start_x, start_y, event.x, event.y)
            def on_mouse_up(event):
                nonlocal end_x, end_y
                end_x, end_y = event.x, event.y
                root.quit()
            canvas = tk.Canvas(root, cursor="cross")
            canvas.pack(fill=tk.BOTH, expand=True)
            canvas.bind("<ButtonPress-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_move)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)
            root.mainloop()
            root.destroy()
            return (min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y))
        region = select_region()
        print(f"Selected region: {region}")
    show_ocr_hotkey(region)
