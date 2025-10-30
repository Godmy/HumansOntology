import os
import shutil
import datetime

TASKS_DIR = ".gemini-tasks"
PROCESSED_DIR = os.path.join(TASKS_DIR, ".processed_md")
LOG_FILE = os.path.join(TASKS_DIR, "md_task_log.txt")

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry) # Also print to console for immediate feedback
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def process_md_file(filepath):
    log_message(f"Reading Markdown task file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        log_message(f"--- Content of {os.path.basename(filepath)} ---")
        print(content) # Print the actual Markdown content to stdout
        log_message(f"--- End of content for {os.path.basename(filepath)} ---")

        # Move the processed file
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        shutil.move(filepath, os.path.join(PROCESSED_DIR, os.path.basename(filepath)))
        log_message(f"Successfully processed and moved {filepath} to {PROCESSED_DIR}")

    except FileNotFoundError:
        log_message(f"ERROR: Markdown task file not found: {filepath}")
    except Exception as e:
        log_message(f"ERROR: An unexpected error occurred while processing {filepath}: {e}")

def main():
    log_message("Starting Markdown task processing...")
    if not os.path.exists(TASKS_DIR):
        log_message(f"ERROR: Tasks directory '{TASKS_DIR}' does not exist.")
        return

    md_files = [f for f in os.listdir(TASKS_DIR) if os.path.isfile(os.path.join(TASKS_DIR, f)) and f.lower().endswith(".md") and not f.startswith(".")]
    
    if not md_files:
        log_message(f"No Markdown task files found in '{TASKS_DIR}'.")
        return

    for filename in md_files:
        filepath = os.path.join(TASKS_DIR, filename)
        process_md_file(filepath)
    
    log_message("Markdown task processing finished.")

if __name__ == "__main__":
    main()
