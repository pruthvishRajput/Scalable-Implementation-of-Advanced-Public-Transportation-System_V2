import numpy as np
from numpy.lib.stride_tricks import as_strided

from pymongo import     MongoClient

con = MongoClient()

import pprint

import math

def windowed_view(arr, window, overlap):
    '''
    input: The list size, window size and overlapvalue
    output: The windowed list with specified overlap
    function: It generates the overlapping windows of the input list with the specified window length and window overlap
    '''

    arr = np.asarray(arr)
    window_step = window - overlap
    new_shape = arr.shape[:-1] + ((arr.shape[-1] - overlap) // window_step,
                                  window)
    new_strides = (arr.strides[:-1] + (window_step * arr.strides[-1],) +
                   arr.strides[-1:])
    return as_strided(arr, shape=new_shape, strides=new_strides)


WindowList = [32,64,128,256,512]
WindowIndex = 2

#def ComputeFeatureForComponents(GravityRecords,BodyAcclRecords,GyroRecords,ModeInt,Window,SingleTripInfo):
def ComputeFeatureForComponents(RouteName,AcclRecords,ModeInt,Window,SingleTripInfo,RecordType):
    
    '''
    input: Trips list, windowed accelerometer records, transport mode value, and trip segment type (Record type)
    output: None 
    function: It computes the time-domain and frequency domain features from the windowed accelerometer records and save it in MongoDB.    
    '''
    
    AcclH = [AclR['HorizontalComponent'] for AclR in AcclRecords]
    AcclV = [AclR['VerticalComponent'] for AclR in AcclRecords]
    
    
    AcclH = np.asarray(AcclH)
    #ComputeFeature(Component,ModeInt,Window,'BodyAcclX','Axis')
    AcclV = np.asarray(AcclV)
    
    TimeBetweenSamples = 1/40

    '''
    BodyAcclX, BodyAcclY, BodyAcclZ , GravityX, GravityY, GravityZ, GyroX, GyroY, GyroZ = ApplyWindow(BodyAcclX, BodyAcclY, BodyAcclZ,
                                                                                                      GravityX, GravityY, GravityZ,
                                                                                                      GyroX, GyroY, GyroZ,
                                                                                                     Window)
    '''             
    AcclH, AcclV = ApplyWindow(AcclH, AcclV, Window)
    '''
    ComputeFeature (BodyAcclX,BodyAcclY,BodyAcclZ,
                    GravityX, GravityY, GravityZ, 
                    GyroX, GyroY, GyroZ,
                    ModeInt,Window,SingleTripInfo)#,ComponentType)
    '''
    ComputeFeature (RouteName,AcclH, AcclV, ModeInt, Window, SingleTripInfo,RecordType)#,ComponentType)

'''
def ApplyWindow(BodyAcclX, BodyAcclY, BodyAcclZ,
                GravityX, GravityY, GravityZ,
                GyroX, GyroY, GyroZ, 
                Window):
'''
def ApplyWindow(AcclH, AcclV, Window):
    '''
    input: The vertical and horizontal acceleration records, and window size
    output: The windowed vertical and horizontal acceleration records
    function: It forms the overlapping window of vertical and horizontal acceleration records
    '''
    #print('shape: ')
    #print(BodyAcclX.shape)
    WindowLength = Window
    Overlap = int(WindowLength / 2)
    
    AcclH = windowed_view(AcclH, WindowLength,Overlap)
    AcclV = windowed_view(AcclV, WindowLength,Overlap)
    '''
    BodyAcclX = windowed_view(BodyAcclX, WindowLength,Overlap)
    BodyAcclY = windowed_view(BodyAcclY, WindowLength,Overlap)
    BodyAcclZ = windowed_view(BodyAcclZ, WindowLength,Overlap)
    
    GravityX = windowed_view(GravityX, WindowLength,Overlap)
    GravityY = windowed_view(GravityY, WindowLength,Overlap)
    GravityZ = windowed_view(GravityZ, WindowLength,Overlap)
    
    GyroX = windowed_view(GyroX, WindowLength,Overlap)
    GyroY = windowed_view(GyroY, WindowLength,Overlap)
    GyroZ = windowed_view(GyroZ, WindowLength,Overlap)
    
    return (BodyAcclX, BodyAcclY, BodyAcclZ, GravityX, GravityY, GravityZ, GyroX, GyroY, GyroZ)
    '''
    return (AcclH, AcclV)

