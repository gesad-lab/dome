from text2system.auxiliary.entity import Entity
import sqlite3
import pandas as pd

class DomainEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
        self.__TDB = None #Transaction Database Connection
        self.__entities_map = {} #map of entities        
        #update table names
        sqlCmd = "SELECT name FROM sqlite_schema WHERE type ='table' AND name LIKE '" + self.__getEntityDBNamePrefix() + "%';"
        query = self.__executeSqlCmd(sqlCmd)
        for row in query.fetchall():
            entity_name = row[0].replace(self.__getEntityDBNamePrefix(),'')
            entity_obj = Entity(entity_name)
            #gettting attributes
            sqlCmd = "SELECT name FROM PRAGMA_TABLE_INFO('" + row[0] + "') where name<>'id';" #TODO: manage id
            query2 = self.__executeSqlCmd(sqlCmd)            
            for col_name in query2.fetchall():
                entity_obj.addAttribute(col_name[0], 'string', False) #TODO: manage type and notnull
            
            self.__entities_map[entity_name] = entity_obj
            

                
    def saveEntity(self, entity_name):
        #TODO: update meta data (MDB) and Transaction Data (TDB)
        #if entity already exists, return the object from map
        if self.entityExists(entity_name):
            return self.__entities_map.get(entity_name)
        #else
        #create new entity
        e = Entity(entity_name)
        #save entity in map
        self.__entities_map[entity_name] = e
        #return entity
        return e

    def getEntities(self):
        return list(self.__entities_map.values())

    def addAttribute(self, entity, name, type, notnull=False):
        #TODO: #2 update meta data (MDB) and Transaction Data (TDB)
        #...
        entity.addAttribute(name, type, notnull)
        return True
    
    def entityExists(self, entity_name):
        return self.__entities_map.get(entity_name) is not None
    
    def __executeSqlCmd(self, sqlCmd):
        if self.__TDB is None:
            self.__TDB = sqlite3.connect(self.__AC.getTransactionDB_path(), check_same_thread=False)
        result = self.__TDB.cursor().execute(sqlCmd)
        self.__TDB.commit()
        return result
        
    def __getEntityDBName(self, entityname):
        return self.__getEntityDBNamePrefix() + entityname
        
    def __getEntityDBNamePrefix(self):
        return self.__AC.getWebApp_path() + '_'
    
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
        sqlCmd = "SELECT * FROM " + self.__getEntityDBName(entity) + " where (1=1)" 
        for k in attributes.keys():
            sqlCmd += " AND LOWER(" + k + ") LIKE LOWER('%" + attributes[k] + "%')"

        query = self.__executeSqlCmd(sqlCmd)
        cols = [column[0] for column in query.description]
        data = query.fetchall()
        if len(data)==0:
            return None
        #else
        return pd.DataFrame.from_records(data = data, columns = cols, index=['id'])
            
    def delete(self, entity, attributes):
        sqlCmd = "DELETE FROM " + self.__getEntityDBName(entity) + " where " 
        for k in attributes.keys():
            sqlCmd += "LOWER(" + k + ") LIKE LOWER('%" + attributes[k] + "%') AND "
        sqlCmd = sqlCmd[:-4] #removing the last AND
        return self.__executeSqlCmd(sqlCmd)


        
           
        