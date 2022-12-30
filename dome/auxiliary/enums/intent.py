from enum import auto, Enum

from dome.config import INTENT_MAP


class AutoName(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self  # ==name


class Intent(AutoName):
    # "confirmation", "cancellation", "help", "greeting", "add", "delete", "read", "goodbye"
    ADD = auto()
    UPDATE = auto()
    DELETE = auto()
    GREETING = auto()
    READ = auto()
    GOODBYE = auto()
    HELP = auto()
    CANCELLATION = auto()
    CONFIRMATION = auto()
    MEANINGLESS = auto()

    def __str__(self):
        return self.name

    def getSynonyms(self) -> set:
        return INTENT_MAP[str(self)]

    @staticmethod
    def fromString(intent_str: str):
        for intent in Intent:
            if intent == intent_str:
                return intent
        # else
        return None

    def __eq__(self, another_intent: object) -> bool:
        return ((self.name == str(another_intent).upper()) or
                (str(another_intent).lower() in self.getSynonyms()))