def GetMag(WBodyAcclX,WBodyAcclY):#,WBodyAcclZ):
    '''
    input: X and Y componenet of acceleration
    output: Magnitude of acceleration
    function: It computes the magnitude of the acceleration
    '''
    BodyAcclMag = np.zeros (WBodyAcclX.shape)
    for index in range(WBodyAcclX.shape[0]):
        BodyAcclMag[index] = np.linalg.norm([WBodyAcclX[index],WBodyAcclY[index]])#,WBodyAcclZ[index]])
    return(BodyAcclMag)

'''
def ComputeFeature(BodyAcclX,BodyAcclY,BodyAcclZ,
                    GravityX, GravityY, GravityZ, 
                    GyroX, GyroY, GyroZ,
                    ModeInt,Window,SingleTripInfo):#,ComponentType):
'''
def ComputeFeature (RouteName,AcclH, AcclV, ModeInt, Window, SingleTripInfo,RecordType):#,ComponentType) 
    '''
    input: Trips list, windowed horizontal and vertical accelerometer records, transport mode value, and trip segment type (Record type)
    output: None 
    function: It computes the time-domain and frequency domain features from the windowed horizontal and vertical accelerometer records and save it in MongoDB.
    '''

    SamplingFreq = 40
    TimeBetweenSamples = 1/40
    index = 0
    # W for Windowed segment
    #for (WBodyAcclX,WBodyAcclY,WBodyAcclZ, WGravityX, WGravityY, WGravityZ, WGyroX, WGyroY, WGyroZ) in zip(BodyAcclX,BodyAcclY,BodyAcclZ, GravityX, GravityY, GravityZ, GyroX, GyroY, GyroZ):
    for (WAcclH , WAcclV) in zip (AcclH , AcclV):
        FeaturesDict = {}
        
        FeaturesDict = TimeDomainFeatures(WAcclH,FeaturesDict,'TimeAcclH')
        FeaturesDict = FrequencyComponent(WAcclH,Window,SamplingFreq,FeaturesDict,'FreqAcclH')
        
        FeaturesDict = TimeDomainFeatures(WAcclV,FeaturesDict,'TimeAcclV')
        FeaturesDict = FrequencyComponent(WAcclV,Window,SamplingFreq,FeaturesDict,'FreqAcclV')
        
        FeaturesDict = CorrelationBetweenAxis(WAcclH, WAcclV, 'TimeAccl',FeaturesDict)

        '''Jerk'''
        JerkH = np.ediff1d(WAcclH)/TimeBetweenSamples
        JerkV = np.ediff1d(WAcclV)/TimeBetweenSamples

        FeaturesDict = TimeDomainFeatures(JerkH,FeaturesDict,'TimeJerkH')
        FeaturesDict = FrequencyComponent(JerkH,Window,SamplingFreq,FeaturesDict,'FreqJerkH')
        
        FeaturesDict = TimeDomainFeatures(JerkV,FeaturesDict,'TimeJerkV')
        FeaturesDict = FrequencyComponent(JerkV,Window,SamplingFreq,FeaturesDict,'FreqJerkV')
        
        FeaturesDict = CorrelationBetweenAxis(JerkH, JerkV, 'TimeJerk',FeaturesDict)
        
        
        '''AccMag'''
        AcclMag = GetMag(WAcclH,WAcclV)
        FeaturesDict = TimeDomainFeatures(AcclMag,FeaturesDict,'TimeAcclMag')
        FeaturesDict = FrequencyComponent(AcclMag,Window,SamplingFreq,FeaturesDict,'FreqAcclMag')

        
        '''JerkMag'''
        JerkMag = GetMag(JerkH,JerkV)
        #JerkMag = np.linalg.norm([JerkX,JerkY,JerkZ])
        FeaturesDict = TimeDomainFeatures(JerkMag,FeaturesDict,'TimeJerkMag')
        FeaturesDict = FrequencyComponent(JerkMag,Window,SamplingFreq,FeaturesDict,'FreqJerkMag')

        FeaturesDict['ModeInt'] = float(ModeInt) 
        FeaturesDict['index'] = index
        con[RouteName][SingleTripInfo+'.HARFeature'+RecordType].insert_one(FeaturesDict)
        index+=1
        #pprint.pprint(FeaturesDict)
        #print(len(FeaturesDict))
        #input()

