#!/usr/bin/python3
# -*- coding: cp1252 -*-
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from sqlalchemy import create_engine
from datetime import date, datetime
import pyodbc
import urllib

# pip install simplejson

try:
    db_connect = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};DATABASE=KPUrusalWS;SERVER=ANTILSRV\SQLEXPRESS;PORT=1433;UID=FMACHADO;PWD=Fede1234')
    app = Flask(__name__)
    cors = CORS(app, resources={"*": {"origins": "*"}})
    api = Api(app) 
except Exception as x:
    print x


class ProductionTime(Resource):
    def get(self):
        cursor = db_connect.cursor()
        cursor = cursor.execute("select a.ArtCodId as 'Articulo', a.ArtDsc as 'Descripcion', a.PrdPesBru as 'TiempoEsperado', a.PrdPesNet as 'TiempoMaximo' from ARTICULO a") # This line performs query and returns json result
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()        
        for row in rows:
            l = list()
            for i in range(len(row)):
                l.append(row[i])
            l[2]=float(l[2])
            l[3]=float(l[3])   
            dicc = dict(zip(columns,l))                             
            results.append(dicc)                
        return results
    
    def post(self):
        pass

class Order(Resource):
    def get(self):
        cursor = db_connect.cursor()
        cursor = cursor.execute("select p.OProId as 'Orden', p.OProArtId as 'Articulo', CAST(p.OProCant as CHAR) as 'Cantidad', p.OProObs as 'Observaciones', p.OProFchRea as 'Fecha'  from pordprod p \
                                      where p.OProFchRea >= '2015/01/06'\
                                      order by p.OProFchRea desc")
        columns = [column[0] for column in cursor.description]        
        results = []
        rows = cursor.fetchall()
        contador = 0
        for row in rows:            
            dicc = dict(zip(columns,row))
            dicc['Fecha'] =str(dicc['Fecha'])
            results.append(dicc)
        return results
    
class Worker(Resource):
    def get (self):
        cursor = db_connect.cursor()
        cursor = cursor.execute("select * from CORENT c where c.AuxTpoId like 'FU'")
        columns = [column[0] for column in cursor.description]        
        results = []
        rows = cursor.fetchall()
        contador = 0
        for row in rows:            
            dicc = dict(zip(columns,row))        
            results.append(dicc)
        return results
        
        

api.add_resource(ProductionTime, '/times') # Route_1
api.add_resource(Order, '/orders') # Route_2
api.add_resource(Worker, '/workers') # Route_3


if __name__ == '__main__':
     app.run(host="192.168.1.7",port=5000)
