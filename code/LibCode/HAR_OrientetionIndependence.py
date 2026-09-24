#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import as_strided
from pymongo import MongoClient

con = MongoClient()
import pprint
import math

def GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ, IntervalLength):
    '''
    input: X, Y, and Z axis accelerometer records
    output: The horizontal and vertical components of the accelerometer records
    function: It computes the horizontal and vertical components of the accelerometer records
    '''
    #IntervalLength = 200 #4 sec

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


# In[18]:


def ProcessEarthaxisHVComponentUsingJigSawMethod (RouteName,SingleTripInfo,AcclMagRecordsListStoppages, IntervalLength):
    '''
    input:  The trip name, route name, accelerometer records, and record type variable
    output: None
    function: It utilizes the Jigsaw paper based method for computing the horizontal and vertical components of the acceleration and saves it in the MongoDB
    '''
    AcclRecordInListX = [AclR['X'] for AclR in AcclMagRecordsListStoppages]
    AcclRecordInListY = [AclR['Y'] for AclR in AcclMagRecordsListStoppages]
    AcclRecordInListZ = [AclR['Z'] for AclR in AcclMagRecordsListStoppages]

    #pprint.pprint(AcclRecordInList)

    HorizontalComponentList,VerticalComponentList = GetHorizontalAndVerticalComponent(AcclRecordInListX, AcclRecordInListY, AcclRecordInListZ, IntervalLength)
    #pprint.pprint(len(AcclRecordInListX))
    #pprint.pprint(len(AcclList))
    #pprint.pprint(AcclList)

    for index in range(len(AcclMagRecordsListStoppages)):
        EarthDict = {}
        EarthDict['index'] = AcclMagRecordsListStoppages[index]['index']
        #EarthDict['AcclIndex'] = AcclMagRecordsListStoppages[index]['AcclIndex']  # check

        EarthDict['HorizontalComponent'] = HorizontalComponentList[index]
        EarthDict['VerticalComponent'] = VerticalComponentList[index]
        EarthDict['GPSIndex'] = AcclMagRecordsListStoppages[index]['index']
        EarthDict['AcclIndex'] = AcclMagRecordsListStoppages[index]['index']
        #pprint.pprint(EarthDict)
        con[RouteName][SingleTripInfo+".EAccHVComponent"].insert_one(EarthDict)
        #input()


# In[10]:


def GetSingleTripRecord(SingleTripsInfo):
    '''
    input: The trip list
    output: The list with sliced trip name
    function: It slices the trip name by discarding the part of file name before the first '.'
    '''
    SingleTripsInfoNew = []
    for SingleTripInfo in SingleTripsInfo:
        SingleTripInfoSplit = SingleTripInfo.split('.')
        SingleTripsInfoNew.append(SingleTripInfoSplit[1]+'.'+SingleTripInfoSplit[2]+'.'+SingleTripInfoSplit[3]+'.'+SingleTripInfoSplit[4])
    SingleTripsInfoNew  = list(set(SingleTripsInfoNew))
    #pprint.pprint(SingleTripsInfo)
    #pprint.pprint(SingleTripsInfoNew)
    #pprint.pprint(set(SingleTripsInfoNew))
    return(SingleTripsInfoNew)
