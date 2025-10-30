import os
import subprocess
import shutil
import datetime

TASKS_DIR = ".gemini-tasks"
PROCESSED_DIR = os.path.join(TASKS_DIR, ".processed")
LOG_FILE = os.path.join(TASKS_DIR, "task_log.txt")

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def process_task_file(filepath):
    log_message(f"Processing task file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            commands = f.readlines()

        for i, command in enumerate(commands):
            command = command.strip()
            if not command or command.startswith("#"):
                continue # Skip empty lines and comments

            log_message(f"  Executing command [{i+1}]: {command}")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    text=True,
                    capture_output=True,
                    encoding="oem"  # Use OEM encoding for Windows console
                )
                if result.stdout:
                    log_message(f"    STDOUT:\n{result.stdout.strip()}")
                if result.stderr:
                    log_message(f"    STDERR:\n{result.stderr.strip()}")
            except subprocess.CalledProcessError as e:
                log_message(f"    ERROR: Command failed with exit code {e.returncode}")
                if e.stdout:
                    log_message(f"    STDOUT:\n{e.stdout.strip()}")
                if e.stderr:
                    log_message(f"    STDERR:\n{e.stderr.strip()}")
                # Decide whether to continue or stop on error
                # For now, we'll log and continue to the next command/file
            except FileNotFoundError:
                log_message(f"    ERROR: Command not found: {command.split()[0]}")
            except Exception as e:
                log_message(f"    ERROR: An unexpected error occurred during command execution: {e}")

        # Move the processed file
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        shutil.move(filepath, os.path.join(PROCESSED_DIR, os.path.basename(filepath)))
        log_message(f"Successfully processed and moved {filepath} to {PROCESSED_DIR}")

    except FileNotFoundError:
        log_message(f"ERROR: Task file not found: {filepath}")
    except Exception as e:
        log_message(f"ERROR: An unexpected error occurred while processing {filepath}: {e}")

def main():
    log_message("Starting task processing...")
    if not os.path.exists(TASKS_DIR):
        log_message(f"ERROR: Tasks directory '{TASKS_DIR}' does not exist.")
        return

    task_files = [f for f in os.listdir(TASKS_DIR) if os.path.isfile(os.path.join(TASKS_DIR, f)) and not f.startswith(".") and f != "task_log.txt"]
    
    if not task_files:
        log_message(f"No task files found in '{TASKS_DIR}'.")
        return

    for filename in task_files:
        filepath = os.path.join(TASKS_DIR, filename)
        process_task_file(filepath)
    
    log_message("Task processing finished.")

if __name__ == "__main__":
    main()
