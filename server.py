#!/usr/bin/python3
# -*- coding: cp1252 -*-
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import pyodbc
import urllib

print pyodbc.drivers()
db_connect = pyodbc.connect('DSN=test;UID=FMACHADO;PWD=Fede1234')
app = Flask(__name__)
api = Api(app)


class ProductionTime(Resource):
    def get(self):
        #DSN=Urusal;Description=KP local;UID=sa;Trusted_Connection=Yes;APP=Python;WSID=FEDERICOH-PC;DATABASE=KPUrusalWS;Network=DBMSLPCN
       # conn = db_connect.connect() # connect to database
        cursor = db_connect.cursor()
        cursor = cursor.execute("select * from ARTICULO a") # This line performs query and returns json result
        columns = [column[0] for column in cursor.description]
        print columns
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(columns,row)))
        return results
    
    def post(self):
        pass

class Order(Resource):
    def get(self):
        #DSN=Urusal;Description=KP local;UID=sa;Trusted_Connection=Yes;APP=Python;WSID=FEDERICOH-PC;DATABASE=KPUrusalWS;Network=DBMSLPCN
       # conn = db_connect.connect() # connect to database
        cursor = db_connect.cursor()
        cursor = cursor.execute("select * from podprod") # This line performs query and returns json result
        columns = [column[0] for column in cursor.description]
        print columns
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(columns,row)))
        return results
    

api.add_resource(ProductionTime, '/times') # Route_1
api.add_resource(Order, '/orders') # Route_2


if __name__ == '__main__':
     app.run()
