from dome.auxiliary.attribute import Attribute

class Entity: #TODO: #12 choose other name to differ from responseParse.entity
    def __init__(self, name):
        self.name = name
        self.__attributes = {}

    def getAttributes(self):
        return self.__attributes.values()
    
    def addAttribute(self, name, type, notNull=False):
        if name not in self.__attributes.keys():
            new_att = Attribute(self, name, type, notNull)
            self.__attributes[name] = new_att
        
    def delAttribute(self, name):
        if name in self.__attributes.keys():
            del self.__attributes[name]
        
    def __eq__(self, o: object) -> bool:
        if type(o) == type(''):
            return self.name == o
        elif type(o) == type(self):
            return self.name == o.name
        #else
        return False         
