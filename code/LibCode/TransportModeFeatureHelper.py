import numpy as np
from numpy.lib.stride_tricks import as_strided

from pymongo import     MongoClient

con = MongoClient()

import pprint

import math

import FeaturesExtraction
import ComputeFeaturesTransportMode

def GetTripsBasedOnType(RouteName):
    '''
    input: The routename
    output: The trips for different transport mode
    function: It bifurcates the different trips based on transport mode.
    '''
    SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxis':True})]
    #SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteName]['TripsInfo'].find({'ConvertedToEarthAxis':False})]
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

def GetTripsForTransportModes():
	'''
	input: None 
	output: The trip list of different modes
	function: Get the selected trips for different modes
	'''

	'''
	PDCar = ['PD.30_10_2018__18_30_15',
		     'PD.02_11_2018__18_34_22',
		     'PD.13_11_2018__18_26_46',
		     'PD.20_11_2018__18_30_41',
		     'PD.08_01_2019__18_51_12',
		     'PD.10_01_2019__17_42_59',
		     'PD.11_01_2019__17_57_18',
		     'PD.16_01_2019__17_41_04',
		     'PD.18_01_2019__11_58_48',
		    ]

	PDBike =['PD.25_10_2018__18_32_59',
		     'PD.12_11_2018__18_29_53',
		     'PD.26_10_2018__18_30_54',
		     'PD.01_11_2018__18_30_23',
		     'PD.14_11_2018__18_27_21',
		     'PD.19_11_2018__18_31_30',
		     'PD.01_01_2019__17_48_11',
		     'PD.02_01_2019__17_49_45',
		     'PD.04_01_2019__17_49_44',
		     'PD.07_01_2019__16_43_07'
		    ]
	BMSingleTripsInfoList = ['BM.02_11_2018__07_47_26',
							 'BM.12_11_2018__07_36_10',
							 'BM.01_11_2018__18_30_46',
							 'BM.02_11_2018__18_33_04',
							 'BM.01_11_2018__07_37_32']

	CMSingleTripsInfoList = ['CM.01_11_2018__07_37_30',
							 'CM.02_11_2018__07_47_28',
							 'CM.12_11_2018__07_36_18',
							 'CM.02_11_2018__18_33_09',
							 'CM.01_11_2018__18_30_52']
	'''
	PDCar = ['PD.Car.30_10_2018__18_30_15',
		     'PD.Car.02_11_2018__18_34_22',
		     'PD.Car.13_11_2018__18_26_46',
		     'PD.Car.20_11_2018__18_30_41',
		     'PD.Car.08_01_2019__18_51_12',
		     'PD.Car.10_01_2019__17_42_59',
		     'PD.Car.11_01_2019__17_57_18',
		     'PD.Car.16_01_2019__17_41_04',
		     'PD.Car.18_01_2019__11_58_48',
		    ]

	PDBike =['PD.Bike.25_10_2018__18_32_59',
		     'PD.Bike.12_11_2018__18_29_53',
		     'PD.Bike.26_10_2018__18_30_54',
		     'PD.Bike.01_11_2018__18_30_23',
		     'PD.Bike.14_11_2018__18_27_21',
		     'PD.Bike.19_11_2018__18_31_30',
		     'PD.Bike.01_01_2019__17_48_11',
		     'PD.Bike.02_01_2019__17_49_45',
		     'PD.Bike.04_01_2019__17_49_44',
		     'PD.Bike.07_01_2019__16_43_07'
		    ]
	BMSingleTripsInfoList = ['BM.Bus.02_11_2018__07_47_26',
							 'BM.Bus.12_11_2018__07_36_10',
							 'BM.Bus.01_11_2018__18_30_46',
							 'BM.Bus.02_11_2018__18_33_04',
							 'BM.Bus.01_11_2018__07_37_32']

	CMSingleTripsInfoList = ['CM.Bus.01_11_2018__07_37_30',
							 'CM.Bus.02_11_2018__07_47_28',
							 'CM.Bus.12_11_2018__07_36_18',
							 'CM.Bus.02_11_2018__18_33_09',
							 'CM.Bus.01_11_2018__18_30_52']
	

	return(PDCar, PDBike, BMSingleTripsInfoList, CMSingleTripsInfoList)

