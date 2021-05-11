#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 13:24:52 2021

@author: mdshadanaltmash
"""

from flask import Flask,jsonify,request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt

app=Flask(__name__)
api=Api(app)

####### MONGODB CONNECTION #########
client = MongoClient("ENTER YOUR MONGO CLIENT URL")
db = client.Mongo_Database_name     #Replace Mongo_Database_name with your db name
users=db["Collection_name"]         #Replace Collection_name with your collection name


def verifyPassword(username,password):
    hashedPass=users.find({
            "Username":username
        })[0]['Password']
    
    if bcrypt.checkpw(password.encode('utf8'), hashedPass):
        return True
    else:
        return False
    
def countTokens(username):
    tokenCount=users.find({
            "Username":username
        })[0]['Tokens']
    
    return tokenCount
    
        

class Register(Resource):
    def post(self):
        #get Data form user
        postedData=request.get_json()
        
        #get username and password
        username=postedData['username']
        password=postedData['password']
        
        hash_pass=bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        
        #store username and password in database
        users.insert({
            'Username':username,
            'Password':hash_pass,
            'Sentence':"",
            'Tokens':5
            })
        retjson={
            "Status":200,
            "Message":'You have successfully signed up for the API!!'
        }
        
        return jsonify(retjson)

class Store(Resource):
    def post(self):
        
        #get Data form user
        postedData=request.get_json()
        
        #get username and password
        username=postedData['username']
        password=postedData['password']
        sentence=postedData['sentence']
    
        
        #verify username and password maatch
        checkPass=verifyPassword(username,password)
        if not checkPass:
            retjson={
                    "Status":302,
                    "Message":"Credentials does not match or does not exist"
                }
            
            return jsonify(retjson)
        
        #verify he has enough tokens
        token_count=countTokens(username)
        if token_count<=0:
            retjson={
                    "Status":301,
                    "Message":"You do not have enough tokens"
                }
            
            return jsonify(retjson)
            
            
        
        #store the sentence 
        
        users.update({
            "Username":username
            },{
                '$set':{
                    'Sentence':sentence,
                    'Tokens':token_count-1
                    }
                })
                
        retjson={
            'Status':200,
            'Message':'Sentence Inserted Successfully'
            }
        return jsonify(retjson)
        
class Get(Resource):
    def post(self):
        
        #get Data form user
        postedData=request.get_json()
        
        #get username and password
        username=postedData['username']
        password=postedData['password']
       
        #verify username and password maatch
        checkPass=verifyPassword(username,password)
        if not checkPass:
            retjson={
                    "Status":302,
                    "Message":"Credentials does not match or does not exist"
                }
            
            return jsonify(retjson)
        
        #verify he has enough tokens
        token_count=countTokens(username)
        if token_count<=0:
            retjson={
                    "Status":301,
                    "Message":"You do not have enough tokens"
                }
            
            return jsonify(retjson)
        
        users.update({
            "Username":username
            },{
                '$set':{
                    'Tokens':token_count-1
                    }
                })
        
        
        sentence=users.find({
                'Username':username
            })[0]['Sentence']
        
        token=users.find({
                'Username':username
            })[0]['Tokens']
        
        retjson={
            'Status':200,
            'Sentence':sentence,
            'Token Remaining':token
            }
        
        return jsonify(retjson)
        


api.add_resource(Register,'/register')
api.add_resource(Store,'/store')
api.add_resource(Get, '/get')

if __name__=='__main__':
    app.run()


