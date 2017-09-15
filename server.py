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


class Employees(Resource):
    def get(self):
        #DSN=Urusal;Description=KP local;UID=sa;Trusted_Connection=Yes;APP=Python;WSID=FEDERICOH-PC;DATABASE=KPUrusalWS;Network=DBMSLPCN
       # conn = db_connect.connect() # connect to database
        cursor = db_connect.cursor()
        query = cursor.execute("select distinct a.PrdPesBru, a.PrdPesNet from ARTICULO a") # This line performs query and returns json result
        rows = cursor.fetchall()        
        return {'costs': [i[0] for i in rows]} # Fetches first column that is Employee ID
    
    def post(self):
        pass

    
class Tracks(Resource):
    def get(self):
        cursor = db_connect.cursor()
        query = cursor.execute("select distinct a.PrdPesBru, a.PrdPesNet from ARTICULO a") # This line performs query and returns json result
        rows = cursor.fetchall() 
        query = cursor.execute("select trackid, name, composer, unitprice from tracks;")
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

    
class Employees_Name(Resource):
    def get(self, employee_id):
        conn = db_connect.connect()
        query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)


api.add_resource(Employees, '/employees') # Route_1
api.add_resource(Tracks, '/tracks') # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     app.run()
