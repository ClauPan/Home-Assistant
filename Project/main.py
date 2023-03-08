import os
import json
import copy
from random import *
import tkinter as tk
import speech_recognition as sr
import time


class User:
    def __init__(self, name, location, phone_number):
        self.name = name
        self.location = location
        self.phone_number = phone_number
        self.bracelet = Bracelet(36.3, 90, 120, 98, 100)


class Bracelet:
    def __init__(self, temperature, heart_rate, blood_pressure, blood_h2o, energy_level):
        self.temperature = temperature
        self.blood_pressure = blood_pressure
        self.heart_rate = heart_rate
        self.blood_h2o = blood_h2o
        self.energy_level = energy_level


class Environment:
    def __init__(self):
        self.weather = "clear"
        self.rooms = {}
        self.normal_conditions = {
            "room_temperature": 23,
            "humidity": 45,
            "level_co": 0
        }

    def add_room(self, room):
        self.rooms[room.name] = room

    def get_room(self, name):
        for room in self.rooms:
            if self.rooms[room].name == name:
                return self.rooms[room]
        return None


# stats = {room_temperature: int, humidity: int, level_co: int}
class Room:
    def __init__(self, name, short_name, connections):
        self.name = name
        self.short_name = short_name
        self.connections = connections
        self.stats = {
            "room_temperature": 23,
            "humidity": 45,
            "level_co": 0
        }
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def use_device(self, device_name):
        self.stats[self.devices[device_name].effect[0]] += self.devices[device_name].effect[1]


# effect = {state: (stat(str), change(float))}
class Device:
    def __init__(self, name, action, states, effects):
        self.name = name
        self.action = action
        self.state = "off"
        self.states = states
        self.effects = effects


class GUI:
    def __init__(self):
        self.audio_recog = sr.Recognizer()

        self.root = tk.Tk()
        self.root.title("Disease Prevention System")
        self.root.bind("<Return>", self.run)

        self.text_box = tk.Text(self.root)
        self.text_box.config(state=tk.DISABLED)
        self.text_box.grid(row=0, column=0, sticky=tk.W)

        self.chat_box_text = tk.StringVar()
        self.chat_box = tk.Entry(self.root, width=92, textvariable=self.chat_box_text)
        self.chat_box.grid(row=1, column=0, sticky=tk.W)

        self.listbox_entries = []
        self.listbox = tk.Listbox(self.root, height=26)
        self.listbox.grid(row=0, column=1, rowspan=2, sticky=tk.N)
        self.listbox.bind("<<ListboxSelect>>", self.compile_report)

        self.report_box = tk.Text(self.root, height=24)
        self.report_box.config(state=tk.DISABLED)
        self.report_box.grid(row=0, column=2, rowspan=2, sticky=tk.SW)

        self.button_daily = tk.Button(self.root, text="Daily", command=lambda: self.populate_listbox(1, "day"))
        self.button_weekly = tk.Button(self.root, text="Weekly", command=lambda: self.populate_listbox(7, "week"))
        self.button_monthly = tk.Button(self.root, text="Monthly", command=lambda: self.populate_listbox(30, "month"))
        self.button_yearly = tk.Button(self.root, text="Yearly", command=lambda: self.populate_listbox(364, "year"))
        self.button_daily.place(x=770, y=5)
        self.button_weekly.place(x=810, y=5)
        self.button_monthly.place(x=862, y=5)
        self.button_yearly.place(x=920, y=5)

        self.button_send = tk.Button(self.root, text="Send", command=self.run)
        self.button_mic = tk.Button(self.root, text="Voice", command=lambda: self.audio())
        self.button_mic.grid(row=1, column=0, sticky=tk.E)
        self.button_send.place(x=565, y=392)

        self.root.mainloop()

    def populate_listbox(self, interval, entry_text):
        self.listbox.delete(0, tk.END)
        self.listbox_entries = []
        nr_of_days = get_nr_of_days()
        log_list = []

        for i in range(len(os.listdir("files/logs"))):
            log_list.append("day" + str(i + 1) + ".json")

        days = nr_of_days // interval
        if nr_of_days / interval > days:
            days += 1

        file_index = 0
        while file_index < len(log_list):
            for i in range(0, days, 1):
                self.listbox_entries.append([])
                j = 0
                while j < interval and file_index < len(log_list):
                    self.listbox_entries[-1].append(log_list[file_index])
                    j += 1
                    file_index += 1

        for i in range(len(self.listbox_entries)):
            self.listbox.insert(tk.END, entry_text + " " + str(i + 1))

    def compile_report(self, event):
        selected_entry = self.listbox_entries[self.listbox.curselection()[0]]
        base = {
            "user": {
                "temperature": 0,
                "blood_pressure": 0,
                "heart_rate": 0,
                "blood_h2o": 0,
                "energy_level": 0
            },
            "kitchen": {
                "room_temperature": 0,
                "humidity": 0,
                "level_co": 0
            },
            "bathroom": {
                "room_temperature": 0,
                "humidity": 0,
                "level_co": 0
            },
            "living": {
                "room_temperature": 0,
                "humidity": 0,
                "level_co": 0
            },
            "bedroom": {
                "room_temperature": 0,
                "humidity": 0,
                "level_co": 0
            },
            "action_list": [],
            "warnings": [],
        }
        for log_file in selected_entry:
            log = json.loads(open("files/logs/" + log_file).read())
            for entity in log:
                if type(log[entity]) != list:
                    for stat in log[entity]:
                        base[entity][stat] += log[entity][stat]
                else:
                    base[entity].extend(log[entity])
        for entity in base:
            if type(base[entity]) != list:
                for stat in base[entity]:
                    base[entity][stat] /= len(selected_entry)

        self.report_box.config(state=tk.NORMAL)
        self.report_box.delete("1.0", tk.END)
        self.report_box.insert(tk.END, json.dumps(base, indent=4))
        self.report_box.config(state=tk.DISABLED)

    def insert_text(self, text):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, text + "\n")
        self.text_box.config(state=tk.DISABLED)

    def run(self, event):
        chat_text = self.chat_box_text.get()
        self.chat_box_text.set("")
        self.insert_text(chat_text)
        if chat_text == "cls":
            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete("1.0", tk.END)
            self.text_box.config(state=tk.DISABLED)
            self.listbox.selection_clear(0, tk.END)
            self.report_box.config(state=tk.NORMAL)
            self.report_box.delete("1.0", tk.END)
            self.report_box.config(state=tk.DISABLED)
        if chat_text == "restart":
            start_time = time.time()
            file_list = os.listdir("files/logs")
            for file in file_list:
                os.remove("files/logs/" + file)
            elapsed = time.time() - start_time
            self.chat_box_text.set("")
            self.insert_text("Execution time: " + str(elapsed) + " seconds")
        else:
            chat_text = chat_text.split("-")
            if chat_text[0].strip() == "run":
                start_time = time.time()
                try:
                    sim(int(chat_text[1].strip()))
                except ValueError:
                    self.insert_text("- argument for 'run' must be integer")
                elapsed = time.time() - start_time
                self.insert_text("Execution time: " + str(elapsed) + " seconds")

    def audio(self):
        self.chat_box_text.set(self.record())
        self.run("")

    def record(self):
        while True:
            try:
                with sr.Microphone() as source2:
                    self.audio_recog.adjust_for_ambient_noise(source2, duration=1)
                    return self.audio_recog.recognize_google(self.audio_recog.listen(source2)).lower().strip()
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
            except sr.UnknownValueError:
                print("unknown error occurred")


