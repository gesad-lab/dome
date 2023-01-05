from dome.auxiliary.entity import Entity
import sqlite3
import pandas as pd

from dome.config import LIMIT_REGISTERS


class DomainEngine:
    def __init__(self, AC):
        self.__AC = AC  # Autonomous Controller Object
        self.__TDB = None  # Transaction Database Connection
        self.__entities_map = {}  # map of entities
        # update table names
        sql_cmd = "SELECT name FROM sqlite_schema WHERE type ='table' AND name LIKE '" + self.__getEntityDBNamePrefix() + "%';"
        query = self.__executeSqlCmd(sql_cmd)
        for row in query.fetchall():
            entity_name = row[0].replace(self.__getEntityDBNamePrefix(), '')
            entity_obj = self.saveEntity(entity_name)
            # getting attributes
            sql_cmd = "SELECT name FROM PRAGMA_TABLE_INFO('" + row[0] + "') where name<>'id';"  # TODO: manage id
            query2 = self.__executeSqlCmd(sql_cmd)
            for col_name in query2.fetchall():
                entity_obj.addAttribute(col_name[0], 'string', False)  # TODO: manage type and notnull

    def saveEntity(self, entity_name):
        # TODO: update meta data (MDB) and Transaction Data (TDB)
        # if entity already exists, return the object from map
        if self.entityExists(entity_name):
            return self.__entities_map.get(entity_name)
        # else
        # create new entity
        e = Entity(entity_name)
        # add entity in map
        self.__entities_map[entity_name] = e
        # return entity
        return e

    def getEntities(self):
        return list(self.__entities_map.values())

    def get_entities_map(self):
        return self.__entities_map

    def addAttribute(self, entity, name, type, notnull=False):
        # TODO: #2 update meta data (MDB) and Transaction Data (TDB)
        # ...
        entity.addAttribute(name, type, notnull)
        return True

    def entityExists(self, entity_name):
        return entity_name in self.__entities_map.keys()

    def __executeSqlCmd(self, sqlCmd):
        if self.__TDB is None:
            self.__TDB = sqlite3.connect(self.__AC.getTransactionDB_path(), check_same_thread=False)
        result = self.__TDB.cursor().execute(sqlCmd)
        self.__TDB.commit()
        return result

    def __getEntityDBName(self, entity_name):
        return self.__getEntityDBNamePrefix() + entity_name

    def __getEntityDBNamePrefix(self):
        return self.__AC.getWebApp_path() + '_'

    def add(self, entity, attributes):
        sql_cmd = "INSERT OR REPLACE INTO " + self.__getEntityDBName(entity)
        sql_cmd += "(dome_created_at, dome_updated_at, "
        for k in attributes.keys():
            sql_cmd += k + ", "
        sql_cmd = sql_cmd[:-2]  # removing the last comma
        sql_cmd += ") values((datetime('now', 'localtime')), (datetime('now', 'localtime')), "
        for v in attributes.values():
            sql_cmd += "'" + str(v) + "', "
        sql_cmd = sql_cmd[:-2]  # removing the last comma
        sql_cmd += ")"
        self.__executeSqlCmd(sql_cmd)

    def update(self, entity, attributes, where_clause):
        sql_cmd = "UPDATE " + self.__getEntityDBName(entity) + " SET"
        sql_cmd += " dome_updated_at = (datetime('now', 'localtime')),"
        for attribute_name, attribute_value in attributes.items():
            sql_cmd += ' ' + attribute_name + "='" + attribute_value + "',"
        sql_cmd = sql_cmd[:-1]  # removing the last comma
        # fill-up the where clause
        if where_clause:
            sql_cmd += " where "
            for k in where_clause.keys():
                sql_cmd += "LOWER(" + k + ") LIKE LOWER('%" + where_clause[k] + "%') AND "
            sql_cmd = sql_cmd[:-4]  # removing the last AND

        self.__executeSqlCmd(sql_cmd)

    def read(self, entity, attributes):
        sql_cmd = "SELECT * FROM " + self.__getEntityDBName(entity) + " where (1=1)"
        for k in attributes.keys():
            sql_cmd += " AND LOWER(" + k + ") LIKE LOWER('%" + attributes[k] + "%')"

        # ordering by the newest
        # dome_updated_at is a reserved field automatically updated by the system
        sql_cmd += " ORDER BY dome_updated_at DESC"
        # put limit to LIMIT_REGISTERS
        sql_cmd += " LIMIT " + str(LIMIT_REGISTERS)

        query = self.__executeSqlCmd(sql_cmd)
        cols = [column[0] for column in query.description]
        data = query.fetchall()
        if len(data) == 0:
            return None
        # else
        results = pd.DataFrame.from_records(data=data, columns=cols, index=['id'])
        results.drop(['dome_created_at', 'dome_updated_at'], axis=1, inplace=True)
        return results

    def delete(self, entity, attributes):
        sql_cmd = "DELETE FROM " + self.__getEntityDBName(entity) + " where "
        for k in attributes.keys():
            sql_cmd += "LOWER(" + k + ") LIKE LOWER('%" + attributes[k] + "%') AND "
        sql_cmd = sql_cmd[:-4]  # removing the last AND
        return self.__executeSqlCmd(sql_cmd)
