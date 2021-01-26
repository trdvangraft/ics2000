from typing import Hashable


class Room(dict):
    def __init__(self, id, hb, name, devices) -> None:
        self._id = id
        self._hub = hb
        self._name = name
        self._devices = devices
        dict.__init__(self, {
            "id": id,
            "name": name,
            "devices": devices
        })

    