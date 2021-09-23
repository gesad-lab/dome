from baseclasses.auxiliary.entity import Entity

class DomainEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
        self.__entities = []

    def addEntity(self, name):
        #TODO: update meta data (MDB) and Transaction Data (TDB)
        e = Entity(name)
        if self.__entities.count(name) == 0:
            self.__entities.append(e)
        return e

    def getEntities(self):
        return self.__entities

    def addAttribute(self, entity, name, type, notnull=False):
        #TODO: #2 update meta data (MDB) and Transaction Data (TDB)
        #...
        entity.addAttribute(name, type, notnull)
        return True