def ExtractFeaturesOfGivenTypeOfTrip(BMSingleTripsInfoList,Mode,ModeInt,Window,RecordType, RouteName):
    '''
    input: The trips list, transport mode value, trip segment information, window length for feature computation, and routename
    output: The features of different trips
    function: It computes the features of different trip records
    '''
    
    for index in range(len(BMSingleTripsInfoList)):
        print(BMSingleTripsInfoList[index])
        GetSegmentAndApplyFeatureExtraction(BMSingleTripsInfoList[index],ModeInt,Window,RecordType, RouteName)
    
        con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':BMSingleTripsInfoList[index]},
                                               {'$set':{'FeaturesExtractedSegment':True}})

        

def GetSegmentAndApplyFeatureExtraction(BMSingleTripInfo,ModeInt,Window,RecordType, RouteName):
    '''
    input: The trips list, transport mode value, trip segment information, window length for feature computation, and routename
    output: The features for the segment other than stoppage segment
    function: It extracts the segment other than stoppage segment and compute the features using the extracted records.
    '''
    BMStoppageSegments = [Segment for Segment in con[RouteName]['TripsInfo'].find({'SingleTripInfo':BMSingleTripInfo})]
    BMStoppageSegmentsList = BMStoppageSegments[0]['StopSegments']
    
    for indexj in range(len(BMStoppageSegmentsList)):
        BMLocationRecordsListStoppages =[LR for LR in con[RouteName][BMSingleTripInfo+".GPSRecord.Segment"].find({ '$and': [ { 'Time': { '$gte': BMStoppageSegmentsList[indexj][0] } }, { 'Time': {'$lte':BMStoppageSegmentsList[indexj][1]} } ] }).sort([('GPSIndex',1)])]
        if len(BMLocationRecordsListStoppages)!=0:
            #print(len(BMLocationRecordsListStoppages))
            '''
            pprint.pprint(BMLocationRecordsListStoppages[0])
            pprint.pprint(BMLocationRecordsListStoppages[len(BMLocationRecordsListStoppages)-1])
            print(len(BMLocationRecordsListStoppages))
            '''
            BMLowerGPSIndex = BMLocationRecordsListStoppages[0]["GPSIndex"]
            BMUpperGPSIndex = BMLocationRecordsListStoppages[len(BMLocationRecordsListStoppages)-1]["GPSIndex"]

            BMAcclMagRecordsListStoppagesHVComponent = [AclR for AclR in con[RouteName][BMSingleTripInfo+".EAccHVComponent"+RecordType].find({ '$and': [ { 'GPSIndex': { '$gte': BMLowerGPSIndex} }, { 'GPSIndex': {'$lte':BMUpperGPSIndex} } ] }).sort([('GPSIndex',1)])]

            
            ComputeFeaturesTransportMode.ComputeFeature(BMSingleTripInfo,BMAcclMagRecordsListStoppagesHVComponent,ModeInt,Window,RecordType, RouteName)

            FeaturesExtraction.ComputeFeatureForComponents(RouteName,BMAcclMagRecordsListStoppagesHVComponent,ModeInt
                                                           ,Window,BMSingleTripInfo,RecordType)
            

def GetFeaturesForGivenTripType(SingleTripsInfo,Mode,WindowSize,RecordType, RouteName):
    '''
    input: The trips list, transport mode value, trip segment information, window length for feature computation, and routename
    output: The features for the segment other than stoppage segment or raw records
    function: The higher level implementation of feature computation for the trips list of the provided route name
    '''
    '''For entire Trip'''
    for SingleTripInfo in SingleTripsInfo:
        print(SingleTripInfo)
        HVRecord = [Rec for Rec in con[RouteName][SingleTripInfo+'.EAccHVComponent.Raw'].find().sort([('GPSIndex',1)])]

        FeaturesExtraction.ComputeFeatureForComponents(RouteName,HVRecord,Mode,WindowSize,SingleTripInfo,RecordType)
        
        ComputeFeaturesTransportMode.ComputeFeature(SingleTripInfo,HVRecord,Mode,WindowSize,RecordType, RouteName)
        #print(ModeIndex)
        
        con[RouteName]['TripsInfo'].update_one({'SingleTripInfo':SingleTripInfo},{'$set':{'FeaturesExtractedRaw':True}})
        #input()    
