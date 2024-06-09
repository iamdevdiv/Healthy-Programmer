# ----------------- HEALTHY PROGRAMMER -----------------
# Created by Divyanshu Tiwari

# IMPORTS AND INITIALIZATION
import random 
import shutil
import datetime  
import time
import os
import keyboard
import threading
import webbrowser
import win32gui
import win32.lib.win32con as win32con
import subprocess
from pygame import mixer
from pathlib import Path
from win32com.client import Dispatch
mixer.init()


# CLEAR THE CONSOLE AND SET TITLE
os.system('cls')  # clearing console
os.system('title Healthy Programmer: Running')  # setting title


# GLOBAL VARIABLES
program_running = True
program_paused = False
running_or_stopped = "Running"
commands_enabled = False
console_visible = False


# SOUND FILES
drink_water_sound = mixer.Sound("Sounds/drink_water.mp3")
physical_activity_sound = mixer.Sound("Sounds/physical_activity.mp3")
eyes_exercise_sound = mixer.Sound("Sounds/eyes_exercise.mp3")


# PROGRAM FILES RELATED OPERATIONS
if not os.path.exists(f"{Path.home()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
                      f"/Startup/Healthy Programmer.ink"):  # adding program to startup items
    shell = Dispatch('WScript.shell')
    shortcut = shell.createShortcut(os.path.join(Path.home(), "AppData", "Roaming", "Microsoft", "Windows",
                                                 "Start Menu", "Programs", "Startup", "Healthy Programmer.lnk"))
    shortcut.Targetpath = os.getcwd() + "/Healthy Programmer.exe"
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.save()

if not os.path.exists("Log Files"):  # creating folder for saving log files
    os.mkdir("Log Files")

log_files = ["Log Files/Water.txt", "Log Files/Eyes Exercise.txt", "Log Files/Physical Activity.txt"]
for log_file in log_files:  # creating log files and writing heading in it if not already written
    if not os.path.exists(log_file):
        with open(log_file, "w") as new_file:
            new_file.close()
    txt_name = (log_file.split("/")[1]).split(".")[0]
    with open(log_file, "r+") as f:
        first_line = f.readline()
        if first_line != f"{txt_name.upper()} LOGS : HEALTHY PROGRAMMER\n":
            f.seek(0)
            f.write(f"{txt_name.upper()} LOGS : HEALTHY PROGRAMMER\n")

if not os.path.exists(f"Clock format.txt"):  # creating txt to file to save clock format
    with open(f"Clock format.txt", "w") as clock_format:
        clock_format.write("12")

with open(f"Clock format.txt") as clock_format:  # storing clock formats in variables
    time_format = int(clock_format.read())
time_format_reverse = 24 if time_format == 12 else 12


# VARIABLES AND FUNCTIONS RELATED TO TIMING OF REMINDERS
drink_water_timings = []  # hours:minutes:seconds
physical_activity_timings = []  # eyes exercise and body movement both
physical_activity_info = {}
upcoming_intervals = {24: {}, 12: {}}
full_format_time = {}
minutes_to_add = 30  # for physical activity


def get_next_time(to_add, activity):  # returns the timings of next reminders
    hours_now_24 = datetime.datetime.now().hour
    hours_now_12 = int(datetime.datetime.now().strftime("%I"))
    minutes_now = datetime.datetime.now().minute
    am_or_pm = datetime.datetime.now().strftime("%p")
    now = datetime.datetime.now()
    day_now = now.day

    for i in range(to_add):
        minutes_now += 1
        if minutes_now == 60:
            minutes_now = 0
            hours_now_24 += 1
            hours_now_12 += 1
            if hours_now_24 == 24:
                hours_now_24 = 0
                day_now += 1
            if hours_now_12 == 12:
                am_or_pm = "PM" if am_or_pm == "AM" else "AM"
            elif hours_now_12 == 13:
                hours_now_12 = 1
                
    time_list_int_24 = [hours_now_24, minutes_now, 0]  # used by program for giving reminders
    time_list_str_24 = []
    time_list_int_12 = [hours_now_12, minutes_now]
    time_list_str_12 = []  # for showing time to user in 12 hour format

    for items in time_list_int_24:
        time_list_str_24.append(str(items)) if len(str(items)) == 2 else time_list_str_24.append(f"0{str(items)}")

    for items in time_list_int_12:
        time_list_str_12.append(str(items)) if len(str(items)) == 2 else time_list_str_12.append(f"0{str(items)}")

    full_format_time[activity] = datetime.datetime(now.year, now.month, day_now, hours_now_24, minutes_now, 0)
    upcoming_intervals[24][activity] = f"{time_list_str_24[0]}:{time_list_str_24[1]}"
    upcoming_intervals[12][activity] = f"{time_list_str_12[0]}:{time_list_str_12[1]} {am_or_pm}"

    return time_list_int_24


