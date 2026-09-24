#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import os

#from sklearn.datasets import make_classification
from sklearn.ensemble import ExtraTreesClassifier
from pymongo import     MongoClient

con = MongoClient()

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix,precision_score, recall_score, f1_score
from sklearn import tree
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
import pymongo
import pprint
from collections import Counter
from sklearn.impute import SimpleImputer
import pickle

def GetSlicedAcclMagRecord(RouteName,SingleTripInfo):
    '''
    input: The trips list of the given route for which the slicing operation is to be performed
    output: Sliced Accelerometer and GPS records for the given trips
    function: It slices (or removes) the records of first and last five minutes of trips to remove the segments of extranoues user movements during initial and final stage of the trip.
    '''
    #print(SingleTripInfo)
    AcclMagRecordWithTimeStamp = [collection for collection in con[RouteName][SingleTripInfo+'.AcclMagData.Raw'].find().sort([('GPSIndex',1)]) if 'Time' in collection]
    
    '''Get records which has time stamp'''
    #AcclMagRecordWithTimeStamp =  [Rec for Rec in AcclMagRecord if len(Rec)==10]
    '''Add 5 min to start and substract 5 min from end'''
    StartPointTime = AcclMagRecordWithTimeStamp[0]['Time']+300000
    EndPointTime = AcclMagRecordWithTimeStamp[-1]['Time']-300000
    
    AcclMagRecordsAccordingToTimeStamp = [collection for collection in con[RouteName][SingleTripInfo+'.AcclMagData.Raw'].find({ '$and': [ { 'Time': { '$gte': StartPointTime } }, { 'Time': {'$lte':EndPointTime} } ] }).sort([('GPSIndex',1)])]
    
    StartPointGPSIndex = AcclMagRecordsAccordingToTimeStamp[0]['GPSIndex']
    EndPointGPSIndex = AcclMagRecordsAccordingToTimeStamp[-1]['GPSIndex']
    
    AcclMagRecordSliced = [collection for collection in con[RouteName][SingleTripInfo+'.AcclMagData.Raw'].find({ '$and': [ { 'GPSIndex': { '$gte': StartPointGPSIndex } }, { 'GPSIndex': {'$lte':EndPointGPSIndex} } ] }).sort([('GPSIndex',1)])]
    
    #pprint.pprint(AcclMagRecordSliced[0])
    #pprint.pprint(AcclMagRecordSliced[-1])
    
    #print(len(AcclMagRecordSliced)-len(AcclMagRecordsAccordingToTimeStamp))
    #input()
    
    return(AcclMagRecordSliced)

