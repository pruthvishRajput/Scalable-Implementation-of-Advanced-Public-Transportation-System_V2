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
SitStand =""
Position = ""

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

def CheckForGroundTruth(InputAccelerationJSONRecord):
	'''
	input: List of JSON dictonary objects.
	output: The flag indicating whether the ground truth data is available or not. The list of JSON dictonary objects with the information of the commuter's state and phone position is updated if the ground truth data is available.
	function: It checks whether the information of the commuter's state and phone position is available or not. Incase, if the information is available, it is updated in the provided list of dictionaries. 
	'''
	GroundTruthFlag = False
	for key in InputAccelerationJSONRecord:
		if key == "SitStand" or key =="Position":
			#print(key,InputAccelerationJSONRecord[key])
			#print(InputAccelerationJSONRecord["SitStand"],InputAccelerationJSONRecord["Position"])
			global SitStand
			global Position
			SitStand = 	InputAccelerationJSONRecord["SitStand"]
			Position = 	InputAccelerationJSONRecord["Position"]
			return(True)
	return(GroundTruthFlag)

def addToMongo(RouteName,InputAccelerationJSON,dateTimeOP,RecordType):
	'''
	input: The route name, accelerometer records, trip start time and record type information. 
	output: None
	function: It saves the accelerometer records into MongoDB database by applying JSON parsing on the string of accelerometer records.
	'''
	for i in range(len(InputAccelerationJSON)):
		GroundTruthFlag = CheckForGroundTruth(InputAccelerationJSON[i])
		if GroundTruthFlag == False:
			LocationRecordString = InputAccelerationJSON[i]['GPSRecord']
			LocationRecordJSON = json.loads(LocationRecordString)
			
			#Time = float(LocationRecordJSON["Time"])
			
			LocationRecordDict = {}
			LocationRecordDict["Latitude"]=floatTry(LocationRecordJSON["Latitude"])
			LocationRecordDict["Longitude"]=floatTry(LocationRecordJSON["Longitude"])
			LocationRecordDict["GPSIndex"]=i
			if(len(LocationRecordJSON)!=2):
				LocationRecordDict["Time"]=floatTry(LocationRecordJSON["Time"])
				LocationRecordDict["Speed"]=floatTry(LocationRecordJSON["Speed"])
				Speed = LocationRecordDict["Speed"]
				LocationRecordDict["Accuracy"]=floatTry(LocationRecordJSON["Accuracy"])
				Time = float(LocationRecordJSON["Time"])
			
			#pprint.pprint (LocationRecordDict)

			con[RouteName][RecordType+"."+dateTimeOP+".GPSRecord.Raw"].insert_one(LocationRecordDict)
			
			AccelerometerJSONArrayString = InputAccelerationJSON[i]['AccelerometerRecordArray']
			AccelerometerJSONArray = json.loads(AccelerometerJSONArrayString)
			#AccelerometerSegmentRecordList = [(A['x'],A['y'],A['z']) for A in AccelerometerJSONArray]
			
			for indexj in range(len(AccelerometerJSONArray)):
				AccelerometerDict={}

				AccelerometerDict["Ax"] = floatTry(AccelerometerJSONArray[indexj]["Ax"])
				AccelerometerDict["Ay"] = floatTry(AccelerometerJSONArray[indexj]["Ay"])
				AccelerometerDict["Az"] = floatTry(AccelerometerJSONArray[indexj]["Az"])

				AccelerometerDict["Mx"] = floatTry(AccelerometerJSONArray[indexj]["Mx"])
				AccelerometerDict["My"] = floatTry(AccelerometerJSONArray[indexj]["My"])
				AccelerometerDict["Mz"] = floatTry(AccelerometerJSONArray[indexj]["Mz"])
				
				AccelerometerDict["GPSIndex"]=i
				AccelerometerDict["AcclIndex"]=indexj

				if(len(LocationRecordJSON)!=2):
				
					AccelerometerDict["Time"] = Time
				
				#pprint.pprint(AccelerometerDict)
				
				for key in AccelerometerJSONArray[indexj]:
					if key == "Mode":
						AccelerometerDict["Mode"]=AccelerometerJSONArray[indexj][key]
				
				con[RouteName][RecordType+"."+dateTimeOP+".AcclMagData.Raw"].insert_one(AccelerometerDict)
				
			#input()
	
	global Position
	global SitStand
	
	#con[RouteName]['TripsInfo'].insert_one({'SingleTripInfo':RecordType+"."+dateTimeOP,'RawRecord':True,'SegmentExtracted':False,'ConvertedToEarthAxis':False,'AccuracyProcessed':False,'GMapProcessed':False})
	con[RouteName]['TripsInfo'].insert_one({'SingleTripInfo':RecordType+"."+dateTimeOP,'RawRecord':True,'SegmentExtracted':False,'ConvertedToEarthAxis':False,'AccuracyProcessed':False,'GMapProcessed':False,'SitStand':SitStand, 'Position':Position, 'RawExtracted':True, 'FeaturesExtracted':False, 'Filtered':False, 'TriggerMode':True})

	print(RecordType+"."+dateTimeOP)
	SitStand = ""
	Position = ""
	
	con[RouteName][RecordType+"."+dateTimeOP+".AcclMagData.Raw"].create_index('GPSIndex')

