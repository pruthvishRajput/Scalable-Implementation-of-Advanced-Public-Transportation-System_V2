#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

import os

#from sklearn.datasets import make_classification
from sklearn.ensemble import ExtraTreesClassifier

from pymongo import     MongoClient
con = MongoClient()
import pymongo


from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix,precision_score, recall_score, f1_score
from sklearn import tree
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from collections import Counter
import pickle

def InitializeMetricsDict(Modes=3):
    '''
    input: The number of classes
    output: The dictonary for handling the performance metrics of the classifier
    function: It initializes the dictonary for handling the performance metrics of the classifier
    '''
    MetricsDict = {}
    MetricsDict['ConfusionMatrix'] = np.full((Modes,Modes), 0, dtype=float)
    MetricsDict['PrecissionList'] = []
    MetricsDict['RecallList'] = []
    MetricsDict['F1ScoreList'] = []
    MetricsDict['OverallAccuracy'] = []
    
    return(MetricsDict)


def GetData(FeatureType, RecordType, SelectedFeatures, SelectedFeatures_Flag):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed.  
    output: The tuple (X,y) of the features and the labels for different transport modes.
    function: It extracts the features of the selected feature set for either the entire trip records or for the segment other than the stoppage segments based the input variables and forms the tuple of Features and corresponding labels for transport modes.
    '''    
    #RouteNameTest = "GIT_ISCON_PDPU_For_Transport_Mode"
    RouteNameTest = "ISCON_PDPU_For_Transport_Mode"
    '''
    print('------------------------------------------------------------------------------------------------')
    print('-------------------------------For ISCON_PDPU_For_Transport_Mode--------------------------------')
    print('------------------------------------------------------------------------------------------------')
    '''
    TripsISCONBus = ['BM.Bus.02_11_2018__07_47_26','BM.Bus.12_11_2018__07_36_10','BM.Bus.01_11_2018__18_30_46',
             'BM.Bus.02_11_2018__18_33_04','BM.Bus.01_11_2018__07_37_32'


             'CM.Bus.01_11_2018__07_37_30','CM.Bus.02_11_2018__07_47_28','CM.Bus.12_11_2018__07_36_18',
             'CM.Bus.02_11_2018__18_33_09','CM.Bus.01_11_2018__18_30_52']

    TripISCONPD =[
             'PD.Bike.25_10_2018__18_32_59','PD.Bike.12_11_2018__18_29_53','PD.Bike.26_10_2018__18_30_54',
             'PD.Bike.01_11_2018__18_30_23','PD.Bike.14_11_2018__18_27_21', 'PD.Bike.19_11_2018__18_31_30',
             'PD.Bike.01_01_2019__17_48_11','PD.Bike.02_01_2019__17_49_45','PD.Bike.04_01_2019__17_49_44',
             'PD.Bike.07_01_2019__16_43_07'

             'PD.Car.30_10_2018__18_30_15','PD.Car.02_11_2018__18_34_22','PD.Car.13_11_2018__18_26_46',
             'PD.Car.20_11_2018__18_30_41','PD.Car.08_01_2019__18_51_12','PD.Car.10_01_2019__17_42_59',
             'PD.Car.11_01_2019__17_57_18','PD.Car.16_01_2019__17_41_04','PD.Car.18_01_2019__11_58_48'

            ]    
    
    RouteType = 'Transport'
        
    X_Bus, Y_Bus = GetFeatures(TripsISCONBus,RouteNameTest, FeatureType, RecordType,
                               SelectedFeatures, SelectedFeatures_Flag, RouteType)


    X_PD, Y_PD = GetFeatures(TripISCONPD,RouteNameTest, FeatureType, RecordType,
                               SelectedFeatures, SelectedFeatures_Flag, RouteType)
    
    
    RouteNameTest = 'HAR_PDPU_SANAND_'
    
    '''
    print('------------------------------------------------------------------------------------------------')
    print('----------------------------For HAR_PDPU_SANAND-------------------------------------------------')
    print('------------------------------------------------------------------------------------------------')
    '''
    
    RouteType = 'SitStand'
    if RecordType == '.Raw':
        SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})]
    else:
        SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxis':True})]
        if len(SingleTripsInfo)==0:
            SingleTripsInfo = [LR['SingleTripInfo'] for LR in con[RouteNameTest]['TripsInfo'].find({'ConvertedToEarthAxisRaw':True})]
        

    #print('SingleTripsInfo', SingleTripsInfo)
    #input()
    X_SitStand, Y_SitStand = GetFeatures(SingleTripsInfo,RouteNameTest, FeatureType, RecordType,
                                         SelectedFeatures, SelectedFeatures_Flag, RouteType)
    
    
    if FeatureType == '.HARFeature':
        '''X,y: For HAR feature-set'''
        X = np.concatenate((X_Bus, X_PD))
        y = np.concatenate((Y_Bus, Y_PD))
    
    else:
        '''X,y: For other feature-set'''
        X = np.concatenate((X_SitStand, X_PD))
        y = np.concatenate((Y_SitStand, Y_PD))
    
    
    '''For other results on the ISCON_PDPU records having transport data'''
    '''
    X = np.concatenate((X_Bus, X_PD))
    y = np.concatenate((Y_Bus, Y_PD))
    '''
    return(X,y)
    

def GetFeatures(SingleTripsInfo,RouteNameTest, FeatureType, RecordType,
                SelectedFeatures, SelectedFeatures_Flag, RouteType):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage') of 'RouteNameTest' route. Subsequently, the tuple of Feature and Data label is formed. The tuple is formed for all the trips listed in 'SingleTripsInfo' list.
    output: The tuple of features and corresponding labels
    function: It exrtracts the features from one of the four feature-set and corresponding labels for the provided trip list.
    '''
    
    XFeatureList = []
    y = []
    '''

    if FeatureType == '.TransportFeatures' and RouteType=='Transport':
        # The transport mode features for ISCON_PDPU route is saved in as: .TransportModeFirstVersionFeatures
        FeatureType = '.TransportModeFirstVersionFeatures'
    '''    
    for SingleTripInfo in SingleTripsInfo:

        FeaturesDictList = [Features for Features in 
                            con [RouteNameTest][SingleTripInfo+FeatureType+RecordType].find().sort([('index',1)])]

        for index in range(len(FeaturesDictList)):
            FeaturesDict = FeaturesDictList[index]
            sortednames=sorted(FeaturesDict.keys(), key=lambda x:x.lower())

            X = []
            for index in sortednames:
                if index == 'ModeInt':
                    if RouteType=='Transport':
                        y.append(int(FeaturesDict['ModeInt']))
                    elif RouteType=='SitStand':
                        '''As it will be bus only'''
                        y.append(0)
                        
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
    
def GetData_User(RouteNameTest, FeatureType, RecordType, SelectedFeatures, SelectedFeatures_Flag):
    '''
    input: The FeatureType, SelectedFeatures, SelectedFeatures_Flag variables are used for selecting the features of one of the four feature-set of the entire trip records (if RecordType is '.Raw') and of the segment other than the stoppage segments (if Record type is '.SegmentOtherThanStoppage'). Subsequently, the tuple of Feature and Data label is formed. 
    output: The tuple (X,y) of the features and the labels for different transport mode.
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


def FetchMetrics(YTest, predictions, MetricsDict):
    '''
    input: The label list, prediction list and metric dictionary
    output: The Metric dict containing the performance metric of the classifier
    function: It computes different performance metrics using the label list and prediction list, and store them in the metric dictionary
    '''    
    PrecissionValue = precision_score(YTest,predictions,average=None,labels = [0,1,2])
    RecallValue = recall_score(YTest,predictions,average=None, labels = [0,1,2])
    F1ScoreValue = f1_score(YTest,predictions,average=None,labels = [0,1,2])
    ConfusionMatrixValue = confusion_matrix(YTest,predictions,labels = [0,1,2])
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