def GetData(FeatureType, RecordType, SelectedFeatures, SelectedFeatures_Flag):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed.  
    output: The tuple (X,y) of the features and the labels for different commuter state and phone position
    function: It extracts the features of the selected feature set for either the entire trip records or for the segment other than the stoppage segments based the input variables and forms the tuple of Features and corresponding labels for different commuter state and phone positions. 
    '''
    
    
    '''HAR_PDPU_SANAND'''
    '''
    print('------------------------------------------------------------------------------------------------')
    print('--------------------------------For HAR_PDPU_SANAND---------------------------------------------')
    print('------------------------------------------------------------------------------------------------')
    '''

    RouteNameTest = 'HAR_PDPU_SANAND'

    HandSingleTripsInfoSitting = [LR['SingleTripInfo'] for LR in
                                  con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})
                                  if LR['SingleTripInfo'].split('.')[2]=='Hand' and 
                                  (LR['SingleTripInfo'].split('.')[1]=='Sitting' or
                                   LR['SingleTripInfo'].split('.')[1]=='Seating')
                                 ]

    X0_0,y0_0 = GetFeatures(RouteNameTest, HandSingleTripsInfoSitting,FeatureType,
                            RecordType,0, SelectedFeatures, SelectedFeatures_Flag)
    
    #print('HandSingleTripsInfoSitting', len(HandSingleTripsInfoSitting))
    '''
    print('HandSingleTripsInfoSitting',HandSingleTripsInfoSitting)
    input()
    '''


    ShirtPocketSingleTripsInfoSitting = [LR['SingleTripInfo'] for LR in 
                                         con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                         if LR['SingleTripInfo'].split('.')[2]=='ShirtPocket' and 
                                         (LR['SingleTripInfo'].split('.')[1]=='Sitting' or 
                                          LR['SingleTripInfo'].split('.')[1]=='Seating')
                                        ]

    X0_1,y0_1 = GetFeatures(RouteNameTest, ShirtPocketSingleTripsInfoSitting, FeatureType,
                            RecordType,1, SelectedFeatures, SelectedFeatures_Flag)

    '''
    print('ShirtPocketSingleTripsInfoSitting',ShirtPocketSingleTripsInfoSitting)
    input()
    '''


    ShirtPocketSingleTripsInfoStanding = [LR['SingleTripInfo'] for LR in 
                                          con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                          if LR['SingleTripInfo'].split('.')[2]=='ShirtPocket'
                                          and LR['SingleTripInfo'].split('.')[1]=='Standing'
                                         ]

    X0_2,y0_2 = GetFeatures(RouteNameTest, ShirtPocketSingleTripsInfoStanding,FeatureType,
                            RecordType,2, SelectedFeatures, SelectedFeatures_Flag)

    '''
    print('ShirtPocketSingleTripsInfoStanding',ShirtPocketSingleTripsInfoStanding)
    input()
    '''


    TrouserPocketSingleTripsInfoStanding = [LR['SingleTripInfo'] for LR in
                                            con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                            if LR['SingleTripInfo'].split('.')[2]=='TrouserPocket' 
                                            and LR['SingleTripInfo'].split('.')[1]=='Standing'
                                           ]
    
    X0_3,y0_3 = GetFeatures(RouteNameTest, TrouserPocketSingleTripsInfoStanding,
                            FeatureType,RecordType,3, SelectedFeatures, SelectedFeatures_Flag)

    '''
    print('TrouserPocketSingleTripsInfoStanding',TrouserPocketSingleTripsInfoStanding)
    input()
    '''

    '''
    print('------------------------------------------------------------------------------------------------')
    print('----------------------------For HAR_PDPU_SANAND_Triggers----------------------------------------')
    print('------------------------------------------------------------------------------------------------')
    '''
    
    #RouteNameTest = 'HAR_PDPU_SANAND_Triggers'
    '''

    HandSingleTripsInfoSitting = [LR['SingleTripInfo'] for LR in 
                                  con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                  if LR['SingleTripInfo'].split('.')[2]=='Hand' 
                                  and (LR['SingleTripInfo'].split('.')[1]=='Sitting' 
                                       or LR['SingleTripInfo'].split('.')[1]=='Seating')
                                 ]
    print('HandSingleTripsInfoSitting', len(HandSingleTripsInfoSitting))
    X1_0,y1_0 = GetFeatures(RouteNameTest, HandSingleTripsInfoSitting,
                            FeatureType,RecordType,0, SelectedFeatures, SelectedFeatures_Flag)
    '''
    '''
    print('HandSingleTripsInfoSitting',HandSingleTripsInfoSitting)
    input()
    '''
    '''

    ShirtPocketSingleTripsInfoSitting = [LR['SingleTripInfo'] for LR in
                                         con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})
                                         if LR['SingleTripInfo'].split('.')[2]=='ShirtPocket' 
                                         and (LR['SingleTripInfo'].split('.')[1]=='Sitting' 
                                              or LR['SingleTripInfo'].split('.')[1]=='Seating')
                                        ]

    X1_1,y1_1 = GetFeatures(RouteNameTest, ShirtPocketSingleTripsInfoSitting,
                            FeatureType,RecordType,1, SelectedFeatures, SelectedFeatures_Flag)
    '''

    '''
    print('ShirtPocketSingleTripsInfoSitting',ShirtPocketSingleTripsInfoSitting)
    input()
    '''

    '''
    ShirtPocketSingleTripsInfoStanding = [LR['SingleTripInfo'] for LR in 
                                          con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                          if LR['SingleTripInfo'].split('.')[2]=='ShirtPocket' 
                                          and LR['SingleTripInfo'].split('.')[1]=='Standing'
                                         ]
                                         

    X1_2,y1_2 = GetFeatures(RouteNameTest,ShirtPocketSingleTripsInfoStanding,
                            FeatureType,RecordType,2, SelectedFeatures, SelectedFeatures_Flag)
    '''

    '''
    print('ShirtPocketSingleTripsInfoStanding',ShirtPocketSingleTripsInfoStanding)
    input()
    '''
    '''

    TrouserPocketSingleTripsInfoStanding = [LR['SingleTripInfo'] for LR in 
                                            con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                            if LR['SingleTripInfo'].split('.')[2]=='TrouserPocket' 
                                            and LR['SingleTripInfo'].split('.')[1]=='Standing'
                                           ]

    X1_3,y1_3 = GetFeatures(RouteNameTest,TrouserPocketSingleTripsInfoStanding,
                            FeatureType,RecordType,3, SelectedFeatures, SelectedFeatures_Flag)
    '''

    '''
    print('TrouserPocketSingleTripsInfoStanding',TrouserPocketSingleTripsInfoStanding)
    input()
    '''

    HandSingleTripsInfoStanding = [LR['SingleTripInfo'] for LR in 
                                   con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True}) 
                                   if LR['SingleTripInfo'].split('.')[2]=='Hand' 
                                   and LR['SingleTripInfo'].split('.')[1]=='Standing'
                                  ]

    X1_4,y1_4 = GetFeatures(RouteNameTest,HandSingleTripsInfoStanding,
                            FeatureType,RecordType,4, SelectedFeatures, SelectedFeatures_Flag)

    '''
    print('HandSingleTripsInfoStanding',HandSingleTripsInfoStanding)
    input()
    '''

    '''Removing the shirt pocket trip (index: 1_2): having no accl data'''
    #X = np.concatenate((X0_0,X1_0,X0_1,X1_1,X0_2,X0_3,X1_3,X1_4))
    #y = np.concatenate((y0_0,y1_0,y0_1,y1_1,y0_2,y0_3,y1_3,y1_4))
    
    '''
    X = np.concatenate((X0_0,X1_0,X0_1,X1_1,X0_2,X1_2,X0_3,X1_3,X1_4))
    y = np.concatenate((y0_0,y1_0,y0_1,y1_1,y0_2,y1_2,y0_3,y1_3,y1_4))
    '''
    
    ''' After merging the Routes'''

    X = np.concatenate((X0_0,X0_1,X0_2,X0_3,X1_4))
    y = np.concatenate((y0_0,y0_1,y0_2,y0_3,y1_4))

    
    '''
    if Trip == 'M.Sitting.Hand.To.13_02_2019__14_03_01':
        RouteNameTest = 'HAR_PDPU_SANAND_ForRevision'
        
        X_Other,y_Other = GetFeaturesFromMongoDBForSitStandWithPosition(RouteNameTest,
                                                                        [Trip],
                                                                        FeatureType,
                                                                        '.OtherThanRoadSegment_ForRevision',0)
        
        X = np.concatenate((X, X_Other))
        y = np.concatenate((y, y_Other))
    '''
    
    return(X,y)

def GetData_User(RouteNameTest, FeatureType, RecordType, SelectedFeatures, SelectedFeatures_Flag):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed. 
    output: The tuple (X,y) of the features and the labels for different commuter state and phone position.
    function: It extracts the features of the selected feature set for either the entire trip records or for the segment other than the stoppage segments based the input variables and forms the tuple of Features and corresponding labels for different commuter state and phone positions. It is similar to 'GetData' function, but for the dataset of users' trips.
    '''    
    XFeatureList = []
    y = []
    '''

    if FeatureType == '.TransportFeatures' and RouteType=='Transport':
        # The transport mode features for ISCON_PDPU route is saved in as: .TransportModeFirstVersionFeatures
        FeatureType = '.TransportModeFirstVersionFeatures'
    '''    
    SingleTripsInfo = [LR['SingleTripInfo'] for LR in 
                       con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})]    
    for SingleTripInfo in SingleTripsInfo:

        FeaturesDictList = [Features for Features in 
                            con [RouteNameTest][SingleTripInfo+FeatureType+RecordType].find().sort([('index',1)])]

        for index in range(len(FeaturesDictList)):
            FeaturesDict = FeaturesDictList[index]
            sortednames=sorted(FeaturesDict.keys(), key=lambda x:x.lower())

            X = []
            for index in sortednames:
                if index == 'ModeInt':
                    y.append(int(FeaturesDict['ModeInt']))
                        
                elif (index != 'index' and index != '_id' and index != 'StartAcclIndex' 
                      and index !='StartGPSIndex'):
                    
                    if SelectedFeatures_Flag==False:
                        X.append(float(FeaturesDict[index]))
                        
                    elif SelectedFeatures_Flag==True:
                        for Feature in  SelectedFeatures:
                            if Feature in index and 'Mag' not in index:
                                X.append(float(FeaturesDict[index]))

                    
            XFeatureList.append(X)
            
    return(ReplaceNAnsByMean(XFeatureList),np.asarray(y))    


