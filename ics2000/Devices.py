from ics2000.TrustEnconder import TrustEncodable
import json
from typing import Optional


class Device(TrustEncodable):
    def __init__(self, name, entity_id, hb):
        self._hub = hb
        self._name = name
        self._id = entity_id
        print(str(self._name) + " : " + str(self._id))

    def name(self):
        return self._name

    def turnoff(self):
        cmd = self._hub.getcmdswitch(self._id, False)
        self._hub.sendcommand(cmd.getcommand())

    def turnon(self):
        cmd = self._hub.getcmdswitch(self._id, True)
        self._hub.sendcommand(cmd.getcommand())

    def getstatus(self) -> Optional[bool]:
        return self._hub.getlampstatus(self._id)
    
    def __str__(self) -> str:
        return json.dumps({
            self._id,
            self._name
        }, indent=2)

    def toJson(self) -> dict:
        return {
            "id": self._id,
            "name": self._name
        }


class Dimmer(Device):

    def dim(self, level):
        if level < 0 or level > 15:
            return
        cmd = super()._hub.getcmddim(super()._hub, level)
        super()._hub.sendcommand(cmd.getcommand())

class ZigbeeZll(Device):
    def __init__(self, name, entity_id, hb, info, additional_info, module_info):
        super().__init__(name, entity_id, hb)
        self.info = info
        self.additional_info = additional_info
        self.module_info = module_info

    def toJson(self) -> dict:
        device = super().toJson()
        device.update({
            "info": self.info,
            "additional_info": self.additional_info,
            "module_info": self.module_info
        })
        return device