def set_next_interval(activity):  # set the timings of next activities using above function
    global drink_water_timings, physical_activity_timings, minutes_to_add, physical_activity_info
    if activity == "water":
        drink_water_timings = get_next_time(60, "water")
    elif activity == "physical":
        physical_activity_timings = get_next_time(minutes_to_add, "physical")
        minutes_to_add = 60
        random_number = random.randint(1, 10)
        prime_number = True
        for divisor in range(2, random_number):
            if random_number % divisor == 0:
                prime_number = False
        if prime_number:
            physical_activity_info["sound"] = physical_activity_sound
            physical_activity_info["command"] = "\nIt's time to move. Do some physical activity, then press enter: "
            physical_activity_info["file"] = "Log Files/Physical Activity.txt"
            physical_activity_info["next"] = "body movement"
        else:
            physical_activity_info["sound"] = eyes_exercise_sound
            physical_activity_info["command"] = "\nYour eyes need some rest. Exercise your eyes, then press enter: "
            physical_activity_info["file"] = "Log Files/Eyes Exercise.txt"
            physical_activity_info["next"] = "eyes exercise"


set_next_interval("water")
set_next_interval("physical")


# HIDE AND SHOW CONSOLE WINDOW
def hide_console_window():
    global running_or_stopped, console_visible
    window = win32gui.FindWindow(None, f"Healthy Programmer: {running_or_stopped}")
    win32gui.ShowWindow(window, win32con.SW_HIDE)
    console_visible = False
    keyboard.press_and_release("alt+tab")


def show_console_window(auto_show):
    global running_or_stopped, commands_enabled, console_visible
    if not console_visible:
        window = win32gui.FindWindow(None, f"Healthy Programmer: {running_or_stopped}")
        win32gui.ShowWindow(window, win32con.SW_SHOW)
        console_visible = True
    if not auto_show:
        commands_enabled = True


# ADD KEYBOARD HOTKEY TO SHOW CONSOLE WINDOW
keyboard.add_hotkey("ctrl+alt+z", show_console_window, args=(False,))


# PRINT MAIN COMMANDS
def show_main_commands():
    print("\nCommands:")
    print("    upcoming()  : Check the timings of the upcoming reminders")
    print("    log()       : View Logs")
    print("    clock()     : Change clock format")
    print("    clear()     : Clear console window")
    print("    about()     : Know about the program and its creator")
    print("    hide()      : Hide Healthy Programmer")
    print("    stop()      : Stop Healthy Programmer")
    print("    source()    : Get Source Code of Healthy Programmer")


# ABOUT HEALTHY PROGRAMMER (about() command)
def show_program_info():
    print("\n-------------------------------------------------------------")
    print("HEALTHY PROGRAMMER is a tool created by a coder for coders!")
    print("Programmers usually spend their day sitting on a chair for long hours. Once sat, they do not move from their"
          " seat. Sitting for a long time affects their health a lot. A programmer needs to take rest on regular"
          " intervals to keep himself fit and fine.")
    print("This program will remind you to drink water, rest their eyes, and do physical activity regularly. These"
          " activities in between their work ensure their good health. Thus, programmers do not get frustrated while"
          " coding, and this will also increase their productivity.")
    print("STAY HEALTHY! CODE MORE!")
    print("Version: 1.1")
    print("Created by Divyanshu Tiwari")
    print("(GitHub: https://github.com/iamdevdiv/)")
    print("-------------------------------------------------------------")


