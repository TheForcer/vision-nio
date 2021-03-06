from chat_functions import send_text_to_room
from bot_commands import Command
from nio import JoinError, RoomLeaveError
from message_responses import Message

import logging

logger = logging.getLogger(__name__)


class Callbacks(object):
    def __init__(self, client, store, config):
        """
        Args:
            client (nio.AsyncClient): nio client used to interact with matrix

            store (Storage): Bot storage

            config (Config): Bot configuration parameters
        """
        self.client = client
        self.store = store
        self.config = config
        self.command_prefix = config.command_prefix

    async def message(self, room, event):
        """Callback for when a message event is received

        Args:
            room (nio.rooms.MatrixRoom): The room the event came from

            event (nio.events.room_events.RoomMessageText): The event defining the message

        """
        # Extract the message text
        msg = event.body

        # Ignore messages from ourselves
        if event.sender == self.client.user:
            return

        logger.debug(
            f"Bot message received for room {room.display_name} | "
            f"{room.user_name(event.sender)}: {msg}"
        )

        # Process as message if in a public room without command prefix
        has_command_prefix = msg.startswith(self.command_prefix)
        if not has_command_prefix:  # and not room.is_group:
            # General message listener
            message = Message(self.client, self.store, self.config, msg, room, event)
            await message.process()
            return

        # Otherwise if this is in a 1-1 with the bot or features a command prefix,
        # treat it as a command
        if has_command_prefix:
            # Remove the command prefix
            msg = msg[len(self.command_prefix) :]

        command = Command(self.client, self.store, self.config, msg, room, event)
        await command.process()

    async def invite(self, room, event):
        """Callback for when an invite is received. Join the room specified in the invite"""
        logger.debug(f"Got invite to {room.room_id} from {event.sender}.")

        # If user not whitelisted, try to reject for 3 times
        if (self.config.invite_whitelist_enabled) and (
            event.sender not in self.config.invite_whitelist
        ):
            for attempt in range(3):
                result = await self.client.room_leave(room.room_id)
                if type(result) == RoomLeaveError:
                    logger.error(
                        f"Error rejecting invite to room {room.room_id} (attempt %d): %s",
                        attempt,
                        result.message,
                    )
                else:
                    logger.info(
                        f"Reject invite to room {room.room_id}, {event.sender} not whitelisted."
                    )
                    return

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt,
                    result.message,
                )
            else:
                logger.info(f"Joined {room.room_id}")
                break

