#!/usr/bin/env python
# coding: utf-8
'''Imports and Functions'''
import json
import pprint
import numpy as np
from pymongo import     MongoClient
from datetime import datetime
from dateutil.parser import parse
from datetime import *
from dateutil.relativedelta import *
import calendar
import time
from pymongo import     MongoClient
from operator import itemgetter, attrgetter

con = MongoClient()

#RouteName= "ISCON_PDPU_BusStopDetection"

def SaveInMongoFunction(RouteName,FileName,RecordType):
	'''
	input: Route name, file name, and record type variable
	output: None
	function: It extracts the records from the provided files and saves the extracted records into MongoDB database for further processing.
	'''
	#print("Started")
	InputAccelerationFile = open(FileName,'r')
	InputAccelerationString = InputAccelerationFile.read()
	InputAccelerationJSON = json.loads("["+InputAccelerationString+"]")
	
	for i in range(len(InputAccelerationJSON)):
		InitalGPSRecordJSON = json.loads(InputAccelerationJSON[i]["GPSRecord"])
		if(len(InitalGPSRecordJSON))!=2:
			break

	s,mod=divmod(float(InitalGPSRecordJSON["Time"]),1000)
	dateTimeOP=datetime.fromtimestamp(s).strftime('%d_%m_%Y__%H_%M_%S')
	
	CollectionExists = [LR for LR in con[RouteName]['TripsInfo'].find({'SingleTripInfo':RecordType+"."+dateTimeOP}).limit(1)]
	#CollectionExists=[]
	if len(CollectionExists)==0:
		addToMongo(RouteName,InputAccelerationJSON,dateTimeOP,RecordType)


def addToMongo(RouteName,InputAccelerationJSON,dateTimeOP,RecordType):
	'''
	input: The route name, accelerometer records, trip start time and record type information. 
	output: None
	function: It saves the accelerometer records into MongoDB database by applying JSON parsing on the string of accelerometer records.
	'''
	for i in range(len(InputAccelerationJSON)):
		LocationRecordString = InputAccelerationJSON[i]['GPSRecord']
		LocationRecordJSON = json.loads(LocationRecordString)
		
		#Time = float(LocationRecordJSON["Time"])
		
		LocationRecordDict = {}
		LocationRecordDict["Latitude"]=floatTry(LocationRecordJSON["Latitude"])
		LocationRecordDict["Longitude"]=floatTry(LocationRecordJSON["Longitude"])
		if(len(LocationRecordJSON)!=2):
			LocationRecordDict["Time"]=floatTry(LocationRecordJSON["Time"])
			LocationRecordDict["Speed"]=floatTry(LocationRecordJSON["Speed"])
			LocationRecordDict["Accuracy"]=floatTry(LocationRecordJSON["Accuracy"])
			Time = float(LocationRecordJSON["Time"])
		
		#pprint.pprint (LocationRecordDict)

		con[RouteName][RecordType+"."+dateTimeOP+".GPSRecord.Raw"].insert_one(LocationRecordDict)
		
		AccelerometerJSONArrayString = InputAccelerationJSON[i]['AccelerometerRecordArray']
		AccelerometerJSONArray = json.loads(AccelerometerJSONArrayString)
		#AccelerometerSegmentRecordList = [(A['x'],A['y'],A['z']) for A in AccelerometerJSONArray]
		
		for AccelerometerJSON in AccelerometerJSONArray:
			AccelerometerDict={}

			AccelerometerDict["Ax"] = floatTry(AccelerometerJSON["Ax"])
			AccelerometerDict["Ay"] = floatTry(AccelerometerJSON["Ay"])
			AccelerometerDict["Az"] = floatTry(AccelerometerJSON["Az"])

			AccelerometerDict["Mx"] = floatTry(AccelerometerJSON["Mx"])
			AccelerometerDict["My"] = floatTry(AccelerometerJSON["My"])
			AccelerometerDict["Mz"] = floatTry(AccelerometerJSON["Mz"])
			if(len(LocationRecordJSON)!=2):
		    
				AccelerometerDict["Time"] = Time
		    
			#pprint.pprint(AccelerometerDict)
			con[RouteName][RecordType+"."+dateTimeOP+".AcclMagData.Raw"].insert_one(AccelerometerDict)
		    
		#input()
	con[RouteName]['TripsInfo'].insert_one({'SingleTripInfo':RecordType+"."+dateTimeOP,'RawRecord':'True','SegmentExtracted':'False','ConvertedToEarthAxis':'False'})
		    
def floatTry (Record):
    '''
    input: record value in string data type
    output: record value of float data type
    function: It converts the string value of the record to the float data type.
    '''
    try:
        return(float(Record))
    except ValueError:
        return("NA") 
    #lambda Record: try: return(float(element)) except ValueError: return("Not a float")

def UpdateAccuracyAvgSTD(RouteName,SingleTripInfo):
	'''
	input: The route name and trip name
	output: None
	function: It updates the location records with the information of relative standard deviation of accuracy of GPS record in the MongoDB database. 
	'''
	LocationRecord = [LR for LR in con[RouteName][SingleTripInfo+".GPSRecord.Raw"].find()]
	AccuracyList = [LR["Accuracy"] for LR in LocationRecord if len(LR)!=3]
	AccuracyListNP = np.asarray(AccuracyList)

	meanAccuracy=np.mean(AccuracyListNP)
	stdAccuracy=np.std(AccuracyListNP)	

	RelativeSTDAccuracy = (stdAccuracy/meanAccuracy)*100

	
	con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':SingleTripInfo},{'$set':'meanAccuracy':meanAccuracy,'stdAccuracy':stdAccuracy,'RelativeSTDAccuracy':RelativeSTDAccuracy})
