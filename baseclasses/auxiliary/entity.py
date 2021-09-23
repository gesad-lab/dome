from baseclasses.auxiliary.attribute import Attribute

class Entity: #TODO: #12 choose other name to differ from responseParse.entity
    def __init__(self, name):
        self.name = name
        self.__attributes = [] #TODO: #20 to change to set()
        #self.addAttribute('att0', 'str', True) #all entities need at least one attribute not null

    def getAttributes(self):
        return self.__attributes
    
    def addAttribute(self, name, type, notNull=False):
        new_att = Attribute(self, name, type, notNull)
        #if self.getAttributes().count(new_att) > 0:
        #    return None
        #else
        self.__attributes.append(new_att)
        
    def delAttribute(self, name):
        self.__attributes.remove(name)
        
    def __eq__(self, o: object) -> bool:
        if type(o) == type(''):
            return self.name == o
        elif type(o) == type(self):
            return self.name == o.name
        #else
        return False         
