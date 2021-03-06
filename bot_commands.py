from chat_functions import send_text_to_room
import requests
import json


class Command(object):
    def __init__(self, client, store, config, command, room, event):
        """A command made by a user

        Args:
            client (nio.AsyncClient): The client to communicate to matrix with

            store (Storage): Bot storage

            config (Config): Bot configuration parameters

            command (str): The command and arguments

            room (nio.rooms.MatrixRoom): The room the command was sent in

            event (nio.events.room_events.RoomMessageText): The event describing the command
        """
        self.client = client
        self.store = store
        self.command = command
        self.config = config
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]

    async def process(self):
        """Process the command"""
        if self.command.startswith("echo"):
            await self._echo()
        elif self.command.startswith("help"):
            await self._show_help()
        elif self.command.startswith("ads"):
            await self._pihole_stats()
        elif self.command.startswith("uptime"):
            await self._utrobot_stats()
        else:
            await self._unknown_command()

    async def _echo(self):
        """Echo back the command's arguments"""
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _show_help(self):
        """Show the help text"""
        if not self.args:
            text = (
                "Hello, I am a bot made with matrix-nio! Use `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = "These are the rules!"
        elif topic == "commands":
            text = "Available commands"
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _pihole_stats(self):
        """Echo back some PiHole stats"""
        url = self.config.pihole_url + "/admin/api.php"
        json_data = json.loads(requests.request("GET", url, data="", headers="").text)
        response = (
            "**PiHole Stats** 🖥️<br>Today's DNS queries: **"
            + str(json_data["dns_queries_today"])
            + "**<br>Blocked: **"
            + str(json_data["ads_blocked_today"])
            + "** / **"
            + str(round(json_data["ads_percentage_today"], 2))
            + "**%<br>Client count: **"
            + str(json_data["unique_clients"])
            + "**"
        )
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _utrobot_stats(self):
        """Echo back some uptimerobot stats"""
        payload = (
            f"api_key={self.config.utrobot_apikey}&format=json&logs=1&response_times=1"
        )
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }
        url = "https://api.uptimerobot.com/v2/getMonitors"
        json_data = json.loads(
            requests.request("POST", url, data=payload, headers=headers).text
        )
        response = (
            "**Uptime Stats for "
            + str(json_data["pagination"]["total"])
            + " services:** <br><br>**Response Time**:"
        )
        for monitor in json_data["monitors"]:
            response = (
                response
                + "<br>- "
                + monitor["friendly_name"]
                + ": "
                + str(monitor["response_times"][0]["value"])
                + "ms"
            )
        response = response + "<br><br>**Current Status**: "
        for monitor in json_data["monitors"]:
            if monitor["logs"][0]["type"] == 2:
                response = (
                    response
                    + "<br>- "
                    + monitor["friendly_name"]
                    + ": ✅ for "
                    + str(round((monitor["logs"][0]["duration"]) / 60 / 60 / 24, 2))
                    + " days"
                )
            elif monitor["logs"][0]["type"] == 1:
                response = (
                    response
                    + "<br>- "
                    + monitor["friendly_name"]
                    + ": ❌ for "
                    + str(round((monitor["logs"][0]["duration"]) / 60 / 60 / 24, 2))
                    + " days"
                )
            else:
                response = (
                    response
                    + "<br>- "
                    + monitor["friendly_name"]
                    + ": ❓️ paused/rebooting"
                )
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"I don't know '{self.command}'. Please try again.",
        )
