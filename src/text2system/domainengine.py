from auxiliary.entity import Entity
import sqlite3
import pandas as pd

class DomainEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
        self.__entities = []
        self.__TDB = None #Transaction Database Connection

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
    
    def __executeSqlCmd(self, sqlCmd):
        if self.__TDB is None:
            self.__TDB = sqlite3.connect(self.__AC.getTransactionDB_path())
        result = self.__TDB.cursor().execute(sqlCmd)
        self.__TDB.commit()
        return result
        
    def __getEntityDBName(self, entityname):
        return self.__AC.getWebApp_path() + '_' + entityname
        
    def save(self, entity, attributes):
        sqlCmd = "INSERT OR REPLACE INTO " + self.__getEntityDBName(entity) + "(" 
        for k in attributes.keys():
            sqlCmd += k + ", "
        sqlCmd = sqlCmd[:-2] #removing the last comma
        sqlCmd += ") values(" 
        for v in attributes.values():
            sqlCmd += "'" + str(v) + "', " 
        sqlCmd = sqlCmd[:-2] #removing the last comma
        sqlCmd += ")"
        self.__executeSqlCmd(sqlCmd)
        
    def read(self, entity, attributes):
        sqlCmd = "SELECT * FROM " + self.__getEntityDBName(entity) + " where " 
        for k in attributes.keys():
            sqlCmd += "LOWER(" + k + ") LIKE LOWER('%" + attributes[k] + "%') AND "
        sqlCmd = sqlCmd[:-4] #removing the last comma
        query = self.__executeSqlCmd(sqlCmd)
        cols = [column[0] for column in query.description]
        return pd.DataFrame.from_records(data = query.fetchall(), columns = cols, index=['id'])
            


        
           
        