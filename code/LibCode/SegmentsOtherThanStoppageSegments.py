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

def GetTripsBasedOnType(RouteName):
	'''
	input: The routename
	output: The trips for different transport mode
	function: It bifurcates the different trips based on transport mode.
	'''
	SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'SegmentExtracted':False})]
	'''For Separating BM, CM, and PD'''
	BMSingleTripsInfoList = []
	CMSingleTripsInfoList = []
	PDSingleTripsInfoList = []
	for index in range(len(SingleTripsInfo)):
		SingleTripInfoList = SingleTripsInfo[index].split(".")
		if(SingleTripInfoList[0]=="BM"):
			BMSingleTripsInfoList.append(SingleTripsInfo[index])
		elif(SingleTripInfoList[0]=="CM"):
			CMSingleTripsInfoList.append(SingleTripsInfo[index])
		else:
			PDSingleTripsInfoList.append(SingleTripsInfo[index])
	#print(BMSingleTripsInfoList)
	#print(CMSingleTripsInfoList)
	#print(PDSingleTripsInfoList)
	return(BMSingleTripsInfoList,CMSingleTripsInfoList,PDSingleTripsInfoList)

'''Segment other than stoppage'''
        
def GetBMAndPDSegments(RouteName,BMSingleTripsInfoList,StopSpeed,LowerSpeedLimit):
	'''
	input: The route name, trips list, range of speeds to extract the segment other than stoppage segments.
	output: None
	function: It extracts the segment other than stoppage segments and stores it in MongoDB
	'''
	
	for index in range(len(BMSingleTripsInfoList)):
		StoppageSegments= []

		LocationRecordsListStoppages =[LR for LR in con[RouteName][BMSingleTripsInfoList[index]+".GPSRecord.Raw"].find(  { 'Speed': { '$gte': LowerSpeedLimit } } ).sort([('Time',1)])]
		StartSegment = False
		#StoreSegment =False

		for indexj in range(len(LocationRecordsListStoppages)-1):
			if StartSegment== False  and LocationRecordsListStoppages[indexj]['Speed']>StopSpeed:
				StartSegment = True
				
				StartSegmentTimeValue = LocationRecordsListStoppages[indexj]["Time"]
				#print("StartSegment")
				#print(LocationRecordsListStoppages[indexj]['Time'],LocationRecordsListStoppages[indexj]['Speed'])
				#print(LocationRecordsListStoppages[indexj+1]['Time'],LocationRecordsListStoppages[indexj+1]['Speed'])
				#print(LocationRecordsListStoppages[indexj+1]["Time"],LocationRecordsListStoppages[indexj+1]["Latitude"],LocationRecordsListStoppages[indexj+1]["Longitude"],LocationRecordsListStoppages[indexj]["Accuracy"],LocationRecordsListStoppages[indexj+1]["Speed"])
			elif LocationRecordsListStoppages[indexj]['Speed']<StopSpeed and StartSegment == True:
				#print("StopSegment")
				#print(LocationRecordsListStoppages[indexj-1]['Time'],LocationRecordsListStoppages[indexj-1]['Speed'])
				#print(LocationRecordsListStoppages[indexj]['Time'],LocationRecordsListStoppages[indexj]['Speed'])
				
				StartSegment = False
				StopSegmentTimeValue = LocationRecordsListStoppages[indexj]["Time"]
				StoppageSegments.append([StartSegmentTimeValue,StopSegmentTimeValue])
				'''
				if StoreSegment==True:
				    print("Duration")
				    print((StopSegmentTimeValue-StartSegmentTimeValue)/(1000))
				    StoppageSegments.append([StartSegmentTimeValue,StopSegmentTimeValue])
				    StoreSegment =False
				
				#print(BMSingleTripsInfoList[index])
				    input()
				'''
				#input()
			'''
			if LocationRecordsListStoppages[indexj]['Speed']<1:
			    StoreSegment =True
			'''
		#pprint.pprint(StoppageSegments)
		con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':BMSingleTripsInfoList[index]},{'$set':{'StopSegments':StoppageSegments}})