# COMMAND HANDLER
def handle_commands():
    global minutes_to_add, program_running, program_paused, commands_enabled, running_or_stopped, time_format, \
        time_format_reverse
    print("----------------- HEALTHY PROGRAMMER -----------------")
    print("STAY HEALTHY! CODE MORE!\n")
    show_main_commands()
    while program_running:
        if commands_enabled:  # true when user uses the hotkey to reveal the console window
            command = input("\nEnter command here: ").lower().strip()
            if command == "upcoming()":
                print(f"Next drink water reminder is scheduled at {upcoming_intervals[time_format]['water']}")
                print(f"Next physical activity is {physical_activity_info['next']}, scheduled at "
                      f"{upcoming_intervals[time_format]['physical']}")
            elif command == "log()": 
                print("\nWhich log do you want to view?")
                log_reference = {"1": "Water", "2": "Eyes Exercise", "3": "Physical Activity"}
                print("1: Water\n2: Eyes Exercise\n3: Physical Activity")
                question_asked = True
                while question_asked:
                    try:
                        which_log = log_reference[input("\n1/2/3: ").strip()]
                        with open(f"Log Files/{which_log}.txt", "r") as log:
                            log_text = log.read()
                            if "[" in log_text:
                                print("\n-------------------------------------------")
                                print(log_text)
                                print("-------------------------------------------")
                                while question_asked:
                                    download = input("\nDo you want to save this log as a text file? (y/n): ").lower()\
                                        .strip()
                                    if download == "y" or download == "yes":
                                        if not os.path.exists(Path.home()/"Documents"/"Healthy Programmer Logs"):
                                            os.mkdir(Path.home()/"Documents"/"Healthy Programmer Logs")
                                        shutil.copyfile(f"Log Files/{which_log}.txt",
                                                        f"{Path.home()}/Documents/Healthy Programmer Logs/"
                                                        f"{which_log} Logs.txt")
                                        print("The log has been saved to your system's Documents folder.")
                                        question_asked = False
                                    elif download == "n" or download == "no":
                                        question_asked = False
                                    elif download == "":
                                        pass
                                    else:
                                        print("Wrong Input! Try Again...")
                            else:
                                print(f"No log found for {which_log}!")
                                question_asked = False
                    except KeyError:
                        print("Wrong Input! Try Again...")
            elif command == "clock()":
                question_asked = True
                while question_asked:
                    yes_or_no = input(f"\n{time_format}-hour clock is current clock format. Do you want to switch to "
                                      f"{time_format_reverse}-hour clock? (y/n): ").lower().strip()
                    if yes_or_no == "y" or yes_or_no == "yes":
                        time_format, time_format_reverse = time_format_reverse, time_format
                        with open(f"Clock format.txt", "w") as changed_clock_format:
                            changed_clock_format.write(str(time_format))
                        print(f"The clock format is changed to {time_format}-hour clock!")
                        question_asked = False
                    elif yes_or_no == "n" or yes_or_no == "no":
                        print("Clock format not changed!")
                        question_asked = False
                    else:
                        print("Wrong Input! Try Again...")
            elif command == "clear()":
                os.system('cls')
                print("----------------- HEALTHY PROGRAMMER -----------------")
                print("STAY HEALTHY! CODE MORE!\n")
                show_main_commands()
            elif command == "about()":
                show_program_info()
            elif command == "hide()":
                hide_console_window()
                commands_enabled = False
            elif command == "stop()":
                program_paused = True
                minutes_to_add = 30
                running_or_stopped = "Stopped"
                os.system('title Healthy Programmer: Stopped')
                print("Healthy Programmer Stopped!")
                print("Commands:")
                print("    restart() : Restart Healthy Programmer")
                print("    hide()    : Hide Healthy Programmer")
                print("    kill()    : Terminate Healthy Programmer completely")
                question_asked = True
                while question_asked:
                    start_hide_kill = input("\nRestart/Hide/Kill: ").lower().strip()
                    if start_hide_kill == "restart()":
                        set_next_interval("water")
                        set_next_interval("physical")
                        program_paused = False
                        question_asked = False
                        running_or_stopped = "Running"
                        os.system("title Healthy Programmer: Running")
                        print("Healthy Programmer Restarted!")
                        show_main_commands()
                    elif start_hide_kill == "hide()":
                        hide_console_window()
                        commands_enabled = False
                    elif start_hide_kill == "kill()":
                        skip = False
                        while not skip:
                            yes_or_no = input("\nAre you sure? The program will restart on next system boot (y/n): ")\
                                .lower().strip()
                            if yes_or_no == "y" or yes_or_no == "yes":
                                skip = True
                                question_asked = False
                                program_running = False
                            elif yes_or_no == "n" or yes_or_no == "no":
                                skip = True
                            else:
                                print("Wrong Input! Try Again...")
                    elif start_hide_kill == "":
                        pass
                    else:
                        print("No such command found! Try again...")
            elif command == "source()":
                webbrowser.open("https://github.com/iamdevdiv/Healthy-Programmer")
            elif command == "kill()":
                print("Healthy Programmer must be stopped before being killed! Use stop() to stop it.")
            elif command == "":
                pass
            else:
                print("No such command found! Try again...")

        time.sleep(0.2)  # to prevent high CPU usage


