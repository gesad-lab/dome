from enum import auto, Enum

from dome.config import INTENT_MAP


class AutoName(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self  # ==name


class Intent(AutoName):
    # "confirmation", "cancellation", "help", "greeting", "save", "delete", "read", "goodbye"
    SAVE = auto()
    DELETE = auto()
    GREETING = auto()
    READ = auto()
    GOODBYE = auto()
    HELP = auto()
    CANCELLATION = auto()
    CONFIRMATION = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name

    def getSynonyms(self) -> list:
        return INTENT_MAP[str(self)]

    def __eq__(self, another_intent: object) -> bool:
        return ((self.name == str(another_intent).upper()) or
                (str(another_intent).lower() in self.getSynonyms()))
