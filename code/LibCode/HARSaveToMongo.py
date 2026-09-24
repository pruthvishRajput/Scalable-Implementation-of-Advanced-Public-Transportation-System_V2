#!/usr/bin/env python
# coding: utf-8

import subprocess
import os
import sys
import json
from pymongo import     MongoClient

con = MongoClient()

import re
import pandas as pd
import pprint


#pd.set_option('precision', 16) # For floating values
pd.set_option("display.precision", 16)

'''Directory of raw data'''
def SaveHARDataInMongo(RouteName, path):
	'''
	input: The route name and directory path of HAR dataset
	output: None
	function: It extracts the HAR data of different records and saves it in MongoDB 
	'''
	label = os.path.join(path, 'labels.txt')

	Activties = ['WALKING', 'WALKING_UPSTAIRS','WALKING_DOWNSTAIRS','SITTING','STANDING','LAYING',
		        'STAND_TO_SIT','SIT_TO_STAND','SIT_TO_LIE','LIE_TO_SIT','STAND_TO_LIE','LIE_TO_STAND']
	ActivityID = [1,2,3,4,5,6,7,8,9,10,11,12]
	ActivityIncluded = ['WALKING', 'WALKING_UPSTAIRS','WALKING_DOWNSTAIRS','SITTING','STANDING','LAYING',
		        'STAND_TO_SIT','SIT_TO_STAND','SIT_TO_LIE','LIE_TO_SIT','STAND_TO_LIE','LIE_TO_STAND']

	LabelColoumn = ['ExpID','UserID','Activity','StartPt','EndPt']
	LabelFile = open(label,'r')
	DfLabel = pd.read_csv(label,delim_whitespace=True,header=None,names = ['ExpID','UserID','Activity','StartPt','EndPt'])
	DfLabel['ActivityName'] =''

	for (index, row) in DfLabel.iterrows():
		DfLabel.loc[index,'ActivityName']= Activties[row['Activity']-1]
		#print(row['Activity']-1)
		#print(Activties[row['Activity']-1])
		#input()

	SaveUserRecordInMongo(ActivityIncluded, DfLabel, RouteName, path)
	SaveUserTripsInfo(RouteName)
	
def	SaveUserRecordInMongo(ActivityIncluded, DfLabel, RouteName, path):

	'''
	input: The list of activity included in the processing, dataset, route name, and dataset directory path.
	output: None
	function: It extracts the data records for all the activities and saves the data records corresponding to the included activity in the dataset.
	'''

	'''Save the record in mongodb with collection name RawAcc.Activity.User3.segment'''
	for (index, Activity) in enumerate(ActivityIncluded):
		dfActivty = DfLabel.loc[DfLabel['ActivityName']==Activity]
		'''Segment Logic'''
		PreviousUserID = 0
		Segment = 0
		#print(dfActivty.head(n=10))
		for (index, row) in dfActivty.iterrows():
		    Segment =Segment+ 1 if PreviousUserID == row['UserID'] else 0
		    FileNameList = GetFileForExpIDAndUserID(row['ExpID'],row['UserID'], path)
		    for File in FileNameList:
		        #print(File)
		        #print(type(File))
		        #print(row)
		        #index

		        DfAcclData  = pd.read_csv(path+File,delim_whitespace=True,header=None,names = ['X','Y','Z'],float_precision='high')
		        DfAcclDataSliced = DfAcclData.iloc [row['StartPt']:row['EndPt']]
		        #print(DfAcclDataSliced.head())
		        DictSlicedData = SaveToMongo(DfAcclDataSliced)
		        #DictSlicedData = DfAcclDataSliced.to_dict(orient='index')
		        #DictSlicedData = DfAcclDataSliced.to_dict()
		        #pprint.pprint(DictSlicedData)
		        #DfFromDictAcclDataSliced = pd.DataFrame.from_dict(DictSlicedData,orient='index')
		        #DfFromDictAcclDataSliced = pd.DataFrame.from_dict(DictSlicedData)
		        #print(DfFromDictAcclDataSliced.head())
		        #print(DfAcclDataSliced.head ())
		        #print(Segment)
		        '''Save the record in mongodb with collection name RawAcc.Activity.User3.segment'''
		        #check printit
		        ReadingType = File.split('_')[0]
		        CollectionName = ReadingType+'.'+Activity+".User."+str(row['UserID'])+"."+str(Segment)+".Raw"
		        print(CollectionName)
		        '''
		        con[RouteName][CollectionName].insert_many(DataFrames Possible?)

		        '''
		        con[RouteName][CollectionName].insert_many(DictSlicedData)
		        PreviousUserID = row['UserID']
		        #input()

def SaveUserTripsInfo(RouteName):
	'''
	input: Route name
	output: None
	function: It extracts the collections of the selected route from the MongoDB database and saves the metadata of the record in the TripsInfo collection. 
	'''
	'''TripsInfo'''
	CollectionName =[collection for collection in con[RouteName].list_collection_names()]
	for Collection in CollectionName:
		if Collection != "system.indexes":
		    Record ={}
		    CollectionList = Collection.split('.')

		    #print(CollectionList)
		    Record['SingleTripInfo'] = CollectionList[0]+'.'+CollectionList[1]+'.'+CollectionList[2]+'.'+CollectionList[3]+'.'+CollectionList[4]
		    Record['RawExtracted'] = True
		    Record['ConvertedToEarthAxis'] = False
		    Record['FeaturesExtracted'] = False
		    Record['Filtered'] = False
		    #pprint.pprint(Record)
		    con[RouteName]['TripsInfo'].insert_one(Record)
		    #input()


def SaveToMongo(DfAcclDataSliced):
    '''
    input: Dataframe of the accelerometer data
    output: List of JSON dictonary of the accelerometer data
    function: It creates the list of JSON dictonary of the accelerometer data from the provided input
    '''
    DictList =[]
    for (index, row) in DfAcclDataSliced.iterrows():
        Dict ={}
        Dict ['index'] = index
        Dict ['X'] = row['X']
        Dict ['Y'] = row['Y']
        Dict ['Z'] = row['Z']
        DictList.append(Dict)
    return(DictList)


def ExtractFileInfo(fileNameSplits):

    '''
    input: File name
    output: The list of information of activity and user ID
    function: It extracts the list of information of activity and user ID
    '''
    
    #print(fileName)
    FileType =fileNameSplits[0]
    FileExpID = int(fileNameSplits[1][-2:])
    FileUserID = int(fileNameSplits[2].split('.')[0][-2:])
    '''Could be done better using regex'''
    return(FileType,FileExpID,FileUserID)


def GetFileForExpIDAndUserID(ExpID, UserID, path ):
    '''
    input: Experiment ID, User ID and dataset directory path
    output: List of files present in the provided directory
    function: It extracts the list of files present in the provided directory
    '''
    FileNameList = []
    for fileName in [f for f in os.listdir(path)]:
        fileNameSplits = fileName.split('_')
        if (fileNameSplits[0]=='acc'):# or fileNameSplits[0]=='gyro'):
            #print(fileName)
            FileType, FileExpID,FileUserID = ExtractFileInfo(fileNameSplits)
            if FileExpID==ExpID and FileUserID == UserID:
                #return(fileName)
                FileNameList.append(fileName)
    return(FileNameList)

