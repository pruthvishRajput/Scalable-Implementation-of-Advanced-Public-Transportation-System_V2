#!/usr/bin/python
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
import math

con = MongoClient()

def LPFFunction(XMovementList,YMovementList,ZMovementList,alpha):
	'''
	input: The X, Y, Z axis records and alpha variable
	output: The low pass filtered X, Y, Z axis records
	function: It applies the low pass filtering on the X, Y, Z axis records with the given alpha value
	'''

	XMovementFilteredList = []
	YMovementFilteredList = []
	ZMovementFilteredList = []

	XMovementFilteredList.append(XMovementList[0])
	YMovementFilteredList.append(YMovementList[0])
	ZMovementFilteredList.append(ZMovementList[0])

	#alpha = 0.135695765

	for index in range(1,len(ZMovementList)):
		XMovementFilteredList.append(XMovementFilteredList[index-1]+alpha * (XMovementList[index]-XMovementFilteredList[index-1]))
		#print(XMovementFilteredList[index],XMovementFilteredList[index-1],XMovementList[index],XMovementList[index-1])
		#input()
		YMovementFilteredList.append(YMovementFilteredList[index-1]+alpha * (YMovementList[index]-YMovementFilteredList[index-1]))
		ZMovementFilteredList.append(ZMovementFilteredList[index-1]+alpha * (ZMovementList[index]-ZMovementFilteredList[index-1]))

	return(XMovementFilteredList, YMovementFilteredList, ZMovementFilteredList)	

def HPFFunction(XMovementList, YMovementList, ZMovementList, alpha):
	'''
	input: The X, Y, Z axis records and alpha variable
	output: The high pass filtered X, Y, Z axis records
	function: It applies the high pass filtering on the X, Y, Z axis records with the given alpha value
	'''

	XMovementHPFFilteredList = []
	YMovementHPFFilteredList = []
	ZMovementHPFFilteredList = []

	XMovementHPFFilteredList.append(XMovementList[0])
	YMovementHPFFilteredList.append(YMovementList[0])
	ZMovementHPFFilteredList.append(ZMovementList[0])

	#alpha = 0.135695765

	for index in range(1,len(ZMovementList)):
		XMovementHPFFilteredList.append(alpha*(XMovementHPFFilteredList[index-1]+XMovementList[index]-XMovementList[index-1]))
		#print(XMovementFilteredList[index],XMovementFilteredList[index-1],XMovementList[index],XMovementList[index-1])
		#input()
		YMovementHPFFilteredList.append(alpha*(YMovementHPFFilteredList[index-1]+YMovementList[index]-YMovementList[index-1]))
		ZMovementHPFFilteredList.append(alpha*(ZMovementHPFFilteredList[index-1]+ZMovementList[index]-ZMovementList[index-1]))

	return(XMovementHPFFilteredList,YMovementHPFFilteredList,ZMovementHPFFilteredList)

def GetGravity(XLinearList, YLinearList, ZLinearList,XList, YList, ZList):
	'''
	input: The X, Y, Z axis raw accelerometer records and linear acceleration records
	output: The gravity value for X, Y, and Z axis
	function: It computes the gravity records for X, Y, and Z axis using raw accelerometer records and linear accelerometer records of each axis
	'''

	XGravityList =[XList[i] - XLinearList[i] for i in range(len(XList))]
	YGravityList =[YList[i] - YLinearList[i] for i in range(len(YList))]
	ZGravityList =[ZList[i] - ZLinearList[i] for i in range(len(ZList))]
	
	GravityMag = [math.sqrt(XGravityList[i]*XGravityList[i]+YGravityList[i]*YGravityList[i]+ZGravityList[i]*ZGravityList[i]) for i in range (len(ZList))]
	#return(XGravityList, YGravityList, ZGravityList)
	return(XGravityList, YGravityList, ZGravityList,GravityMag)