#def CorrelationBetweenAxis(WBodyAcclX,WBodyAcclY,WBodyAcclZ, ComponentType,FeaturesDict):
def CorrelationBetweenAxis(WAcclH, WAcclV, ComponentType,FeaturesDict):

    '''
    input: Windowed horizontal and vertical accelerometer records, feature type, and feature dictionary
    output: Feature dictionary with the correlation value
    function: It computes the correlation between windowed horizontal and vertical accelerometer records
    '''
    
    CorelationCoeff, Pvalue = pearsonr(WAcclH,WAcclV)
    FeaturesDict['CorrelationHV'+ComponentType] = CorelationCoeff
    '''
    CorelationCoeff, Pvalue = pearsonr(WBodyAcclY,WBodyAcclZ)
    FeaturesDict['CorrelationYZ'+ComponentType] = CorelationCoeff

    CorelationCoeff, Pvalue = pearsonr(WBodyAcclX,WBodyAcclZ)
    FeaturesDict['CorrelationXZ'+ComponentType] = CorelationCoeff
    '''
    return(FeaturesDict)

from scipy.stats import entropy, pearsonr
from scipy.stats import iqr
from astropy.stats import median_absolute_deviation
from scipy.stats import skew
from scipy.stats import kurtosis
from scipy import integrate


def TimeDomainFeatures(WindowIntervalNp,FeaturesDict,ComponentType):
#def TimeDomainFeatures(window,FeaturesDict,ComponentType):
	'''
	input: Windowed accelerometer records, Feature Dictonary and feature type
	output: The dictionary having the feature values
	function: It computes the time-domain from the windowed accelerometer records and stores it in the feature dictionary. 
	'''
	WindowIntervalMean = np.mean(WindowIntervalNp)
	FeaturesDict['Mean'+ComponentType] = WindowIntervalMean
	FeaturesDict['STD'+ComponentType] = np.std(WindowIntervalNp)

	#'''
	MeanRemovedComponentNp = WindowIntervalNp - WindowIntervalMean
	MeanCrossingRate = ((MeanRemovedComponentNp[:-1] * MeanRemovedComponentNp[1:]) < 0).sum()
	FeaturesDict['MeanCrossingRate'+ComponentType] = float(MeanCrossingRate)

	#FeaturesDict['ZeroCrossingRate'+ComponentType] = ((WindowIntervalNp[:-1] * WindowIntervalNp[1:]) < 0).sum()

	ThirdQuartile = np.percentile(WindowIntervalNp, 75)
	FeaturesDict['ThirdQuartile'+ComponentType] = ThirdQuartile

	Range = np.amax(WindowIntervalNp)- np.amin(WindowIntervalNp)
	FeaturesDict['Range'+ComponentType] = Range

	RMS = np.sqrt(np.mean(np.square(WindowIntervalNp)))
	FeaturesDict['RMS'+ComponentType] = RMS

	Volume = integrate.simps(WindowIntervalNp)
	FeaturesDict['Volume'+ComponentType] = Volume
	#'''
	'''New features for HAR'''
	#  Max, Min,  Energy (Avg sum of sq), Entropy
	MAD = median_absolute_deviation(WindowIntervalNp)
	FeaturesDict['MAD'+ComponentType] = MAD

	SMA = np.sum(np.abs(WindowIntervalNp)) 
	FeaturesDict['SMA'+ComponentType] = SMA

	IQR = iqr(WindowIntervalNp)
	FeaturesDict['IQR'+ComponentType] = IQR

	FeaturesDict['Max'+ComponentType] = np.amax(WindowIntervalNp)
	FeaturesDict['Min'+ComponentType] = np.amin(WindowIntervalNp)

	'''Calculation of entropy'''
	SquareMag = [WindowIntervalNp[i]*WindowIntervalNp[i] for i in range(len(WindowIntervalNp))]

	SumOfSquareMag = sum(SquareMag)

	#CDFOfSquareMag = [SquareMag[i]/SumOfSquareMag for i in range(len(SquareMag))]
	CDFOfSquareMag = [SquareMag[i]/SumOfSquareMag if SumOfSquareMag!=0 else np.nan for i in range(len(SquareMag))]
	Entropy = entropy(CDFOfSquareMag)

	FeaturesDict['Entropy'+ComponentType] = Entropy
	FeaturesDict['Energy'+ComponentType] = SumOfSquareMag

	return (FeaturesDict)