def GetCMSegments(RouteName,CMSingleTripsInfoList,BMSingleTripsInfoList):
	'''
	input: The route name, trips list of Commuter Module (CM) and Bus Module (BM) devices, range of speeds to extract the segment other than stoppage segments.
	output: None
	function: It extracts the segment other than stoppage segments by mapping the timestamps of the BM and CM devices and using the GPS records of BM device due to low accuracy of CM dvice. The extracted segments are stored it in MongoDB.
	'''
	'''Find the BM trip corresponding to CM trip'''
	for index in range(len(CMSingleTripsInfoList)):
		#Time =[LR for LR in con[RouteName][CMSingleTripsInfoList[index]+".GPSRecord.Raw"].find({'Time':'$min'})]
		Time =[LR for LR in con[RouteName][CMSingleTripsInfoList[index]+".GPSRecord.Raw"].find({ 'Latitude': { '$ne': "NA" }  }).sort([('Time',1)]).limit(1)]
		#print(Time[0]['Time'])
		#print(CMSingleTripsInfoList[index])
		BMTimeList =[]
		for indexj in range(len(BMSingleTripsInfoList)):
			BMTimeRecord =[LR for LR in con[RouteName][BMSingleTripsInfoList[indexj]+".GPSRecord.Raw"].find({ 'Latitude': { '$ne': "NA" }  }).sort([('Time',1)]).limit(1)]
			#print(BMTimeRecord)
			BMTimeList.append(BMTimeRecord[0]['Time'])
		CompareTimeWithBMTripList = [abs(BMTimeList[i]-Time[0]['Time']) for i in range(len(BMTimeList))]
		#print(BMTimeList[CompareTimeWithBMTripList.index(min(CompareTimeWithBMTripList))])
		s,mod=divmod(BMTimeList[CompareTimeWithBMTripList.index(min(CompareTimeWithBMTripList))],1000)
		dateTimeOP=datetime.fromtimestamp(s).strftime('%d_%m_%Y__%H_%M_%S')
		
		StoppageSegments = [Segment for Segment in con[RouteName]['TripsInfo'].find({'SingleTripInfo':"BM.Bus."+dateTimeOP})]
		StoppageSegmentsList = StoppageSegments[0]['StopSegments']
		
		#print(StoppageSegments[0]['StopSegments'])
		StoppageSegmentsListCM =[[Segment[0]-2000,Segment[1]+2000] for Segment in StoppageSegmentsList] 
		#StoppageSegmentsListCM =[[Segment[0],Segment[1]] for Segment in StoppageSegmentsList] 
		                         
		#print(StoppageSegmentsListCM)
		#print("BM."+dateTimeOP)    
		
		con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':CMSingleTripsInfoList[index]},{'$set':{'StopSegments':StoppageSegmentsListCM}})
		
		#input()

def GetGPSAndAcclReadOfSegment(RouteName):
	'''
	input: The route name 
	output: None
	function: It extracts the accelerometer and GPS records for the segment other than stoppage segment and stores it in MongoDB.
	'''
	SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'SegmentExtracted':False})]
	
	for index in range(len(SingleTripsInfo)):
		StoppageSegments = [Segment for Segment in con[RouteName]['TripsInfo'].find({'SingleTripInfo':SingleTripsInfo[index]})]
		StoppageSegmentsList = StoppageSegments[0]['StopSegments']
		
		StopSegmentsGPSIndex=[]
		for indexj in range(len(StoppageSegmentsList)):
			LocationRecordsListStoppages =[LR for LR in con[RouteName][SingleTripsInfo[index]+".GPSRecord.Raw"].find({ '$and': [ { 'Time': { '$gte': StoppageSegmentsList[indexj][0] } }, { 'Time': {'$lte':StoppageSegmentsList[indexj][1]} } ] }).sort([('GPSIndex',1)])]
			if len(LocationRecordsListStoppages)!=0:
				
				for indexk in range(len(LocationRecordsListStoppages)):
				    del LocationRecordsListStoppages[indexk]['_id']
				con[RouteName][SingleTripsInfo[index]+".GPSRecord.Segment"].insert_many(LocationRecordsListStoppages)
				#print(StoppageSegmentsList[index][0],StoppageSegmentsList[index][1])
				#pprint.pprint(LocationRecordsListStoppages)
				#pprint.pprint(LocationRecordsListStoppages[0]["GPSIndex"])
				#pprint.pprint(LocationRecordsListStoppages[len(LocationRecordsListStoppages)-1]["GPSIndex"])
				
				LowerGPSIndex = LocationRecordsListStoppages[0]["GPSIndex"]
				UpperGPSIndex = LocationRecordsListStoppages[len(LocationRecordsListStoppages)-1]["GPSIndex"]

				StopSegmentsGPSIndex.append([LowerGPSIndex,UpperGPSIndex])
				
				AcclMagRecordsListStoppages =[AclR for AclR in con[RouteName][SingleTripsInfo[index]+".AcclMagData.Raw"].find({ '$and': [ { 'GPSIndex': { '$gte': LowerGPSIndex} }, { 'GPSIndex': {'$lte':UpperGPSIndex} } ] }).sort([('GPSIndex',1)])]
				#pprint.pprint(AcclMagRecordsListStoppages)
				for indexk in range(len(AcclMagRecordsListStoppages)):
				    del AcclMagRecordsListStoppages[indexk]['_id']
				con[RouteName][SingleTripsInfo[index]+".AcclMagData.Segment"].insert_many(AcclMagRecordsListStoppages)
				
			#input()
		con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':SingleTripsInfo[index]},{'$set':{'SegmentExtracted':True,'StopSegmentsGPSIndex':StopSegmentsGPSIndex}})
