#!/usr/bin/python3
# -*- coding: cp1252 -*-
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from sqlalchemy import create_engine
from json import dumps
from datetime import date, datetime
import pyodbc
import urllib

print pyodbc.drivers()
db_connect = pyodbc.connect('DSN=test;UID=FMACHADO;PWD=Fede1234')
app = Flask(__name__)
cors = CORS(app, resources={"*": {"origins": "*"}})
api = Api(app)


class ProductionTime(Resource):
    def get(self):
        #DSN=Urusal;Description=KP local;UID=sa;Trusted_Connection=Yes;APP=Python;WSID=FEDERICOH-PC;DATABASE=KPUrusalWS;Network=DBMSLPCN
       # conn = db_connect.connect() # connect to database
        cursor = db_connect.cursor()
        cursor = cursor.execute("select a.ArtCodId as 'Articulo', a.PrdPesBru as 'Peso Bruto', a.PrdPesNet as 'Peso Neto' from ARTICULO a") # This line performs query and returns json result
        columns = [column[0] for column in cursor.description]
        print columns
        results = []
        rows = cursor.fetchall()
        contador = 0
        for row in rows:
                print "Row"
                dicc = dict(zip(columns,row))
                for k in dicc:
                    print k                
                dicc = json.dumps(dicc, indent=4, sort_keys=True, default=str)
                results.append(dicc)
                contador+=1
        return results
    
    def post(self):
        pass

class Order(Resource):
    def get(self):
        #DSN=Urusal;Description=KP local;UID=sa;Trusted_Connection=Yes;APP=Python;WSID=FEDERICOH-PC;DATABASE=KPUrusalWS;Network=DBMSLPCN
       # conn = db_connect.connect() # connect to database
        cursor = db_connect.cursor()
        cursor = cursor.execute("select top 10 p.OProId as 'Orden', p.OProArtId as 'Articulo', CAST(p.OProCant as CHAR) as 'Cantidad', p.OProObs as 'Observaciones', p.OProFchRea as 'Fecha'  from pordprod p order by p.OProFchRea desc")
        columns = [column[0] for column in cursor.description]
        print columns
        results = []
        rows = cursor.fetchall()
        contador = 0
        for row in rows:            
            if contador<10:
                print "Row"
                dicc = dict(zip(columns,row))
                dicc['Fecha'] =str(dicc['Fecha'])
               # dicc = dumps(dicc, indent=0, sort_keys=True, default=str)
                results.append(dicc)
                contador+=1                
        return results
    

api.add_resource(ProductionTime, '/times') # Route_1
api.add_resource(Order, '/orders') # Route_2


if __name__ == '__main__':
     app.run()
