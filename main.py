from monitor import (
    check_all_files,
    detect_new_files,
    detect_deleted_files
)

import json
import os
import time


# Folder to monitor
folder_path = "monitored_files"

# Baseline file
baseline_file = "baseline.json"


def create_baseline():
    """Create a baseline containing all files in the monitored folder."""

    baseline = {}

    for root, directories, filenames in os.walk(folder_path):

        for filename in filenames:

            file_path = os.path.join(root, filename)

            # Convert Windows path to consistent format
            file_path = file_path.replace("\\", "/")

            # Calculate SHA-256 hash
            from hash_utils import calculate_hash

            file_hash = calculate_hash(file_path)

            baseline[file_path] = file_hash

    with open(baseline_file, "w") as file:
        json.dump(baseline, file, indent=4)

    print("✅ Baseline created successfully!")
    print("Files included:", len(baseline))


# Create baseline if missing or empty
if not os.path.exists(baseline_file) or os.path.getsize(baseline_file) == 0:

    create_baseline()

else:

    # Load baseline to count monitored files
    with open(baseline_file, "r") as file:
        baseline = json.load(file)

    print()
    print("=" * 50)
    print("       FILE INTEGRITY MONITOR")
    print("=" * 50)
    print()
    print("📁 Monitoring Folder :", folder_path)
    print("📄 Baseline Files    :", len(baseline))
    print("⏱️ Check Interval    : 5 seconds")
    print()
    print("🟢 Status: MONITORING...")
    print()
    print("Press Ctrl+C to stop.")
    print("=" * 50)

    try:

        while True:

            # Check modifications
            print("\n🔍 Checking file integrity...")
            check_all_files()

            # Check new files
            print("🔍 Checking for new files...")
            detect_new_files(folder_path)

            # Check deleted files
            print("🔍 Checking for deleted files...")
            detect_deleted_files(folder_path)

            # Wait
            print("⏳ Waiting 5 seconds...")
            time.sleep(5)

    except BaseException as error:

        print("\n⚠️ PROGRAM STOPPED")
        print("Error type:", type(error).__name__)
        print("Error:", error)