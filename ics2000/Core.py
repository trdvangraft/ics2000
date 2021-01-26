import enum
from ics2000.Cryptographer import decrypt
from ics2000.settings import BASE_URL
from ics2000.TrustEnconder import TrustEnconder
from ics2000.Room import Room
from typing import List
import requests
import json
import ast

from ics2000.Devices import *

from deepdiff import DeepDiff

def constraint_int(inp, min_val, max_val) -> int:
    if inp < min_val:
        return min_val
    elif inp > max_val:
        return max_val
    else:
        return inp


class Hub:
    aes = None
    mac = None

    def __init__(self, mac, email, password):
        """Initialize an ICS2000 hub."""
        self.mac = mac
        self._email = email
        self._password = password
        self._connected = False
        self._homeId = -1
        self._devices : List[Device] = []
        self._rooms : List[Room] = []
        self.loginuser()
        self.pulldevices()
        self.get_my_devices()

    def loginuser(self):
        print("Logging in user")
        url = BASE_URL + "/account.php"
        params = {"action": "login", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "device_unique_id": "android", "platform": "Android"}
        req = requests.get(url, params=params)
        if req.status_code == 200:
            resp = json.loads(req.text)
            self.aes = resp["homes"][0]["aes_key"]
            self._homeId = resp["homes"][0]["home_id"]
            if self.aes is not None:
                print("Succesfully got AES key")
                self._connected = True

    def connected(self):
        return self._connected

    def pulldevices(self):
        url = BASE_URL + "/gateway.php"
        params = {"action": "sync", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "home_id": self._homeId}
        resp = requests.get(url, params=params)
        self._devices = []
        self._rooms = []

        devices = json.loads(resp.text)
        decrypted_devices = [json.loads(decrypt(device["data"], self.aes)) for device in devices]

        for decrypted in decrypted_devices:
            if "module" in decrypted and "info" in decrypted["module"]:
                decrypted = decrypted["module"]
                name = decrypted["name"]
                entityid = decrypted["id"]

                devices = [item.value for item in DeviceType]
                if decrypted["device"] not in devices:
                    self._devices.append(Device(name, entityid, self))
                    continue
                dev = DeviceType(decrypted["device"])
                if dev == DeviceType.LAMP:
                    self._devices.append(Device(name, entityid, self))
                if dev == DeviceType.DIMMER:
                    self._devices.append(Dimmer(name, entityid, self))
                if dev == DeviceType.OPENCLOSE:
                    self._devices.append(Device(name, entityid, self))
                if dev == DeviceType.ZIGBEEZLL:
                    info, additional_info, module_info = decrypted["info"], decrypted["additional_info"], decrypted["extended_module_info"]
                    self._devices.append(ZigbeeZll(name, entityid, self, info, additional_info, module_info))
            elif "room" in decrypted:
                decrypted = decrypted["room"]
                name = decrypted["name"]
                entityid = decrypted["id"]
                modules = decrypted["modules"]
                self._rooms.append(Room(entityid, self, name, modules))


    def devices(self):
        return self._devices

    def get_device_status(self, entity) -> []:
        url = BASE_URL + "/entity.php"
        params = {"action": "get-multiple", "email": self._email, "mac": self.mac.replace(":", ""),
                  "password_hash": self._password, "home_id": self._homeId, "entity_id": "[" + str(entity) + "]"}
        resp = requests.get(url, params=params)
        arr = json.loads(resp.text)
        if len(arr) == 1 and "status" in arr[0] and arr[0]["status"] is not None:
            obj = arr[0]
            dcrpt = json.loads(decrypt(obj["status"], self.aes))
            if "module" in dcrpt and "functions" in dcrpt["module"]:
                return dcrpt["module"]["functions"]
        return []

    def getlampstatus(self, entity) -> Optional[bool]:
        status = self.get_device_status(entity)
        if len(status) >= 1:
            return True if status[0] == 1 else False
        return False

    

    def get_my_devices(self):
        my_room : Room = next(filter(lambda room : room._name == "Tijmen", self._rooms))
        my_modules = my_room._devices
        my_devices = [device for device in self._devices if device._id in my_modules]

        result = [my_room] + my_devices

        FILE_NAME = "light_on_red"

        with open(f"{FILE_NAME}.json", "w") as f:
            json.dump(result, f, indent=4, cls=TrustEnconder)

        with open("baseline.json", "r") as r:
            baseline = json.load(r)

        with open(f"{FILE_NAME}.json", "r") as r:
            test = json.load(r)

        diff = DeepDiff(baseline, test)
        print(diff)

class DeviceType(enum.Enum):
    LAMP = 1
    DIMMER = 2
    OPENCLOSE = 3
    ZIGBEEZLL = 40


def get_hub(mac, email, password) -> Optional[Hub]:
    url = BASE_URL + "/gateway.php"
    params = {"action": "check", "email": email, "mac": mac.replace(":", ""), "password_hash": password}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        if ast.literal_eval(resp.text)[1] == "true":
            return Hub(mac, email, password)
    return