my_time = 0
user = User("Joe", "Street nr. 2", "5555555555")
envir = Environment()
diseases = {}
actions = actions_copy = {}
limits = {}
report = []

rooms_short_to_long = {
    "b": "Bathroom",
    "k": "Kitchen",
    "h": "Hallway",
    "B": "Bedroom",
    "l": "Living",
}
keep_on = []


def init():
    global user, envir, diseases, actions, actions_copy, limits

    diseases = json.loads(open("files/diseases.json").read())
    actions = json.loads(open("files/actions.json").read())
    limits = json.loads(open("files/limit.json").read())

    actions_copy = copy.deepcopy(actions)

    user = User("Joe", "Street nr. 2", "5555555555")
    envir = Environment()

    envir.add_room(Room("Hallway", "h", ["Bedroom", "Kitchen", "Bathroom", "Living"]))
    envir.add_room(Room("Kitchen", "k", ["Hallway", "Living"]))
    envir.add_room(Room("Bathroom", "b", ["Hallway", "Bedroom"]))
    envir.add_room(Room("Living", "l", ["Hallway", "Kitchen"]))
    envir.add_room(Room("Bedroom", "B", ["Hallway", "Bathroom"]))

    envir.rooms["Kitchen"].add_device(
        Device(
            "Stove",
            "cook",
            ["off", "gas", "fire"],
            {
                "off": None,
                "gas": ("co", 0.05),
                "fire": ("rtemp", 0.05)
            }
        )
    )
    envir.rooms["Living"].add_device(
        Device(
            "ACU",
            "ACU",
            ["off", "cooling", "heating"],
            {
                "off": None,
                "cooling": ("rtemp", -1),
                "heating": ("rtemp", 1)
            }
        )
    )
    envir.rooms["Bedroom"].add_device(
        Device(
            "ACU",
            "ACU",
            ["off", "cooling", "heating"],
            {
                "off": None,
                "cooling": ("rtemp", -1),
                "heating": ("rtemp", 1)
            }
        )
    )
    envir.rooms["Bathroom"].add_device(
        Device(
            "Shower",
            "shower",
            ["off", "on"],
            {
                "off": None,
                "on": ("hum", 0.1)
            }
        )
    )


