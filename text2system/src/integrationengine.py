from text2system.src.externalservice import ExternalService

class IntegrationEngine:
    def __init__(self, SE):
        self.__SE = SE
        self.ES = ExternalService(self)
