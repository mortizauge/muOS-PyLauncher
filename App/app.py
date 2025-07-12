import graphic as gr
import input
import sys
import time
import os
import subprocess
import threading
import queue

selected_position = 0
current_window = "browser"
max_items_per_page = 11
skip_input_check = False
menu_pressed = False
show_inspect_button = False

base_path = "/mnt"
current_path = base_path
file_list = []

def start():
    load_browser_menu()

def update():
    global current_window, selected_position, skip_input_check, menu_pressed

    if skip_input_check:
        input.reset_input()
        skip_input_check = False
    else:
        input.check()

    if input.key("MENUF"):
        menu_pressed = True
        input.reset_input()
        return

    if menu_pressed and input.key("START"):
        gr.draw_end()
        sys.exit()

    if not input.key("START") and not input.key("MENUF"):
        menu_pressed = False

    if current_window == "browser":
        load_browser_menu()
    else:
        load_browser_menu()

def load_browser_menu():
    global selected_position, file_list, current_path, skip_input_check, show_inspect_button

    try:
        entries = os.listdir(current_path)
    except Exception as e:
        entries = []
        gr.draw_log(f"Error: {e}", fill=gr.colorBlue, outline=gr.colorBlueD1)
        gr.draw_paint()
        time.sleep(2)

    directories = [d for d in entries if os.path.isdir(os.path.join(current_path, d))]
    files = [f for f in entries if os.path.isfile(os.path.join(current_path, f))]
    files = [f for f in files if f.lower().endswith(".py")]

    file_list = sorted(directories) + sorted(files)

    if not file_list:
        file_list = ["<Empty>"]

    if input.key("DY"):
        if input.value == 1:
            if selected_position < len(file_list) - 1:
                selected_position += 1
            else:
                selected_position = 0
        elif input.value == -1:
            if selected_position > 0:
                selected_position -= 1
            else:
                selected_position = len(file_list) - 1

    if input.key("A"):
        selected_item = file_list[selected_position]
        full_path = os.path.join(current_path, selected_item)
        if selected_item == "<Empty>":
            pass
        elif os.path.isdir(full_path):
            current_path = full_path
            selected_position = 0
            skip_input_check = True
        elif os.path.isfile(full_path) and selected_item.lower().endswith(".py"):
            run_script(full_path)
            skip_input_check = True

    elif input.key("B"):
        # Do not go above root "/mnt"
        if current_path != base_path and current_path != "/mnt":
            current_path = os.path.dirname(current_path)
            selected_position = 0
            skip_input_check = True
        else:
            gr.draw_end()
            sys.exit(0)

    show_inspect_button = False
    if file_list[selected_position] != "<Empty>":
        selected_item_path = os.path.join(current_path, file_list[selected_position])
        if os.path.isfile(selected_item_path) and file_list[selected_position].lower().endswith(".py"):
            show_inspect_button = True
            if input.key("Y"):
                inspect_script(selected_item_path)
                skip_input_check = True

    elif input.key("L1"):
        selected_position = max(0, selected_position - max_items_per_page)
    elif input.key("R1"):
        selected_position = min(len(file_list) - 1, selected_position + max_items_per_page)
    elif input.key("L2"):
        selected_position = max(0, selected_position - 100)
    elif input.key("R2"):
        selected_position = min(len(file_list) - 1, selected_position + 100)

    gr.draw_clear()
    gr.draw_rectangle_r([10, 40, 630, 440], 15, fill=gr.colorGrayD2, outline=None)
    gr.draw_text((320, 20), f"Browser: {current_path}", anchor="mm")

    start_idx = int(selected_position / max_items_per_page) * max_items_per_page
    end_idx = start_idx + max_items_per_page
    for i, item in enumerate(file_list[start_idx:end_idx]):
        display_name = item
        if item != "<Empty>":
            full_item_path = os.path.join(current_path, item)
            if os.path.isdir(full_item_path):
                display_name += "/"
        gr.row_list(display_name, (20, 50 + (i * 35)), 600, i == (selected_position % max_items_per_page))

    # Determine button A label
    if file_list[selected_position] == "<Empty>":
        btn_a_text = "A"
    else:
        selected_item_path = os.path.join(current_path, file_list[selected_position])
        if os.path.isfile(selected_item_path) and file_list[selected_position].lower().endswith(".py"):
            btn_a_text = "Run"
        else:
            btn_a_text = "Open"

    # Determine button B label
    if current_path != base_path and current_path != "/mnt":
        btn_b_text = "Back"
    else:
        btn_b_text = "Exit"

    gr.button_circle((30, 460), "A", btn_a_text)
    gr.button_circle((133, 460), "B", btn_b_text)
    gr.button_circle((520, 460), "M", "+")
    gr.button_circle((568, 460), "ST", "Exit")

    if show_inspect_button:
        gr.button_circle((236, 460), "Y", "Inspect")

    gr.draw_paint()

