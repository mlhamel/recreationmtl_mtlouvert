#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
IMPORTANT : this is NOT completed, so it will likely not run.

TODO:

- use update instead of insert when pool_id already exists

author: Jolan Sergerie-Jeannotte

Creation date : 10 December 2011

"""


from fusiontables.authorization.clientlogin import ClientLogin
from fusiontables.sql.sqlbuilder import SQL
from fusiontables import ftclient
import datetime

# Main Documentaion
# =================


def connect_ft(username, password):
    """
    Connect to the fusion table API

    username -- google account username. (Ex : someone@gmail.com)
    password -- password to access the account.
    """

    token = ClientLogin().authorize(username, password)
    ft_client = ftclient.ClientLoginFTClient(token)
    return ft_client


# Gestion Pool Fusion Table
# -------------------------

class GestionPoolFusionTable():
    def __init__(self, ft_client):
        self.ft_client = ft_client

        #Table id and names of the columns in the FT of pools hours :
        self.hoursTableId = 2392546
        self.hoursId = "pool_id"
        self.hoursName = "pool_name"
        self.hoursAddresse = "pool_address"
        self.hoursSchedule = "schedule_text"
        self.hoursUpdateDate = "update_date"

    def addPoolHours(self, tableId, name, hours):
        """
        Add a pool and schedule to the table

        Given a table id, a pool name, and a schedule, add or update the data
        for the pool in the fusion table
        """

        # hours is simply a String.
        poolId, should_update = self.getPoolId(tableId, name)
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")

        data = {
                    'pool_id': poolId,
                    'pool_name': name,
                    'schedule_text': hours
               }

        if should_update:
            self.updatePool(tableId, data)
        else:
            self.insertRow(tableId, data)

    def getPoolId(self, tableId, name):
        """
        Get an id from the pool name.

        It will check if there's already the pool address
        in the table, if so, it will return the same id. If not, it will call
        generateIdGen(tableId).

        the function will return `id, True` if the pool already exists
        and `id, False` if it's a new pool
        """

        # Try to get the id of the pool from the given name
        sql = SQL().select(tableId, ["pool_id"],
                           "pool_name = '{}'".format(name))
        print sql
        result = self.ft_client.query(sql).split('\n')[1]

        # Check if the query returned an id
        if result:
            return int(result), True
        else:
            return self.generatePoolId(tableId), False

    def generatePoolId(self, tableId):
        """
        Create a new id for the pool

        Given a table id, find the maximum pool
        id in the table and return id + 1
        """

        sql = 'SELECT pool_id FROM {} ORDER BY pool_id DESC'.format(tableId)
        result = self.ft_client.query(sql).split('\n')[1]

        return int(result) + 1

    def updatePool(self, tableId, data):
        """
        Update the data for a pool which is already in the table.
        """

        row_id = self.ft_client.query(SQL().select(tableId, ["ROWID"],
                         "pool_id = {}".format(data["pool_id"])))
        row_id = int(row_id.split('\n')[1])

        sql = SQL().update(tableId, data, row_id=row_id)
        self.ft_client.query(sql)

    def insertRow(self, tableId, data):
        """
        Insert a pool in the table.
        Data is a dict with this form : `{'columnName': dataToInsert}`

        Example :
            {
                'pool_id': 12,
                'pool_name': 'Piscine Quintal',
                'schedule_text': {
                    "Lundi": "9h00 à 18h00,
                    "Mardi": "10h00 à 15h00"
                }
            }
        """

        sql = SQL().insert(tableId, data)
        print sql
        result = self.ft_client.query(sql)
        rowId = int(result.split("\n")[1])
        return rowId


# Main
# -------------------------

if __name__ == "__main__":

    import getpass
    #Nom d'usager Google (exemple : cpu.gastronomy@gmail.com)
    username = raw_input('user name: ') or "ph.mongeau@gmail.com"
    #Mot de passe du compte
    password = getpass.getpass("Enter your password: ")
    connection = connect_ft(username, password)

    gestion = GestionPoolFusionTable(connection)

    gestion.addPoolHours(2444117,
                         "Piscine du Complexe sportif Claude-Robillard",
                         "jeudi-vendredi: 10h00 a 20h00")
    gestion.addPoolHours(2444117,
                         "Une autre piscine",
                         "jeudi-vendredi: 11h00 a 22h00")