def GetMergeIndexInMongo(RouteName):
	'''
	input: The route name 
	output: None
	function: It extracts the GPS records, accelerometer reecords, and magnetometer records of the provided route and computes the merged index based on the GPSIndex and accelerometer index. 
	'''
	SingleTripsInfo = [LR['SingleTripInfo'] for LR 
		               in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})]
	for SingleTripInfo in SingleTripsInfo:
		print(SingleTripInfo)
		AcclMagRecord = [collection for collection in 
		                 con[RouteName][SingleTripInfo+'.AcclMagData.Raw'].find().sort([('GPSIndex',1)])]

		for Record in AcclMagRecord:
			Record['MergedIndex'] = Record['GPSIndex']
			Record['GPSIndex'] = Record['GPSIndex']+Record['AcclIndex']/100
	

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
	LocationRecord = [LR for LR in con[RouteName][SingleTripInfo+".GPSRecord.Raw"].find().sort([('Time',1)])]
	AccuracyList = [LR["Accuracy"] for LR in LocationRecord if len(LR)!=4]
	AccuracyListNP = np.asarray(AccuracyList)

	meanAccuracy=np.mean(AccuracyListNP)
	stdAccuracy=np.std(AccuracyListNP)	

	RelativeSTDAccuracy = (stdAccuracy/meanAccuracy)*100

	
	con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':SingleTripInfo},{'$set':{'meanAccuracy':meanAccuracy,'stdAccuracy':stdAccuracy,'RelativeSTDAccuracy':RelativeSTDAccuracy,'AccuracyProcessed':True}})

def SaveToTxtForGMaps(RouteName,SingleTripInfo,LocationRecords,FileName):
	'''
	input: The route name, trip name, trip records, and file name.
	output: The csv file containing the location records.
	function: It extract the location records from the file in form of JSON dictionary and saves it in form of csv format for importing the location records in the Google Maps.
	'''
	index = 0	
	#WriteFile = open(FileName+"_"+str(index)+".txt",'w')
	WriteFile = open(FileName+"_"+str(index)+".csv",'w')
	
	WriteFile.write("ts,lt,ln,ac,sp"+"\n")
	for i in range(len(LocationRecords)):
		s,mod=divmod(float(LocationRecords[i]["Time"]),1000)
		dateTimeOP=datetime.fromtimestamp(s).strftime('%d_%m_%Y__%H_%M_%S')
		LocationString = dateTimeOP+","+str(LocationRecords[i]["Latitude"])+","+str(LocationRecords[i]["Longitude"])+","+str(LocationRecords[i]["Accuracy"])+","+str(LocationRecords[i]["Speed"])+"\n"
	
		indexForWrite = int(i/1999)
		if indexForWrite!=index:
			index = indexForWrite
			WriteFile.close()
			#WriteFile = open(FileName+"_"+str(index)+".txt",'w')
			WriteFile = open(FileName+"_"+str(index)+".csv",'w')
			WriteFile.write("ts,lt,ln,ac,sp"+"\n")
		WriteFile.write(LocationString)
	
	WriteFile.close()
	con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':SingleTripInfo},{'$set':{'GMapProcessed':True}})
	