def FrequencyComponent(WindowIntervalNp,Window,SamplingFreq,FeaturesDict,ComponentType):
	'''
	input: Windowed accelerometer records, Feature Dictonary and feature type
	output: The dictionary having the feature values
	function: It computes the frequency-domain from the windowed accelerometer records and stores it in the feature dictionary. 
	'''
	spX = np.fft.fft(WindowIntervalNp)
	freq = np.fft.fftfreq(len(WindowIntervalNp),1/(SamplingFreq))

	MagList = [math.sqrt(spX.real[i]*spX.real[i]+spX.imag[i]*spX.imag[i]) 
		      for i in range(len(spX))]

	'''Calculation of entropy'''
	SquareMag = [MagList[i]*MagList[i] for i in range(len(MagList))]

	SumOfSquareMag = sum(SquareMag)

	#CDFOfSquareMag = [SquareMag[i]/SumOfSquareMag for i in range(len(SquareMag))]
	CDFOfSquareMag = [SquareMag[i]/SumOfSquareMag if SumOfSquareMag!=0 else np.nan for i in range(len(SquareMag))]

	Entropy = entropy(CDFOfSquareMag)
	FeaturesDict['Entropy'+ComponentType] = Entropy

	'''PeakFreq feature'''
	MaxIndex = MagList.index(max(MagList))
	PeakFreq = float(int(round(MaxIndex * SamplingFreq / Window)))
	FeaturesDict['PeakFreq'+ComponentType] = PeakFreq

	'''2Hz,3Hz,5Hz FFT co-eff'''
	#'''
	TwoHzMag = MagList[int(round(2*Window/SamplingFreq))]

	ThreeHzMag = MagList[int(round(3*Window/SamplingFreq))]

	FiveHzMag = MagList[int(round(5*Window/SamplingFreq))]

	FeaturesDict['TwoHzMag'+ComponentType]= TwoHzMag
	FeaturesDict['ThreeHzMag'+ComponentType]= ThreeHzMag
	FeaturesDict['FiveHzMag'+ComponentType]= FiveHzMag
	#'''
	'''Energy and ratios of energy'''
	'''energy of B1 (0,1], B2 (1,3], B3(3,5],B4(5,16], B1/B2 , B3 /B4, B1 U B2 / B3 U B4 '''
	'''energy of B1 (0,1], B2 (1,3], B3(3,5],B4(5,20], B1/B2 , B3 /B4, B1 U B2 / B3 U B4 '''
	B1Energy = getEnergyInBand(SquareMag,0,1,Window,SamplingFreq)
	B2Energy = getEnergyInBand(SquareMag,1,3,Window,SamplingFreq)
	B3Energy = getEnergyInBand(SquareMag,3,5,Window,SamplingFreq)
	B4Energy = getEnergyInBand(SquareMag,5,20,Window,SamplingFreq)

	if(B2Energy!=0):
		B1ToB2Ratio = B1Energy/B2Energy
	else:
		B1ToB2Ratio = np.nan
	if B4Energy!=0:
		B3ToB4Ratio = B3Energy/B4Energy
	else:
		B3ToB4Ratio = np.nan
	if (B3Energy+B4Energy)!=0:
		B1B2ToB3B4Ratio = (B1Energy+B2Energy)/(B3Energy+B4Energy)
	else :
		B1B2ToB3B4Ratio = np.nan
	FeaturesDict['B1Energy'+ComponentType] = B1Energy
	FeaturesDict['B2Energy'+ComponentType] = B2Energy
	FeaturesDict['B3Energy'+ComponentType] = B3Energy
	FeaturesDict['B4Energy'+ComponentType] = B4Energy

	FeaturesDict['B1ToB2Ratio'+ComponentType] = B1ToB2Ratio
	FeaturesDict['B3ToB4Ratio'+ComponentType] = B3ToB4Ratio

	FeaturesDict['B1B2ToB3B4Ratio'+ComponentType] = B1B2ToB3B4Ratio

	'''New Features for HAR detection'''
	FeaturesDict['TotalEnergy'+ComponentType] = SumOfSquareMag

	WeightedAvg = sum(x * y for x, y in zip(MagList, freq)) / sum(freq)
	FeaturesDict['WeightedAvgFreq'+ComponentType] = WeightedAvg

	FeaturesDict['Skew'+ComponentType] = skew(MagList)
	FeaturesDict['Kurtosis'+ComponentType] = kurtosis(MagList)

	'''New features for HAR preprocessing'''
	#Mean, STD, MAD, Max, Min, SMA, IQR, 

	WindowIntervalMean = np.mean(MagList)
	FeaturesDict['Mean'+ComponentType] = WindowIntervalMean
	FeaturesDict['STD'+ComponentType] = np.std(MagList)

	#'''
	MeanRemovedComponentNp = MagList - WindowIntervalMean
	MeanCrossingRate = ((MeanRemovedComponentNp[:-1] * MeanRemovedComponentNp[1:]) < 0).sum()
	FeaturesDict['MeanCrossingRate'+ComponentType] = float(MeanCrossingRate)

	#FeaturesDict['ZeroCrossingRate'+ComponentType] = ((MagList[:-1] * MagList[1:]) < 0).sum()

	ThirdQuartile = np.percentile(MagList, 75)
	FeaturesDict['ThirdQuartile'+ComponentType] = ThirdQuartile

	Range = np.amax(MagList)- np.amin(MagList)
	FeaturesDict['Range'+ComponentType] = Range

	RMS = np.sqrt(np.mean(np.square(MagList)))
	FeaturesDict['RMS'+ComponentType] = RMS

	Volume = integrate.simps(MagList)
	FeaturesDict['Volume'+ComponentType] = Volume
	#'''
	'''New features for HAR'''
	#  Max, Min,  Energy (Avg sum of sq), Entropy
	MAD = median_absolute_deviation(MagList)
	FeaturesDict['MAD'+ComponentType] = MAD

	SMA = np.sum(np.abs(MagList)) 
	FeaturesDict['SMA'+ComponentType] = SMA

	IQR = iqr(MagList)
	FeaturesDict['IQR'+ComponentType] = IQR

	FeaturesDict['Max'+ComponentType] = np.amax(MagList)
	FeaturesDict['Min'+ComponentType] = np.amin(MagList)

	return (FeaturesDict)


def getEnergyInBand(SquareMag,LowerRangeFreq,UpperRangeFreq,Window,SamplingFreq):
    '''
    input: Frequency domain values, frequency range and sampling frequency value.
    output: Summation of magnitude of frequency in the provided range of the frequency.
    function: It computes the summation of magnitude of frequency in the provided range of the frequency.
    '''
    LowerRange =int(round(LowerRangeFreq*Window/SamplingFreq))+1
    UpperRange =int(round(UpperRangeFreq*Window/SamplingFreq))
    
    MagInInterval = [SquareMag[i] for i in range(LowerRange,UpperRange+1)]
    
    return(sum(MagInInterval))
