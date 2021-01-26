from ics2000.commands.Command import Command

class CommandBuilder:
    def __init__(self, mac) -> None:
        self.mac = mac

    def new_command(self, entity, function, value):
        cmd = Command() \
            .setmac(self.mac) \
            .settype(128) \
            .setmagic() \
            .setentityid(entity) \
            .setdata(
                {
                    "module": {
                        "id": entity,
                        "function": function,
                        "value": value
                    }
                },
                self.aes
            )
            # "{\"module\":{\"id\":" + str(entity) + ",\"function\":" + str(function) + ",\"value\":" + str(value) + "}}",

        return cmd