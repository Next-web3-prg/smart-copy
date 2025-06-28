import ocr_history

def get_ocr_history_string():
    return '\n'.join(ocr_history.get_ocr_history())

if __name__ == "__main__":
    print(get_ocr_history_string())
