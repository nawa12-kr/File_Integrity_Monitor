from hash_utils import calculate_hash
from logger import log_event
import json
import os


ALERT_STATE_FILE = "alert_state.json"


def load_alert_state():
    """Load previously reported alerts from the state file."""

    if not os.path.exists(ALERT_STATE_FILE):
        return set()

    try:
        with open(ALERT_STATE_FILE, "r") as file:
            data = json.load(file)

        return set(data)

    except (json.JSONDecodeError, OSError):
        return set()


def save_alert_state(reported_alerts):
    """Save reported alerts to the state file."""

    with open(ALERT_STATE_FILE, "w") as file:
        json.dump(list(reported_alerts), file, indent=4)


# Load previous alert state
reported_alerts = load_alert_state()


def check_file(file_path):
    """Check whether a monitored file has been modified."""

    # Load baseline
    with open("baseline.json", "r") as file:
        baseline = json.load(file)

    # File deleted
    if not os.path.exists(file_path):
        return

    # Get original hash
    original_hash = baseline.get(file_path)

    # File not present in baseline
    if original_hash is None:
        return

    # Calculate current hash
    current_hash = calculate_hash(file_path)

    # Compare hashes
    if original_hash == current_hash:

        print("✅ File is safe. No changes detected.")

        # Clear old modification alert
        alert_key = f"modified:{file_path}"

        if alert_key in reported_alerts:
            reported_alerts.remove(alert_key)
            save_alert_state(reported_alerts)

    else:

        alert_key = f"modified:{file_path}"

        # Alert only once
        if alert_key not in reported_alerts:

            print("--------------------------------------------")
            print("🚨 ALERT: File has been modified!")
            print("File:", file_path)
            print("Original Hash:", original_hash)
            print("Current Hash:", current_hash)

            log_event(
                f"ALERT: File modified: {file_path}"
            )

            reported_alerts.add(alert_key)
            save_alert_state(reported_alerts)


def check_all_files():
    """Check every file stored in the baseline."""

    # Load baseline
    with open("baseline.json", "r") as file:
        baseline = json.load(file)

    # Check every baseline file
    for file_path in baseline:

        check_file(file_path)


def scan_folder(folder_path):
    """Scan all files inside the monitored folder."""

    files = {}

    for root, directories, filenames in os.walk(folder_path):

        for filename in filenames:

            file_path = os.path.join(root, filename)

            # Convert Windows path to consistent format
            file_path = file_path.replace("\\", "/")

            files[file_path] = calculate_hash(file_path)

    return files


def detect_new_files(folder_path):
    """Detect files that were not present in the baseline."""

    # Load baseline
    with open("baseline.json", "r") as file:
        baseline = json.load(file)

    # Scan current folder
    current_files = scan_folder(folder_path)

    # Check for new files
    for file_path in current_files:

        if file_path not in baseline:

            alert_key = f"new:{file_path}"

            # Alert only once
            if alert_key not in reported_alerts:

                print("--------------------------------------------")
                print("🚨 ALERT: New file detected!")
                print("File:", file_path)

                log_event(
                    f"ALERT: New file detected: {file_path}"
                )

                reported_alerts.add(alert_key)
                save_alert_state(reported_alerts)


def detect_deleted_files(folder_path):
    """Detect files from the baseline that have been deleted."""

    # Load baseline
    with open("baseline.json", "r") as file:
        baseline = json.load(file)

    # Scan current folder
    current_files = scan_folder(folder_path)

    # Check every baseline file
    for file_path in baseline:

        if file_path not in current_files:

            alert_key = f"deleted:{file_path}"

            # Alert only once
            if alert_key not in reported_alerts:

                print("--------------------------------------------")
                print("🚨 ALERT: File has been deleted!")
                print("File:", file_path)

                log_event(
                    f"ALERT: File deleted: {file_path}"
                )

                reported_alerts.add(alert_key)
                save_alert_state(reported_alerts)

        else:

            # File has been restored
            alert_key = f"deleted:{file_path}"

            # Clear only the old deleted alert
            if alert_key in reported_alerts:

                reported_alerts.remove(alert_key)
                save_alert_state(reported_alerts)