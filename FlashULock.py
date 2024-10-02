import psutil
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import ctypes
import sys
from art import tprint
click_count = 0
tprint('FlashULock V1.0')
print('Build 15')
print('GitHub > https://github.com/ErkinKraft')
def get_drives():
    drives = []
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        drives.append(partition.device)
    return drives


def execute_diskpart(commands):
    process = subprocess.Popen(
        ['diskpart'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output, error = process.communicate(commands)
    return output, error


def check_write_permission(disk):
    test_file_path = os.path.join(disk, 'test_file.tmp')

    try:
        with open(test_file_path, 'w') as test_file:
            test_file.write('test')
        os.remove(test_file_path)
        return True
    except Exception:
        return False


def update_buttons(is_blocked):
    if is_blocked:
        block_button.config(state=tk.DISABLED)
        unblock_button.config(state=tk.NORMAL)
    else:
        block_button.config(state=tk.NORMAL)
        unblock_button.config(state=tk.DISABLED)


def on_drive_selected(event):
    disk = disk_combobox.get()
    if disk:
        if check_write_permission(disk):
            update_buttons(False)
        else:
            update_buttons(True)


def block_usb():
    disk = disk_combobox.get()
    if disk:
        commands = f"select volume {disk}\nattributes disk set readonly\n"
        output, error = execute_diskpart(commands)

        if error:
            messagebox.showerror("Error", f"Failed to lock the disk: {error}")
        else:
            messagebox.showinfo("Success", "The disk has been successfully locked!")
            update_buttons(True)


def unblock_usb():
    disk = disk_combobox.get()
    if disk:
        commands = f"select volume {disk}\nattributes disk clear readonly\n"
        output, error = execute_diskpart(commands)

        if error:
            messagebox.showerror("Error", f"The disk could not be unlocked: {error}")
        else:
            messagebox.showinfo("Success", "The disk has been successfully unlocked!")
            update_buttons(False)


def show_console():
    ctypes.windll.kernel32.AllocConsole()

    command = input("> ")
    handle_command(command)


def handle_command(command):
    global click_count
    drives = get_drives()

    if command == "v":
        print("Version: 1.0    b15")
        print('GitHub > https://github.com/ErkinKraft')

    elif command == "unlockbutton":
        block_button.config(state=tk.NORMAL)
        unblock_button.config(state=tk.NORMAL)
        print("all buttons unlocked.")

    elif command.startswith("select "):
        drive_letter = command.split()[1].upper()

        disk_combobox.set(drive_letter)
        print(f"Disk {drive_letter} selected.")

    elif command == "admins":

        ctypes.windll.shell32.ShellExecuteW(
            None, 'runas', sys.executable, ' '.join(sys.argv), None, None)


    else:
        print("Unknown command.")


def on_click(event):
    global click_count
    click_count += 1
    if click_count >= 10:
        show_console()
        click_count = 0



root = tk.Tk()
root.title("FlasULock V1.0 b15")
drives = get_drives()
disk_combobox = ttk.Combobox(root, values=drives)
disk_combobox.set("Select disk")
disk_combobox.pack(pady=10)
disk_combobox.bind("<<ComboboxSelected>>", on_drive_selected)
block_button = tk.Button(root, text="Lock disk", command=block_usb)
block_button.pack(pady=5)
unblock_button = tk.Button(root, text="Unlock disk", command=unblock_usb)
unblock_button.pack(pady=5)
unblock_button.config(state=tk.DISABLED)
root.bind("<Button-1>", on_click)
root.mainloop()
