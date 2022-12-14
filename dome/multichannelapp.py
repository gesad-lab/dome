from dome.auxiliary.constants import (OPR_APP_TELEGRAM_START)
from dome.securityengine import SecurityEngine


class MultiChannelApp:
    # initializing singleton static instances
    __instance = None

    def __init__(self):
        if MultiChannelApp.__instance is None:
            MultiChannelApp.__instance = self
            self.__SE = SecurityEngine(self)
            self.run_telegram()

    def run_telegram(self):
        return self.__SE.execute(OPR_APP_TELEGRAM_START)