def run_script(path):
    gr.draw_clear()
    gr.draw_text((320, 240), f"Running {os.path.basename(path)}...\n\nPlease wait...", anchor="mm")
    gr.draw_paint()

    output_queue = queue.Queue()

    def reader(pipe):
        try:
            with pipe:
                for line in iter(pipe.readline, ''):
                    output_queue.put(line)
        except Exception:
            pass

    process = subprocess.Popen(
        ["python3", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )

    thread = threading.Thread(target=reader, args=(process.stdout,))
    thread.daemon = True
    thread.start()

    output_lines = []
    all_output = []
    max_lines = 20

    while True:
        while not output_queue.empty():
            line = output_queue.get()
            all_output.append(line)
            output_lines.append(line.rstrip())
            if len(output_lines) > max_lines:
                output_lines.pop(0)

        gr.draw_clear()
        y = 20
        gr.draw_text((10, 0), f"Output of {os.path.basename(path)}:", font=15, color=gr.colorBlue)
        for line in output_lines:
            gr.draw_text((10, y), line)
            y += 20

        gr.draw_paint()

        if process.poll() is not None and output_queue.empty():
            break

        time.sleep(0.05)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "logs")

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    filename_no_ext = os.path.splitext(os.path.basename(path))[0]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"{filename_no_ext}_log_{timestamp}.log")

    try:
        with open(log_filename, "w", encoding="utf-8") as log_file:
            log_file.write(f"--- Output from {os.path.basename(path)} ---\n")
            log_file.writelines(all_output)
            log_file.write("\n--- End of output ---\n")
    except Exception as e:
        gr.draw_log(f"Error writing log: {e}", fill="red", outline="red")
        gr.draw_paint()
        time.sleep(2)

    gr.button_circle((290, 460), "B", "Return")
    gr.draw_paint()

    while True:
        input.check()
        if input.key("B"):
            break
        time.sleep(0.1)

def inspect_script(path):
    input.simulate_key_press("R1")
    # Hack to refresh screen immediately
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            gr.draw_paint()
    except Exception as e:
        gr.draw_log(f"Error: {e}", fill="red", outline="red")
        gr.draw_paint()
        time.sleep(2)
        return

    scroll_pos = 0
    max_lines = 20

    while True:
        input.check()

        if input.key("B"):
            break
        elif input.key("DY"):
            if input.value == 1 and scroll_pos < len(lines) - max_lines:
                scroll_pos += 1
            elif input.value == -1 and scroll_pos > 0:
                scroll_pos -= 1

        gr.draw_clear()
        gr.draw_text((10, 0), f"Inspecting: {os.path.basename(path)}", font=15, color=gr.colorBlue)

        y = 20
        for line in lines[scroll_pos:scroll_pos + max_lines]:
            gr.draw_text((10, y), line.rstrip())
            y += 20

        gr.button_circle((290, 460), "B", "Back")
        gr.draw_paint()

        time.sleep(0.05)
