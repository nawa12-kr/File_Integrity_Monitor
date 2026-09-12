from datetime import datetime


def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("fim.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")