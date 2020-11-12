import logging
import os
import traceback
from enum import Enum

from aiarena import settings
from aiarena.core.models import Result, Bot
from aiarena.core.utils import post_result_to_discord_bot

logger = logging.getLogger(__name__)


class EventType(Enum):
    MATCH_RESULT_RECEIVED = 1
    BOT_ACTIVATION_STATUS_CHANGED = 2


class Event:
    TYPE = None


class MatchResultReceivedEvent(Event):
    TYPE = EventType.MATCH_RESULT_RECEIVED

    def __init__(self, result: Result):
        self.result = result


class BotActivationStatusChangedEvent(Event):
    TYPE = EventType.BOT_ACTIVATION_STATUS_CHANGED

    def __init__(self, bot: Bot):
        self.bot = bot


class EventManager:
    def __init__(self):
        self._EVENT_HANDLER_MAP = {
            EventType.MATCH_RESULT_RECEIVED: self._handle_match_result_received,
            EventType.BOT_ACTIVATION_STATUS_CHANGED: self._handle_bot_activation_status_changed
        }

    def broadcast_event(self, event: Event):
        try:
            self._EVENT_HANDLER_MAP[event.TYPE](event)
        except Exception as e:
            logger.error(f"Event broadcast for event type {event.TYPE.name} failed with the following error:"
                         + os.linesep + traceback.format_exc())

    def _handle_match_result_received(self, event: MatchResultReceivedEvent):
        if settings.POST_SUBMITTED_RESULTS_TO_ADDRESS and event.result.match.round is not None:
            post_result_to_discord_bot(event.result)

    # todo: change this to a generic bot updated event
    def _handle_bot_activation_status_changed(self, event: BotActivationStatusChangedEvent):
        pass


EVENT_MANAGER = EventManager()