def GetEarthAxis(XLinearList, YLinearList, ZLinearList,XGravityList, YGravityList, ZGravityList,MagRecordInListX, MagRecordInListY, MagRecordInListZ):
	'''
	input: The X, Y, Z axis linear acceleration records, gravity records, and magnitude of the accelerometer records. 
	output: The three dimensional acceleremoter records along the earth axis
	function: It computes the orientation independent three dimensional accelerometer records along the earth axis using the linear acceleration records, gravity records, and magnitude of the accelerometer records.
	'''

	EAcclRecordInListX = []
	EAcclRecordInListY = []
	EAcclRecordInListZ = []
	InverseRmatrixList =[]
	for index in range(len(ZGravityList)):
		Gravity = [XGravityList[index],YGravityList[index],ZGravityList[index]]
		Linear =  [XLinearList[index],YLinearList[index],ZLinearList[index]]
		MagData = [MagRecordInListX[index],MagRecordInListY[index],MagRecordInListZ[index]]
		
		GravityNp = np.asarray(Gravity)
		LinearNp = np.asarray(Linear)
		MagDataNp = np.asarray(MagData)
		
		EastVector = np.cross(MagDataNp,GravityNp)
		NorthVector = np.cross(GravityNp,EastVector)
		
		GravityNorm = np.linalg.norm(GravityNp)
		EastVectorNorm = np.linalg.norm(EastVector)
		NorthVectorNorm = np.linalg.norm(NorthVector)
		
		if(GravityNorm!=0 and EastVectorNorm!=0 and NorthVectorNorm!=0):
			GravityNormalize = GravityNp/GravityNorm
			EastVectorNormalize = EastVector/EastVectorNorm
			NorthVectorNormalize = NorthVector/NorthVectorNorm


			InverseRmatrix = np.full((3,3),np.inf,dtype=float)

			InverseRmatrix[0][0] = EastVectorNormalize[0]
			InverseRmatrix[0][1] = EastVectorNormalize[1]
			InverseRmatrix[0][2] = EastVectorNormalize[2]

			InverseRmatrix[1][0] = NorthVectorNormalize[0]
			InverseRmatrix[1][1] = NorthVectorNormalize[1]
			InverseRmatrix[1][2] = NorthVectorNormalize[2]

			InverseRmatrix[2][0] = GravityNormalize[0]
			InverseRmatrix[2][1] = GravityNormalize[1]
			InverseRmatrix[2][2] = GravityNormalize[2]
			'''
			EAcclRecordInListX = InverseRmatrix[0][0] * Linear[0] + InverseRmatrix[0][1] * Linear[1] + InverseRmatrix[0][2] * Linear[2]
			EAcclRecordInListY = InverseRmatrix[1][0] * Linear[0] + InverseRmatrix[1][1] * Linear[1] + InverseRmatrix[1][2] * Linear[2]
			EAcclRecordInListZ = InverseRmatrix[2][0] * Linear[0] + InverseRmatrix[2][1] * Linear[1] + InverseRmatrix[2][2] * Linear[2]
			'''
			EAcclRecordInListX.append(InverseRmatrix[0][0] * Linear[0] + InverseRmatrix[0][1] * Linear[1] + InverseRmatrix[0][2] * Linear[2])
			EAcclRecordInListY.append(InverseRmatrix[1][0] * Linear[0] + InverseRmatrix[1][1] * Linear[1] + InverseRmatrix[1][2] * Linear[2])
			EAcclRecordInListZ.append(InverseRmatrix[2][0] * Linear[0] + InverseRmatrix[2][1] * Linear[1] + InverseRmatrix[2][2] * Linear[2])

			InverseRmatrixList.append(InverseRmatrix)
		    
		else:
			InverseRmatrixList.append(np.full((3,3),0,dtype=float))
			EAcclRecordInListX.append(0)
			EAcclRecordInListY.append(0)
			EAcclRecordInListZ.append(0)
		    
	return(EAcclRecordInListX, EAcclRecordInListY, EAcclRecordInListZ, InverseRmatrixList)