def sim(days_to_sim):
    global my_time, user, envir, diseases, actions, limits
    current_room = envir.get_room("Bedroom")

    def apply_effect(name, value):
        if name == "temp":
            user.bracelet.temperature += value
        elif name == "bpr":
            user.bracelet.blood_pressure += value
        elif name == "hr":
            user.bracelet.heart_rate += value
        elif name == "bh2o":
            user.bracelet.blood_h2o += value
        elif name == "eng":
            user.bracelet.energy_level += value
        elif name == "rtemp":
            current_room.stats["room_temperature"] += value
        elif name == "hum":
            current_room.stats["humidity"] += value
        elif name == "co":
            current_room.stats["level_co"] += value

    def normalize_factors(current_action_time):
        if "temp" not in changed_factors:
            if user.bracelet.temperature < 36.2:
                user.bracelet.temperature += 0.005 * current_action_time
            elif user.bracelet.temperature > 36.2:
                user.bracelet.temperature -= 0.005 * current_action_time
        if "bpr" not in changed_factors:
            if user.bracelet.blood_pressure < 120:
                user.bracelet.blood_pressure += 0.01 * current_action_time
            elif user.bracelet.blood_pressure > 120:
                user.bracelet.blood_pressure -= 0.01 * current_action_time
        if "hr" not in changed_factors:
            if user.bracelet.heart_rate < 90:
                user.bracelet.heart_rate += 0.1 * current_action_time
            elif user.bracelet.heart_rate > 90:
                user.bracelet.heart_rate -= 0.1 * current_action_time
        if "bh2o" not in changed_factors:
            if user.bracelet.blood_h2o < 98:
                user.bracelet.blood_h2o += 0.001 * current_action_time
            elif user.bracelet.blood_h2o >= 98:
                user.bracelet.blood_h2o -= 0.001 * current_action_time
        if "eng" not in changed_factors:
            if user.bracelet.energy_level < 100:
                user.bracelet.energy_level += 0.001 * current_action_time
            elif user.bracelet.energy_level > 100:
                user.bracelet.energy_level = 100
        for this_room in envir.rooms:
            if "rtemp" not in changed_factors:
                if envir.rooms[this_room].stats["room_temperature"] < 23:
                    envir.rooms[this_room].stats["room_temperature"] += 0.01 * current_action_time
                elif envir.rooms[this_room].stats["room_temperature"] >= 23:
                    envir.rooms[this_room].stats["room_temperature"] -= 0.01 * current_action_time
            if "hum" not in changed_factors:
                if envir.rooms[this_room].stats["humidity"] < 45:
                    envir.rooms[this_room].stats["humidity"] += 0.01 * current_action_time
                elif envir.rooms[this_room].stats["humidity"] >= 45:
                    envir.rooms[this_room].stats["humidity"] -= 0.01 * current_action_time
            if "co" not in changed_factors:
                if envir.rooms[this_room].stats["level_co"] < 0:
                    envir.rooms[this_room].stats["level_co"] += 0.1 * current_action_time
                elif envir.rooms[this_room].stats["level_co"] > 0:
                    envir.rooms[this_room].stats["level_co"] -= 0.1 * current_action_time

    def get_device(device_name):
        for this_room in envir.rooms:
            for this_device in envir.rooms[this_room].devices:
                if this_device.name == device_name:
                    return this_device

    def check_limit(factor, value):
        if factor in limits:
            if value < limits[factor][0]:
                return -1
            elif value > limits[factor][1]:
                return 1
            else:
                return 0

    def check_diseases():
        current_user_factor_values = {
            "temperature": user.bracelet.temperature,
            "blood_pressure": user.bracelet.blood_pressure,
            "heart_rate": user.bracelet.heart_rate,
            "blood_h2o": user.bracelet.blood_h2o,
            "energy_level": user.bracelet.energy_level
        }
        for user_factor in current_user_factor_values:
            check_result = check_limit(user_factor, current_user_factor_values[user_factor])
            if check_result != 0:
                for disease in diseases:
                    if user_factor in diseases[disease]["factors"]:
                        if check_result == diseases[disease]["factors"][user_factor]:
                            warnings.append("Disease Alert, " + disease.replace("_", " ").capitalize() + " detected.")

        room_stats = ["room_temperature", "humidity", "level_co"]

        for this_room in envir.rooms:
            for room_stat in room_stats:
                check_result = check_limit(room_stat, envir.rooms[this_room].stats[room_stat])
                if check_result != 0:
                    for disease in diseases:
                        if room_stat in diseases[disease]["factors"]:
                            if check_result == diseases[disease]["factors"][room_stat]:
                                warnings.append(
                                    "Disease Alert, " + disease.replace("_", " ").capitalize() + " detected.")

    def in_keep_on(current_action):
        is_in_keep_on = False, None
        for k in range(len(keep_on)):
            if keep_on[k][0]["name"] == current_action:
                is_in_keep_on = True, k
        return is_in_keep_on

    warnings = []
    action_list = []
    day_count = 1
    i = 0
    while i // 1440 <= days_to_sim:
        changed_factors = []
        j = 0
        while j < len(keep_on):
            device = get_device(keep_on[j][0]["name"])
            if i - keep_on[j][1] > 20:
                warnings.append(
                    "Device alert; " + device.name + " has remained in a running state for too long. Shutting down due to health concerns.")
                device.state = "off"
                keep_on.pop(j)
            elif i - keep_on[j][1] > 10:
                warnings.append("Device alert; " + device.name + " may have been forgotten in a running state.")
                j += 1
            else:
                device.state = keep_on[j][0]["set"]
                j += 1

        if len(actions) < 2:
            actions = copy.deepcopy(actions_copy)
        if user.bracelet.energy_level > 50:
            action = actions[list(actions.keys())[randint(0, len(actions.keys()) - 1)]]
            actions.pop(action["name"])
        else:
            action = actions_copy["sleep"]

        action_list.append(action["name"])
        action_time = randint(action["time"][0], action["time"][1])
        if action_time % 2 != 0:
            action_time += 1

        if current_room.short_name not in action["room"]:
            current_room = envir.get_room(rooms_short_to_long[action["room"][randint(0, len(action["room"]) - 1)]])

        if action["use"] != "":
            current_room.devices[0].state = action["use"]
            kept_on, index = in_keep_on(current_room.devices[0].name)
            if kept_on:
                keep_on.pop(index)

        for effect in action["effects"]:
            if effect[2] == "o":
                apply_effect(effect[0], effect[1])
            elif effect[2] == "t":
                apply_effect(effect[0], effect[1] * action_time)
            if effect[0] not in changed_factors:
                changed_factors.append(effect[0])

        for room in envir.rooms:
            current_room = envir.rooms[room]
            for device in current_room.devices:
                if device.state != "off":
                    apply_effect(device.effects[device.state][0], device.effects[device.state][1] * action_time)

        for event in action["events"]:
            if uniform(0, 100) < action["events"][event]["chance"]:
                if not in_keep_on(action["name"])[0]:
                    keep_on.append((action["events"][event], i))
        for room in envir.rooms:
            current_room = envir.rooms[room]
            for device in current_room.devices:
                if not in_keep_on(device.name)[0]:
                    device.state = "off"

        check_diseases()
        normalize_factors(action_time)

        if i // 1440 >= day_count:
            if user.bracelet.energy_level > 100:
                user.bracelet.energy_level = 100

            this_day = {
                "user": {
                    "temperature": user.bracelet.temperature,
                    "blood_pressure": user.bracelet.blood_pressure,
                    "heart_rate": user.bracelet.heart_rate,
                    "blood_h2o": user.bracelet.blood_h2o,
                    "energy_level": user.bracelet.energy_level
                },
                "kitchen": {
                    "room_temperature": envir.rooms["Kitchen"].stats["room_temperature"],
                    "humidity": envir.rooms["Kitchen"].stats["humidity"],
                    "level_co": envir.rooms["Kitchen"].stats["level_co"]
                },
                "bathroom": {
                    "room_temperature": envir.rooms["Bathroom"].stats["room_temperature"],
                    "humidity": envir.rooms["Bathroom"].stats["humidity"],
                    "level_co": envir.rooms["Bathroom"].stats["level_co"]
                },
                "living": {
                    "room_temperature": envir.rooms["Living"].stats["room_temperature"],
                    "humidity": envir.rooms["Living"].stats["humidity"],
                    "level_co": envir.rooms["Living"].stats["level_co"]
                },
                "bedroom": {
                    "room_temperature": envir.rooms["Bedroom"].stats["room_temperature"],
                    "humidity": envir.rooms["Bedroom"].stats["humidity"],
                    "level_co": envir.rooms["Bedroom"].stats["level_co"]
                },
                "action_list": action_list,
                "warnings": warnings,
            }
            open("files/logs/day" + str(day_count) + ".json", "w").write(json.dumps(this_day, indent=4))
            warnings = []
            action_list = []
            day_count += 1

        i += action_time


def get_nr_of_days():
    return len(os.listdir("files/logs"))


init()
GUI()
