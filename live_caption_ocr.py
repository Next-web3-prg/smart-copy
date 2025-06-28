import os
import pytesseract
from PIL import ImageGrab
import time
import pyperclip
import pyautogui
import pygetwindow as gw
import tkinter as tk
import ocr_history
import keyboard

# Suppress ChromeDriver and Chrome logs
os.environ['WDM_LOG_LEVEL'] = '0'

def select_region():
    root = tk.Tk()
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

def ocr_capture_and_copy():
    img = ImageGrab.grab(bbox=CAPTION_REGION)
    text = pytesseract.image_to_string(img, lang='eng').strip()
    # Remove empty lines
    cleaned_text = '\n'.join([line for line in text.splitlines() if line.strip()])
    if cleaned_text:
        ocr_history.add_ocr_text(cleaned_text)
        pyperclip.copy(cleaned_text)
        print(f"Copied OCR text: {cleaned_text}")
    else:
        print("No text detected in region.")

def show_ocr_button():
    def on_click():
        ocr_capture_and_copy()
        btn.config(text='Copied!')
        root.after(1000, lambda: btn.config(text='Copy OCR Text'))
    root = tk.Tk()
    root.title('Cute OCR Button')
    btn = tk.Button(root, text='Copy OCR Text', font=('Arial', 16), bg='#ffb6c1', fg='#333', command=on_click)
    btn.pack(padx=40, pady=40)
    root.mainloop()

# Use dynamic region selection
print("Select the OCR region with your mouse...")
CAPTION_REGION = select_region()
print(f"Selected region: {CAPTION_REGION}")

print("Starting Live Caption OCR and ChatGPT paste automation...")
print(f"Capturing region: {CAPTION_REGION}")

input("Focus the ChatGPT input box in your browser, then press Enter here to continue...")

# Get the title of the currently focused window
focused_window = gw.getActiveWindow()
if focused_window:
    focus_title = focused_window.title
    print(f"Will only paste if this window is focused: {focus_title}")
else:
    focus_title = None
    print("Warning: Could not get focused window title. Will always copy, never paste.")

last_text = ""
last_nonempty_time = time.time()

def on_hotkey():
    ocr_capture_and_copy()
    print('OCR region captured and copied!')

keyboard.add_hotkey('shift+alt+c', on_hotkey)
print('Press Shift+Alt+C to capture OCR region. Press ESC to exit.')
keyboard.wait('esc')

if __name__ == "__main__":
    print("Select the OCR region with your mouse...")
    CAPTION_REGION = select_region()
    print(f"Selected region: {CAPTION_REGION}")
    show_ocr_button()