#def GetLinearAndGravityAcc (AcclMagRecordsListStoppages):
def ProcessEarthaxisAcceleration (RouteName,SingleTripInfo,AcclMagRecordsListStoppages):
	'''
	input: The trip name, route name, and accelerometer records
	output: The orientation independent accelerometer records along the earth axis
	function: It extracts the raw X, Y, and Z axis acceleration records and computes the orientation independent accelerometer records along the earth axis using the gravity and linear acceleration. 
	'''
	AcclRecordInListX = [AclR['Ax'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListY = [AclR['Ay'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListZ = [AclR['Az'] for AclR in AcclMagRecordsListStoppages]

	MagRecordInListX = [AclR['Mx'] for AclR in AcclMagRecordsListStoppages]
	MagRecordInListY = [AclR['My'] for AclR in AcclMagRecordsListStoppages]
	MagRecordInListZ = [AclR['Mz'] for AclR in AcclMagRecordsListStoppages]
	#pprint.pprint(AcclRecordInList)
	pi = 3.14159265359
	sampleDuration = 1/40
	'''LPF Filtered Data'''
	fc = 1
	alpha = 2* pi * sampleDuration * fc / (2* pi * sampleDuration * fc+1)
	alphaLinear = alpha

	XList, YList, ZList = LPFFunction(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ,alpha)
	#pprint.pprint(AcclRecordInListLPFFiltered)

	alpha = 0.9
	#alpha = 0.99  # 200 pts delay
	XLinearList, YLinearList, ZLinearList = HPFFunction(XList, YList, ZList,alpha)
	XLinearList, YLinearList, ZLinearList = LPFFunction(XLinearList, YLinearList, ZLinearList,alphaLinear)

	XGravityList, YGravityList, ZGravityList,GravityMag =  GetGravity(XLinearList, YLinearList, ZLinearList,XList, YList, ZList)

	#pprint.pprint(len(XGravityList))


	EAcclRecordInListX, EAcclRecordInListY, EAcclRecordInListZ, InverseRmatrix = GetEarthAxis(XLinearList, YLinearList, ZLinearList,XGravityList, YGravityList, ZGravityList,MagRecordInListX, MagRecordInListY, MagRecordInListZ)
	#pprint.pprint(len(AcclMagRecordsListStoppages))
	#pprint.pprint(len(EAcclRecordInListZ))
	#Same for single value
	for index in range(len(AcclMagRecordsListStoppages)):
		EarthDict = {}
		EarthDict['GPSIndex'] = AcclMagRecordsListStoppages[index]['GPSIndex']
		EarthDict['AcclIndex'] = AcclMagRecordsListStoppages[index]['AcclIndex']  # check
		EarthDict['Ex'] = EAcclRecordInListX[index]
		EarthDict['Ey'] = EAcclRecordInListY[index]
		EarthDict['Ez'] = EAcclRecordInListZ[index]
		EarthDict['InverseRmatrix'] = InverseRmatrix[index].tolist()
		#pprint.pprint(EarthDict)
		con[RouteName][SingleTripInfo+".EAcc"].insert_one(EarthDict)

#def GetLinearAndGravityAcc (AcclMagRecordsListStoppages):
def GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ,IntervalLength):

	'''
	input: X, Y, and Z axis accelerometer records
	output: The horizontal and vertical components of the accelerometer records
	function: It computes the horizontal and vertical components of the accelerometer records
	'''

	#IntervalLength = 160 #4 sec

	TotalPoint = math.ceil(len(AcclRecordInListX)/IntervalLength)

	HorizontalComponentList = []
	VerticalComponentList = []
	GravityComponentList =[]
	#AcclList =[]
	#print(len(AcclRecordInListX))
	#print(TotalPoint)
	#AcclLen = 0
	for index in range (TotalPoint):
		if index !=TotalPoint-1:
		    #print(index * IntervalLength , index * IntervalLength+IntervalLength-1)
		    AcclRecordInIntervalX = AcclRecordInListX[index * IntervalLength : index * IntervalLength+IntervalLength]
		    AcclRecordInIntervalY = AcclRecordInListY[index * IntervalLength : index * IntervalLength+IntervalLength]
		    AcclRecordInIntervalZ = AcclRecordInListZ[index * IntervalLength : index * IntervalLength+IntervalLength]
		#'''
		else:
		    #print("Got Here: ")
		    AcclRecordInIntervalX = AcclRecordInListX[index * IntervalLength : ]
		    AcclRecordInIntervalY = AcclRecordInListY[index * IntervalLength : ]
		    AcclRecordInIntervalZ = AcclRecordInListZ[index * IntervalLength : ]
		    #print(index * IntervalLength , len(AcclRecordInIntervalZ))
		#''' 
		AcclRecordInIntervalXNp = np.asarray (AcclRecordInIntervalX)
		AcclRecordInIntervalYNp = np.asarray (AcclRecordInIntervalY)
		AcclRecordInIntervalZNp = np.asarray (AcclRecordInIntervalZ)
		
		AcclRecordInIntervalXMean = np.mean(AcclRecordInIntervalXNp)
		AcclRecordInIntervalYMean = np.mean(AcclRecordInIntervalYNp)
		AcclRecordInIntervalZMean = np.mean(AcclRecordInIntervalZNp)
		
		Gravity = [AcclRecordInIntervalXMean,AcclRecordInIntervalYMean,AcclRecordInIntervalZMean]
		
		#AcclLen +=len(AcclRecordInIntervalX)
		#print(AcclLen)
		#input()
		for indexj in range(len(AcclRecordInIntervalX)):
			Accl = [AcclRecordInIntervalX[indexj],AcclRecordInIntervalY[indexj],AcclRecordInIntervalZ[indexj]]
			
			VerticalComponent = np.dot(Accl,Gravity)
			VerticalComponentInGravityDirection = [VerticalComponent * G for G in Gravity]
			
			HorizontalComponentVector = [Accl[i]-VerticalComponentInGravityDirection[i] for i in range(3)]
			
			HorizontalComponent = np.linalg.norm(HorizontalComponentVector)

			VerticalComponentList.append(VerticalComponent)
			HorizontalComponentList.append(HorizontalComponent)
			
			GravityComponentList.append(Gravity)
			#AcclList.append(Accl)
	#return(HorizontalComponentList,VerticalComponentList,AcclLen)
	return(HorizontalComponentList,VerticalComponentList,GravityComponentList)



#def GetLinearAndGravityAcc (AcclMagRecordsListStoppages):
def ProcessEarthaxisHVComponentUsingJigSawMethod (RouteName,SingleTripInfo,AcclMagRecordsListStoppages,IntervalLength,NameToRecord):
	'''
	input:  The trip name, route name, accelerometer records, and record type variable
	output: None
	function: It utilizes the Jigsaw paper based method for computing the horizontal and vertical components of the acceleration and saves it in the MongoDB
	'''
	AcclRecordInListX = [AclR['Ax'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListY = [AclR['Ay'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListZ = [AclR['Az'] for AclR in AcclMagRecordsListStoppages]

	#pprint.pprint(AcclRecordInList)

	HorizontalComponentList,VerticalComponentList,GravityComponentList = GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ,IntervalLength)
	''' For Speed, Lat and Lon'''
	PreviousGPSIndex = -1
	#pprint.pprint(len(AcclRecordInListX))
	#pprint.pprint(len(AcclList))
	#pprint.pprint(AcclList)

	for index in range(len(AcclMagRecordsListStoppages)):
		#Speed = "NA"
		HaveGPSRecord = False
		EarthDict = {}
		EarthDict['GPSIndex'] = AcclMagRecordsListStoppages[index]['GPSIndex']
		EarthDict['AcclIndex'] = AcclMagRecordsListStoppages[index]['AcclIndex']  # check

		EarthDict['HorizontalComponent'] = HorizontalComponentList[index]
		EarthDict['VerticalComponent'] = VerticalComponentList[index]

		EarthDict['GravityComponentList'] = GravityComponentList[index]
		if PreviousGPSIndex !=AcclMagRecordsListStoppages[index]['GPSIndex']:
			PreviousGPSIndex = AcclMagRecordsListStoppages[index]['GPSIndex']
			LR = [LR for LR in con[RouteName][SingleTripInfo+".GPSRecord.Raw"].find({'GPSIndex':AcclMagRecordsListStoppages[index]['GPSIndex']}).limit(1)]
			if len(LR[0])!=4:
				HaveGPSRecord = True
				#pprint.pprint(LR[0])
				Speed = LR[0]["Speed"]
				Latitude = LR[0]["Latitude"]
				Longitude = LR[0]["Longitude"]

		if HaveGPSRecord == True:
			EarthDict["Speed"] = Speed
			EarthDict["Latitude"] = Latitude
			EarthDict["Longitude"] = Longitude
		else:
			EarthDict["Speed"] = "NA"
			EarthDict["Latitude"] = "NA"
			EarthDict["Longitude"] = "NA"

		for key in AcclMagRecordsListStoppages[index]:
			if key =="Mode":
				EarthDict["Mode"] = AcclMagRecordsListStoppages[index][key]

		#pprint.pprint(EarthDict)
		#print(SingleTripInfo+".EAccHVComponent.Raw"+NameToRecord)
		#input()
		con[RouteName][SingleTripInfo+".EAccHVComponent"+NameToRecord].insert_one(EarthDict)
        
    

def ConvertToEarthaxisAcc(RouteName,SingleTripsInfo,IntervalLength,NameToRecord):
	'''
	input: Routename and record type variable
	output: None
	function: It identifies the trips for which the acceleration components are to be computed. Subsequently, it applies the Jigsaw paper method for computing the horizontal and vertical components of the acceleration. The computed acceleration components are then saved in the MongoDB database
	'''
	#SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxis':False})]
	for index in range(len(SingleTripsInfo)):
		print(SingleTripsInfo[index])
		AcclMagRecordsListStoppages =[LR for LR in con[RouteName][SingleTripsInfo[index]+".AcclMagData.Raw"].find().sort([('GPSIndex',1)])]
		ProcessEarthaxisHVComponentUsingJigSawMethod (RouteName,SingleTripsInfo[index],AcclMagRecordsListStoppages,IntervalLength,NameToRecord)

