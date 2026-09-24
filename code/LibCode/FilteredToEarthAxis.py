from scipy.signal import butter, lfilter, stft, medfilt
import pprint
import numpy as np
from pymongo import     MongoClient
con = MongoClient()

import pprint
import math

def GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ):
	IntervalLength = 160 #4 sec

	TotalPoint = math.ceil(len(AcclRecordInListX)/IntervalLength)

	HorizontalComponentList = []
	VerticalComponentList = []
	#GravityComponentList =[]
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

			#GravityComponentList.append(Gravity)
			#AcclList.append(Accl)
	#return(HorizontalComponentList,VerticalComponentList,AcclLen)
	return(HorizontalComponentList,VerticalComponentList)

def ProcessEarthaxisHVComponentUsingJigSawMethod (RouteName,SingleTripInfo,AcclMagRecordsListStoppages,RecordType):
	AcclRecordInListX = [AclR['X'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListY = [AclR['Y'] for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListZ = [AclR['Z'] for AclR in AcclMagRecordsListStoppages]

	#pprint.pprint(AcclRecordInList)

	HorizontalComponentList,VerticalComponentList = GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ)
	#pprint.pprint(len(AcclRecordInListX))
	#pprint.pprint(len(AcclList))
	#pprint.pprint(AcclList)

	for index in range(len(AcclMagRecordsListStoppages)):
		EarthDict = {}
		EarthDict['GPSIndex'] = AcclMagRecordsListStoppages[index]['GPSIndex']
		EarthDict['AcclIndex'] = AcclMagRecordsListStoppages[index]['AcclIndex']  # check

		EarthDict['HorizontalComponent'] = HorizontalComponentList[index]
		EarthDict['VerticalComponent'] = VerticalComponentList[index]
		#pprint.pprint(EarthDict)

		for key in AcclMagRecordsListStoppages[index]:
			if key == "Mode":
				EarthDict["Mode"] = AcclMagRecordsListStoppages[index][key]

		con[RouteName][SingleTripInfo+".EAccHVComponent"+RecordType].insert_one(EarthDict)
		#input()

