#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import ExtraTreesClassifier
from pymongo import     MongoClient
import pymongo


con = MongoClient()

def GetFeaturesFromMongoDB(RouteName, FeatureType, RecordType):
    '''
    input: The route name, feature type and trip segment type variable
    output: The features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed. 
    function: It extracts the features of selected feature-set and segment type (Entire segment / Segment other than stoppage segment).
    '''
    XFeatureList = []
    y = []
    SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxis':True})]
    SingleTripsInfo = GetSingleTripRecord(SingleTripsInfo)
    # due to GetSingleTripRecord the FeatureExtracted is not reflected as True 
    for SingleTripInfo in SingleTripsInfo:
        FeaturesDictList = [Features for Features in con [RouteName][SingleTripInfo+FeatureType+RecordType].find().sort([('index',1)])]
        
        #print(SingleTripInfo+FeatureType+RecordType)
        #print(FeaturesDictList[0])
        #input()
    
        for index in range(len(FeaturesDictList)):
            FeaturesDict = FeaturesDictList[index]
            if int(FeaturesDict['ModeInt']) < 5:
                sortednames=sorted(FeaturesDict.keys(), key=lambda x:x.lower())
                #print(sortednames)
                X = []
                for index in sortednames:
                    if index == 'ModeInt':
                        Mode = int(FeaturesDict['ModeInt']) 
                        if Mode == 0 or Mode == 1 or Mode == 2:
                            y.append(0)
                        else:
                            y.append(int(FeaturesDict['ModeInt']))
                        #y.append(int(FeaturesDict['ModeInt']))
                    elif index != 'index' and index != '_id':
                        #print(index)
                        X.append(float(FeaturesDict[index]))

                XFeatureList.append(X)
                #y.append(int(FeaturesDict['ModeInt']))
                #pprint.pprint(XFeatureList)
                #pprint.pprint(y)
                #input()
    return(np.asarray(XFeatureList),np.asarray(y))

def GetFeaturesFromMongoDB(RouteName, FeatureType, RecordType, SelectedFeatures, SelectedFeatures_Flag):
    '''
    input: The route name, feature type and trip segment type variable
    output: The features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed. 
    function: It extracts the features of selected feature-set and segment type (Entire segment / Segment other than stoppage segment).
    '''
    XFeatureList = []
    y = []
    SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxis':True})]
    SingleTripsInfo = GetSingleTripRecord(SingleTripsInfo)
    # due to GetSingleTripRecord the FeatureExtracted is not reflected as True 
    for SingleTripInfo in SingleTripsInfo:
        FeaturesDictList = [Features for Features in con [RouteName][SingleTripInfo+FeatureType+RecordType].find().sort([('index',1)])]
        
        #print(SingleTripInfo+FeatureType+RecordType)
        #print(FeaturesDictList[0])
        #input()
    
        for index in range(len(FeaturesDictList)):
            FeaturesDict = FeaturesDictList[index]
            if int(FeaturesDict['ModeInt']) < 5:
                sortednames=sorted(FeaturesDict.keys(), key=lambda x:x.lower())
                #print(sortednames)
                X = []
                for index in sortednames:
                    if index == 'ModeInt':
                        Mode = int(FeaturesDict['ModeInt']) 
                        if Mode == 0 or Mode == 1 or Mode == 2:
                            y.append(0)
                        else:
                            y.append(int(FeaturesDict['ModeInt']))
                        #y.append(int(FeaturesDict['ModeInt']))
                    elif index != 'index' and index != '_id':
                        #print(index)

                        if SelectedFeatures_Flag==False:
                            X.append(float(FeaturesDict[index]))

                        elif SelectedFeatures_Flag==True:
                            #print(SelectedFeatures)
                            for Feature in SelectedFeatures:
                                if Feature in index and 'Mag' not in index:
                                    X.append(float(FeaturesDict[index]))
                                    
                XFeatureList.append(X)
                #y.append(int(FeaturesDict['ModeInt']))
                #pprint.pprint(XFeatureList)
                #pprint.pprint(y)
                #input()
    return(np.asarray(XFeatureList),np.asarray(y))


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

