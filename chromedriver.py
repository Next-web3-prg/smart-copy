import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Please speak...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return None

def send_to_chatgpt_web(text, chatgpt_url="https://chat.openai.com"):
    # Start Chrome with chromedriver
    driver = webdriver.Chrome()
    driver.get(chatgpt_url)
    print("Please log in to ChatGPT if not already logged in.")
    # Wait for user to log in manually if needed
    input("Press Enter after you are logged in and see the chat input box...")
    # Find the input box (ChatGPT web UI)
    input_box = driver.find_element(By.TAG_NAME, "textarea")
    input_box.clear()
    input_box.send_keys(text)
    input_box.send_keys(Keys.ENTER)
    print("Text sent to ChatGPT web interface.")
    # Optionally, keep browser open for review
    time.sleep(5)
    # driver.quit()  # Uncomment to close browser automatically
    return driver

if __name__ == "__main__":
    user_text = recognize_speech_from_mic()
    if user_text:
        print("Sending to ChatGPT web interface...")
        send_to_chatgpt_web(user_text)