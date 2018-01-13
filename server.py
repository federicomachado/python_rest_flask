#!/usr/bin/python3
# -*- coding: cp1252 -*-
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_cors import CORS
from sqlalchemy import create_engine
from datetime import date, datetime
import pyodbc
import sqlite3
import urllib
import json, inspect
import getpass
import win32security
# pip install simplejson

class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

def initRegistryParser():
    parser = reqparse.RequestParser()
    parser.add_argument("order_id")
    parser.add_argument("firstWorker")
    parser.add_argument("secondWorker")
    parser.add_argument("meanTime")
    parser.add_argument("meanTimePerWorker")
    parser.add_argument("date")
    parser.add_argument("startTime")
    parser.add_argument("endTime")
    parser.add_argument("stopTime")
    parser.add_argument("realTime")
    parser.add_argument("timePerWorker")
    parser.add_argument("firstWorkerDesc")
    parser.add_argument("secondWorkerDesc")
    return parser

def initWorkerRegistryParser():
    parser = reqparse.RequestParser()
    parser.add_argument("workerName")
    parser.add_argument("workerNameDesc")
    parser.add_argument("orderQuantity")
    parser.add_argument("meanRate")
    parser.add_argument("faultCount")
    return parser

def initWorkerRegistryRateParser():
    parser = reqparse.RequestParser()
    parser.add_argument("workerName")
    parser.add_argument("rate")
    parser.add_argument("date")

    return parser

def initLoginParser():
    parser = reqparse.RequestParser()
    parser.add_argument("username")
    parser.add_argument("password")
    return parser

try:
    db_connect = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};DATABASE=KPUrusalWS;SERVER=ANTILSRV\SQLEXPRESS;PORT=1433;UID=FMACHADO;PWD=Fede1234')
    registryParser = initRegistryParser()
    workerRegistryParser = initWorkerRegistryParser()
    workerRegistryRatesParser = initWorkerRegistryRateParser()
    loginParser = initLoginParser()
    app = Flask(__name__)
    cors = CORS(app, resources={"*": {"origins": "*"}})
    db_sqlite3 = sqlite3.connect("entries.db")
    api = Api(app) 
except Exception as x:
    print x

class WorkerObj:

    def __init__(self, workerName, workerNameDesc, orderQuantity, meanRate,faultCount):
        self.workerName =workerName
        self.workerNameDesc = workerNameDesc
        self.orderQuantity = orderQuantity
        self.meanRate = meanRate
        self.faultCount = faultCount
        self.rateArray = []
        self.dateArray = []


    def __str__(self):
        s = ""
        z = ""
        for x in self.rateArray:
            s+= str(x)+" "
        for y in self.dateArray:
            z+= str(y)+" "
        return self.workerName+ "\n" + s + "\n" + z

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

class RegistryEntry(Resource):
    def get(self):
        try:
            cursor = db_sqlite3.cursor()
            cursor = cursor.execute("select * from entry;")
            columns = [column[0] for column in cursor.description]        
            results = []
            rows = cursor.fetchall()
            for row in rows:            
                dicc = dict(zip(columns,row))            
                results.append(dicc)
            return results
        except Exception as x:
            print x
        
    def post(self):
        args = registryParser.parse_args()        
        c = db_sqlite3.cursor()
        c.execute("""insert into entry values(?,?,?,?,?,?,?,?,?,?,?,?,?)""",(args["order_id"],args["firstWorker"],args["secondWorker"],args["meanTime"],args["meanTimePerWorker"],args["date"],args["startTime"],args["endTime"], args["stopTime"], args["realTime"],args["timePerWorker"],args["firstWorkerDesc"],args["secondWorkerDesc"]    ))
        db_sqlite3.commit()
        return args,201
        

class Order(Resource):
    def get(self):
        cursor = db_connect.cursor()
        cursor = cursor.execute("select p.OProId as 'Orden', p.OProArtId as 'Articulo', CAST(p.OProCant as CHAR) as 'Cantidad', p.OProObs as 'Observaciones', p.OProFchRea as 'Fecha'  from pordprod p \
                                      where p.OProFchRea >= '2015/01/06'\
                                      order by p.OProFchRea desc")
        columns = [column[0] for column in cursor.description]        
        results = []
        rows = cursor.fetchall()
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

class WorkerEntry(Resource):
    def get(self):        
        cursor = db_sqlite3.cursor()
        cursor = cursor.execute("select * from workerEntry inner join workerEntryRates ON workerEntry.workerName = workerEntryRates.workerName")
        columns = [column[0] for column in cursor.description]        
        results = []
        rows = cursor.fetchall()
        names = []
        workers = []
        dictionary = {}
        for row in rows:
##            print row
            dicc = dict(zip(columns,row))        
            results.append(dicc)
            if row[0] not in names:
                names.append(row[0])
                x = WorkerObj(row[0],row[1],row[2],row[3],row[4])
                x.rateArray.append(row[7])
                x.dateArray.append(row[8])
                workers.append(x)
            else:
                for w in workers:
                    w.rateArray.append(row[7])
                    w.dateArray.append(row[8])
        return json.dumps(workers, cls=ObjectEncoder, indent=2, sort_keys=True)
    
    def post(self):        
        args = workerRegistryParser.parse_args()
        c = db_sqlite3.cursor()
        c.execute(""" insert into workerEntry values(?,?,?,?,?) """,( args["workerName"],args["workerNameDesc"],args["orderQuantity"],args["meanRate"],args["faultCount"] ) )
        db_sqlite3.commit()        
        return args,201
    
    def put(self):
        args = workerRegistryParser.parse_args()
        c = db_sqlite3.cursor()
        c.execute(""" UPDATE workerEntry SET orderQuantity = ?, meanRate = ?, faultCount = ? WHERE workerName = ?   """,( args["orderQuantity"],args["meanRate"],args["faultCount"],args["workerName"] ) )
        db_sqlite3.commit()        
        return args,201
        
class WorkerEntryRate(Resource):
    def get(self):
        pass
    def post(self):
        args = workerRegistryRatesParser.parse_args()        
        c = db_sqlite3.cursor()
        c.execute(""" insert into workerEntryRates(workerName,rate,date) values(?,?,?) """, (args["workerName"],args["rate"],args["date"] ))
        db_sqlite3.commit()
        return args,201

class LoginCredentials(Resource):
    def get(self):
        pass
    def post(self):
        args = loginParser.parse_args()
        domain = "ANTIL"
        username =  args["username"]
        password = args["password"]
        try:
          hUser = win32security.LogonUser (
            username,
            domain,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT
          )
        except win32security.error:
          print "Failed"
          return "Login fallido",403
        else:
          print "Succeeded"
          return username,201

api.add_resource(ProductionTime, '/times') # Route_1
api.add_resource(Order, '/orders') # Route_2
api.add_resource(Worker, '/workers') # Route_3
api.add_resource(RegistryEntry, '/entries') # Route_3
api.add_resource(WorkerEntry, '/workerEntries') # Route_3
api.add_resource(WorkerEntryRate, '/workerEntriesRates') # Route_3
api.add_resource(LoginCredentials,"/login")

if __name__ == '__main__':
##    app.run(host="localhost",port=5000)
    #app.debug = True
    app.run(host="192.168.1.7",port=5000)


