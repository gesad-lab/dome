class Attribute:
    def __init__(self, entity, name, type, notNull=False):
        self.__entity = entity
        self.name = name
        self.type = type
        self.notnull = notNull
        
    def __eq__(self, o: object) -> bool:
        if type(o) == type(''):
            return self.name == o
        elif type(o) == type(self):
            return self.name == o.name
        #else
        return False 
