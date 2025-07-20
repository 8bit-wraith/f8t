
import subprocess
import time
import random
import re
import openai  # Or mock this
from datetime import datetime

SESSION = "my-session"
IDLE_THRESHOLD_RANGE = (10, 20)
CHECK_INTERVAL = 1

def list_panes():
    out = subprocess.check_output(
        ["tmux", "list-panes", "-t", SESSION, "-F", "#{pane_id}"]).decode()
    return out.strip().splitlines()

def get_pane_content(pane_id):
    return subprocess.check_output(
        ["tmux", "capture-pane", "-pt", pane_id, "-S", "-10"]).decode()

def is_idle(pane_id):
    text = get_pane_content(pane_id)
    last_line = text.strip().splitlines()[-1] if text.strip() else ""
    return bool(re.match(r".*[\$>#] ?$", last_line))

def get_summary(pane_id):
    content = get_pane_content(pane_id)
    return f"Pane {pane_id}:\n" + "\n".join(content.strip().splitlines()[-5:])

def query_openai(prompt):
    # Replace with real API call
    print(f"AI was asked:\n{prompt}")
    return "echo Hello from AI 🧠"

def send_to_pane(pane_id, cmd):
    subprocess.call(["tmux", "send-keys", "-t", pane_id, cmd, "Enter"])

def main():
    panes = list_panes()
    idle_start = {pid: None for pid in panes}

    while True:
        all_idle = True
        for pid in panes:
            if is_idle(pid):
                if idle_start[pid] is None:
                    idle_start[pid] = datetime.now()
            else:
                idle_start[pid] = None
                all_idle = False

        if all_idle and all((datetime.now() - idle_start[pid]).total_seconds() > random.randint(*IDLE_THRESHOLD_RANGE) for pid in panes):
            summaries = "\n\n".join(get_summary(pid) for pid in panes)
            command = query_openai("Summarize then give one command:\n" + summaries)

            main_pid = panes[0]
            print(f"Sending command to {main_pid}: {command}")
            send_to_pane(main_pid, command)

            # Reset idle times
            idle_start = {pid: None for pid in panes}

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
