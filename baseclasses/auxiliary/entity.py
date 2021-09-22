from baseclasses.auxiliary.attribute import Attribute

class Entity:
    def __init__(self, name):
        self.name = name
        self.__attributes = []
        #self.addAttribute('att0', 'str', True) #all entities need at least one attribute not null

    def getAttributes(self):
        return self.__attributes
    
    def addAttribute(self, name, type, notNull=False):
        self.__attributes.append(Attribute(self, name, type, notNull))
        
    def delAttribute(self, name):
        self.__attributes.remove(name)