def GetFeatures(RouteNameTest,SingleTripsInfo,FeatureType,RecordType,Position, SelectedFeatures,
                SelectedFeaturesFlag):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage') of 'RouteNameTest' route. Subsequently, the tuple of Feature and Data label is formed based on the Position variable which specifies the phone position. The tuple is formed for all the trips listed in 'SingleTripsInfo' list.
    output: The tuple of features and corresponding labels
    function: It exrtracts the features from one of the four feature-set and corresponding labels for the provided trip list.
    '''
    XFeatureList = []
    y = []
    
    for SingleTripInfo in SingleTripsInfo:

        FeaturesDictList = [Features for Features in con
                            [RouteNameTest][SingleTripInfo+FeatureType+RecordType].find().sort([('index',1)])]
                            
        for index in range(len(FeaturesDictList)):
            FeaturesDict = FeaturesDictList[index]
            sortednames=sorted(FeaturesDict.keys(), key=lambda x:x.lower())
            
            X = []
            for index in sortednames:
                if index == 'ModeInt':
                    y.append(Position)
                elif (index != 'index' and index != '_id' and 
                      index != 'StartAcclIndex' and index !='StartGPSIndex'):
                    
                    if SelectedFeaturesFlag == False:
                        X.append(float(FeaturesDict[index]))
                        
                    else:
                        for Feature in  SelectedFeatures:
                            if Feature in index and 'Mag' not in index:
                                X.append(float(FeaturesDict[index]))
                    
            XFeatureList.append(X)
    return(ReplaceNAnsByMean(XFeatureList),np.asarray(y))



def TrainAndPredict(X, y, MyClassifier, MetricsDict):
    '''
    input: The features and labels list, classifier instance and dictionary to store the prediction result.
    output: The dictionary representing the classification performance metrics.
    function: It trains the classifier by applying the stratified sampling and ten-fold cross validation on the features and labels, and predicts the output using for each fold. The result is stored in the MetricsDict.
    '''
        
    skf = StratifiedKFold(n_splits=10)
    skf.get_n_splits(X, y)

    for train_index, test_index in skf.split(X, y):
        #print("TRAIN:", train_index, "TEST:", test_index)
        XTrain, XTest = X[train_index], X[test_index]
        YTrain, YTest = y[train_index], y[test_index]

        scaler = StandardScaler()
        scaler.fit(XTrain)
        XTrainTransformed = scaler.transform(XTrain)
        XTestTransformed = scaler.transform(XTest)

        MyClassifier.fit(XTrainTransformed,YTrain)
        predictions = MyClassifier.predict(XTestTransformed)
        
        '''Save metrics'''
        MetricsDict = FetchMetrics(YTest, predictions, MetricsDict)
        '''Save metrics'''        
        
        '''Optional print metrics'''
        
    return(MetricsDict)
    
def TrainAndPredict(X, y, MyClassifier, MetricsDict, ResultPathDir, ClassifierName, UsedPreTrained, ClassifierName_ForModelSave, TrainedModelPathDir):
    '''
    input: The features and labels list, classifier instance and dictionary to store the prediction result. It also consists the variable to determined whether a pretrained model is used or not.
    output: The dictionary representing the classification performance metrics.
    function: It trains the classifier by applying the stratified sampling and ten-fold cross validation on the features and labels if the UsedPreTrained is false else it used the pretrained model. The function also predicts the output using for each fold. The result is stored in the MetricsDict.
    '''    
    skf = StratifiedKFold(n_splits=10)
    skf.get_n_splits(X, y)
    index = 0

    for train_index, test_index in skf.split(X, y):
        #print("TRAIN:", train_index, "TEST:", test_index)
        XTrain, XTest = X[train_index], X[test_index]
        YTrain, YTest = y[train_index], y[test_index]

        scaler = StandardScaler()
        scaler.fit(XTrain)
        XTrainTransformed = scaler.transform(XTrain)
        XTestTransformed = scaler.transform(XTest)
        
        if UsedPreTrained == False:
        
            MyClassifier.fit(XTrainTransformed,YTrain)
            '''Save model'''
            
            File = os.path.join(TrainedModelPathDir, f'{ClassifierName_ForModelSave}_Model_{index}.sav')
            #File = f'{ResultPathDir}{ClassifierName}_Model_{index}.sav'
            #filename = 'finalized_model.sav'
            pickle.dump(MyClassifier, open(File, 'wb'))        
            
        else: 
            File = os.path.join(TrainedModelPathDir, f'{ClassifierName_ForModelSave}_Model_{index}.sav')
            #File = f'{ResultPathDir}{ClassifierName}_Model_{index}.sav'
            MyClassifier = pickle.load(open(File, 'rb'))
            
        predictions = MyClassifier.predict(XTestTransformed)
        
        '''Save metrics'''
        MetricsDict = FetchMetrics(YTest, predictions, MetricsDict)
        '''Save metrics'''        
        
        '''Optional print metrics'''
        index += 1
        
    return(MetricsDict)    

def TrainAndPredict(X, y, MyClassifier, MetricsDict, ResultPathDir, ClassifierName, UsedPreTrained, ClassifierName_ForModelSave, TrainedModelPathDir, ReducedKFolds):
    '''
    input: The features and labels list, classifier instance and dictionary to store the prediction result. It also consists the variable to determined whether a pretrained model is used or not.
    output: The dictionary representing the classification performance metrics.
    function: It trains the classifier by applying the stratified sampling and ten-fold cross validation on the features and labels if the UsedPreTrained is false else it used the pretrained model. The function also predicts the output using for each fold. The result is stored in the MetricsDict.
    '''    
    skf = StratifiedKFold(n_splits=10)
    skf.get_n_splits(X, y)
    index = 0

    for train_index, test_index in skf.split(X, y):
        #print("TRAIN:", train_index, "TEST:", test_index)
        XTrain, XTest = X[train_index], X[test_index]
        YTrain, YTest = y[train_index], y[test_index]

        scaler = StandardScaler()
        scaler.fit(XTrain)
        XTrainTransformed = scaler.transform(XTrain)
        XTestTransformed = scaler.transform(XTest)
        
        if UsedPreTrained == False:
        
            MyClassifier.fit(XTrainTransformed,YTrain)
            '''Save model'''
            
            File = os.path.join(TrainedModelPathDir, f'{ClassifierName_ForModelSave}_Model_{index}.sav')
            #File = f'{ResultPathDir}{ClassifierName}_Model_{index}.sav'
            #filename = 'finalized_model.sav'
            pickle.dump(MyClassifier, open(File, 'wb'))        
            
        else: 
            File = os.path.join(TrainedModelPathDir, f'{ClassifierName_ForModelSave}_Model_{index}.sav')
            #File = f'{ResultPathDir}{ClassifierName}_Model_{index}.sav'
            MyClassifier = pickle.load(open(File, 'rb'))
            
        predictions = MyClassifier.predict(XTestTransformed)
        
        '''Save metrics'''
        MetricsDict = FetchMetrics(YTest, predictions, MetricsDict)
        '''Save metrics'''        
        
        if ReducedKFolds==True:
            break
        
        '''Optional print metrics'''
        index += 1
        
    return(MetricsDict)    



def ReplaceNAnsByMean(XFeatureList):
    '''
    input: The features list with NA values
    output: The features list with NA values replaced by the mean of the corresponding feature column
    function: It replaces the NA values in the features list by the mean of the corresponding feature column
    '''
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    XFeatureListNP = np.asarray(XFeatureList)
    #print(XFeatureListNP.shape)
    #input()
    
    imp.fit(XFeatureListNP)       
    XFeatureListNP = imp.transform(XFeatureListNP)
    return(XFeatureListNP)


def SelectedFeaturesForFeatureType(FeatureType):
    '''
    input: The feature type
    output: The selected features based on the feature type
    function: It selects the appropriate features for the given feature type
    '''
    if FeatureType == '.TransportFeatures':
        '''To be used with Transport mode'''
        SelectedFeatures=['B1EnergyV', 'B1ToB2RatioV', 'B3EnergyH', 'B3ToB4RatioH',
                          'MeanCrossingRateV', 'MeanH', 'MeanV', 'RMSH', 'ThirdQuartileH',
                          'ThreeHzMagV', 'VolumeH']
        
    elif FeatureType == '.HARFeature':
        '''To be used with HAR'''
        SelectedFeatures = ['B1Energy', 'B1ToB2Ratio', 'B3Energy', 'B3ToB4Ratio', 'MeanCrossingRate',
                            'Mean', 'RMS', 'ThirdQuartile', 'ThreeHzMag', 'Volume']
        
    return(SelectedFeatures)


def InitializeMetricsDict(Classes=5):
    '''
    input: The number of classes
    output: The dictonary for handling the performance metrics of the classifier
    function: It initializes the dictonary for handling the performance metrics of the classifier
    '''
    MetricsDict = {}
    MetricsDict['ConfusionMatrix'] = np.full((Classes,Classes), 0, dtype=float)
    MetricsDict['PrecissionList'] = []
    MetricsDict['RecallList'] = []
    MetricsDict['F1ScoreList'] = []
    MetricsDict['OverallAccuracy'] = []
    
    return(MetricsDict)


def PrintMetricsDict(ClassifierName, ResultPathDir, FeatureType, RecordType, SelectedFeatures_Flag, MetricsDict):
    '''
    input: The classifier name, path of result directory, type of feature record, and the Metric Dictionary containing the performance of the classifier  
    output: None
    function: It stores the Metric values of the provided classifier input in the result directory
    '''
    File = open(f'{ResultPathDir}{ClassifierName}.txt', 'a+')
    '''
    print('ConfusionMatrix')
    pprint.pprint(MetricsDict['ConfusionMatrix'])
    '''
    File.write(f'Results for {RecordType}, {FeatureType}, and selected features flag: {SelectedFeatures_Flag}\n')
    File.write('ConfusionMatrix \n')
    File.write(np.array2string(MetricsDict['ConfusionMatrix']))
    File.write('\n \n')
    
    PrecissionValue = np.mean(MetricsDict['PrecissionList'],axis=0)
    '''
    print('PrecissionList')
    pprint.pprint(PrecissionValue)
    ''' 
    File.write('PrecissionValue \n')
    File.write(np.array2string(PrecissionValue))
    File.write('\n \n')
    
    
    RecallValue = np.mean(MetricsDict['RecallList'],axis=0)
    '''
    print('RecallList')
    pprint.pprint(RecallValue)
    '''
    File.write('RecallValue \n')
    File.write(np.array2string(RecallValue))    
    File.write('\n \n')
    
    F1ScoreValue = np.mean(MetricsDict['F1ScoreList'],axis=0)
    '''
    print('F1ScoreList')
    pprint.pprint(F1ScoreValue)
    '''
    File.write('F1ScoreValue \n')
    File.write(np.array2string(F1ScoreValue))
    File.write('\n \n')
    
    AccuracyValue = np.mean(MetricsDict['OverallAccuracy'])
    '''
    print('OverallAccuracy')
    pprint.pprint(AccuracyValue)
    '''
    File.write('AccuracyValue \n')
    File.write(str(AccuracyValue))
    File.write('\n \n')
                  
    File.close()


def InfereSitStand_And_PrintMetrics(MetricsDict, ClassifierName, ResultPathDir):
    '''
    input: The performance metrics dictionary. classifier name, and result directory path
    output: None
    function: It inferes the commuter state by merging the classes of commuter state for different phone position
    '''
    ConfusionMetrix = MetricsDict['ConfusionMatrix']
    SitStand_ConfusionMetrics = np.full((2,2), 0, dtype=float)
    SitStand_ConfusionMetrics[0][0] = (ConfusionMetrix[0][0] + ConfusionMetrix[0][1] + 
                                       ConfusionMetrix[1][0] + ConfusionMetrix[1][1])
    
    SitStand_ConfusionMetrics[0][1] = (ConfusionMetrix[0][2] + ConfusionMetrix[0][3] + ConfusionMetrix[0][4] +
                                       ConfusionMetrix[1][2] + ConfusionMetrix[1][3] + ConfusionMetrix[1][4])
    
    SitStand_ConfusionMetrics[1][0] = (ConfusionMetrix[2][0] + ConfusionMetrix[2][1] + 
                                       ConfusionMetrix[3][0] + ConfusionMetrix[3][1] + 
                                       ConfusionMetrix[4][0] + ConfusionMetrix[4][1])
    
    SitStand_ConfusionMetrics[1][1] = (ConfusionMetrix[2][2] + ConfusionMetrix[2][3] + ConfusionMetrix[2][4] +
                                       ConfusionMetrix[3][2] + ConfusionMetrix[3][3] + ConfusionMetrix[3][4] +
                                       ConfusionMetrix[4][2] + ConfusionMetrix[4][3] + ConfusionMetrix[4][4])
    
    File = open(f'{ResultPathDir}{ClassifierName}.txt', 'a+')
    '''
    print('ConfusionMatrix')
    pprint.pprint(SitStand_ConfusionMetrics)
    '''
    File.write('Inference for sit-stand \n')
    File.write('SitStand_ConfusionMetrics \n')
    File.write(np.array2string(SitStand_ConfusionMetrics))
    File.write('\n \n')
    
    '''00 01'''
    '''10 11'''
    
    #print('PrecissionList')
    PrecissionMetrics = np.full((2), 0, dtype=float)
    PrecissionMetrics[0] = SitStand_ConfusionMetrics[0][0] / (SitStand_ConfusionMetrics[0][0] +
                                                                 SitStand_ConfusionMetrics[1][0])
    
    PrecissionMetrics[1] = SitStand_ConfusionMetrics[1][1] / (SitStand_ConfusionMetrics[1][1] +
                                                                 SitStand_ConfusionMetrics[0][1])
    
    
    File.write('PrecissionMetrics \n')
    File.write(np.array2string(PrecissionMetrics))
    File.write('\n \n')
    
    #print('RecallList')
    
    RecallMetrics = np.full((2), 0, dtype=float)
    RecallMetrics[0] = (SitStand_ConfusionMetrics[0][0] /(SitStand_ConfusionMetrics[0][0] +
                                                          SitStand_ConfusionMetrics[0][1]))
    
    RecallMetrics[1] = (SitStand_ConfusionMetrics[1][1] / (SitStand_ConfusionMetrics[1][1] +
                                                          SitStand_ConfusionMetrics[1][0]))
    
    
    #pprint.pprint(RecallMetrics)
    File.write('RecallMetrics \n')
    File.write(np.array2string(RecallMetrics))
    File.write('\n \n')
    
    Accuracy = ((SitStand_ConfusionMetrics[0][0] + SitStand_ConfusionMetrics[1][1]) /
                
                (SitStand_ConfusionMetrics[0][0] + SitStand_ConfusionMetrics[0][1] +
                 SitStand_ConfusionMetrics[1][0] + SitStand_ConfusionMetrics[1][1]))
    
    '''
    print('OverallAccuracy')
    pprint.pprint(Accuracy)
    '''
    File.write('Accuracy \n')
    File.write(np.array2string(Accuracy))
    File.write('\n \n')
    File.close()


def FetchMetrics(YTest, predictions, MetricsDict):
    '''
    input: The label list, prediction list and metric dictionary
    output: The Metric dict containing the performance metric of the classifier
    function: It computes different performance metrics using the label list and prediction list, and store them in the metric dictionary
    '''
    
    PrecissionValue = precision_score(YTest,predictions,average=None,labels = [0,1,2,3,4])
    RecallValue = recall_score(YTest,predictions,average=None, labels = [0,1,2,3,4])
    F1ScoreValue = f1_score(YTest,predictions,average=None,labels = [0,1,2,3,4])
    ConfusionMatrixValue = confusion_matrix(YTest,predictions,labels = [0,1,2,3,4])
    AccuracyValue = accuracy_score(YTest,predictions)
    '''
    print('PrecissionValue')
    pprint.pprint(PrecissionValue)
    
    print('RecallValue')
    pprint.pprint(RecallValue)
    
    print('F1ScoreValue')
    pprint.pprint(F1ScoreValue)
    
    
    print('ConfusionMatrixValue')
    pprint.pprint(ConfusionMatrixValue)
    
    print('AccuracyValue')
    print(AccuracyValue)
    
    input()
    '''
    MetricsDict['ConfusionMatrix'] += ConfusionMatrixValue
    MetricsDict['PrecissionList'].append(PrecissionValue)
    MetricsDict['RecallList'].append(RecallValue)
    MetricsDict['F1ScoreList'].append(F1ScoreValue)
    MetricsDict['OverallAccuracy'].append(AccuracyValue)
    
    return(MetricsDict)