# REMINDER
def remind():
    global program_paused, program_running, commands_enabled, minutes_to_add
    while program_running:
        if not program_paused:
            current_time = [int(x) for x in datetime.datetime.now().strftime("%X").split(":")]  # hours:minutes:seconds

            # If user is working with commands in the console window, this if-else block will pause the loop by
            # starting another while loop
            if (commands_enabled and current_time == drink_water_timings) or \
                    (commands_enabled and current_time == physical_activity_timings):
                while commands_enabled:
                    time.sleep(0.2)

            # Main reminders
            if current_time == drink_water_timings:
                show_console_window(True)
                drink_water_sound.play()
                question_asked = True
                while question_asked:
                    enter = input("\nYour throat is thirsty! Drink a glass of water, then press enter: ").lower()\
                        .strip()
                    if enter == "":
                        print("Good!")
                        question_asked = False
                    else:
                        print("Just press enter!")
                hide_console_window()
                time_info = datetime.datetime.now().strftime("%c")
                with open("Log Files/Water.txt", "a") as water_log_file:
                    water_log_file.write(f"\n[{time_info}]")
                set_next_interval("water")
            
            if current_time == physical_activity_timings:
                show_console_window(True)
                physical_activity_info["sound"].play()
                question_asked = True
                while question_asked:
                    enter = input(physical_activity_info["command"]).lower().strip()
                    if enter == "":
                        print("Good!")
                        question_asked = False
                    else:
                        print("Just press enter!")
                hide_console_window()
                time_info = datetime.datetime.now().strftime("%c")
                with open(physical_activity_info["file"], "a") as selected_log_file:
                    selected_log_file.write(f"\n[{time_info}]")
                set_next_interval("physical")
            
            # Set new time for reminder if it founds that any reminder didn't get execute at its already set time
            # and that time has passed.
            now = datetime.datetime.now()
            if now > full_format_time["physical"]:
                minutes_to_add = 30
                set_next_interval("physical")
            if now > full_format_time["water"]:
                minutes_to_add = 30
                set_next_interval("physical")
                set_next_interval("water")

        time.sleep(0.2)  # to prevent high CPU usage


# STARTING PROGRAM
already_running = (subprocess.check_output("tasklist").decode("ascii")).count("Healthy Programmer.exe") > 1

if not already_running:  # if Healthy Programmer is not running, start it
    hide_console_window()
    commands_thread = threading.Thread(target=handle_commands)
    reminder_thread = threading.Thread(target=remind)
    commands_thread.start()
    reminder_thread.start()
else:  # if it is already running, inform it to the user
    print("Healthy Programmer is already running! Use Ctrl+Alt+Z shortcut to show it.")
    while True:
        exit_window = input("\nPress enter to exit this window: ").lower().strip()
        if exit_window == "":
            break
        else:
            print("Just press enter!")
            