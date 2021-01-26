import requests
import os
from ics2000.settings import BASE_URL
from typing import List
from ics2000.commands.Command import Command
from ics2000.commands.CommandBuilder import CommandBuilder
from ics2000.Core import constraint_int


class CommandManager:
    def __init__(self, commandBuilder: CommandBuilder) -> None:
        self.command_builder = commandBuilder
        self.command_queue: List[Command] = []

    def send_command_from_queue(self):
        if len(self.command_queue) == 0:
            return

        command = self.command_queue.pop()
        self._send_command(command)

    def _send_command(self, command):
        url = BASE_URL + "/command.php"

        params = {
            "action": "add",
            "email": os.getenv("EMAIL"),
            "mac": os.getenv("MAC").replace(":", ""),
            "password_hash": os.getenv("PASSWORD"),
            "device_unique_id": "android",
            "command": command}
        requests.get(url, params=params)

    def zigbee_switch(self, entity, power):
        cmd = self.command_builder.new_command(entity, 3, (str(1) if power else str(0)))
        self._send_command(cmd.getcommand())

    def turnoff(self, entity):
        cmd = self.command_builder.new_command(entity, 0, 0)
        self._send_command(cmd)

    def turnon(self, entity):
        cmd = self.command_builder.new_command(entity, 0, 1)
        self._send_command(cmd.getcommand())

    def dim(self, entity, level):
        cmd = self.command_builder.new_command(entity, 1, level)
        self._send_command(cmd.getcommand())

    def zigbee_color_temp(self, entity, color_temp):
        color_temp = constraint_int(color_temp, 0, 600)
        cmd = self.command_builder.new_command(entity, 9, color_temp)
        self._send_command(cmd.getcommand())

    def zigbee_dim(self, entity, dim_lvl):
        dim_lvl = constraint_int(dim_lvl, 1, 254)
        cmd = self.command_builder.new_command(entity, 4, dim_lvl)
        self._send_command(cmd.getcommand())
