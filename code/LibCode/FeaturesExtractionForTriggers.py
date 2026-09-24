import numpy as np
from numpy.lib.stride_tricks import as_strided

from pymongo import     MongoClient

con = MongoClient()

import pprint

import math
from collections import Counter

def windowed_view(arr, window, overlap):
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
def ComputeFeatureForComponents(RouteName,AcclRecords,ModeInt,Window,SingleTripInfo):
	AcclH = [AclR['HorizontalComponent'] for AclR in AcclRecords]
	AcclV = [AclR['VerticalComponent'] for AclR in AcclRecords]
	Speed = [Rec['Speed'] if Rec['Speed']!="NA" else -1 for Rec in AcclRecords]
	TriggerMode = [AclR['Mode'] for AclR in AcclRecords]    

	AcclH = np.asarray(AcclH)
	#ComputeFeature(Component,ModeInt,Window,'BodyAcclX','Axis')
	AcclV = np.asarray(AcclV)
	Speed = np.asarray(Speed)
	TimeBetweenSamples = 1/40

	'''
	BodyAcclX, BodyAcclY, BodyAcclZ , GravityX, GravityY, GravityZ, GyroX, GyroY, GyroZ = ApplyWindow(BodyAcclX, BodyAcclY, BodyAcclZ,
		                                                                                              GravityX, GravityY, GravityZ,
		                                                                                              GyroX, GyroY, GyroZ,
		                                                                                             Window)
	'''             
	AcclH, AcclV, Speed, TriggerMode = ApplyWindow(AcclH, AcclV, Speed, TriggerMode, Window)
	'''
	ComputeFeature (BodyAcclX,BodyAcclY,BodyAcclZ,
		            GravityX, GravityY, GravityZ, 
		            GyroX, GyroY, GyroZ,
		            ModeInt,Window,SingleTripInfo)#,ComponentType)
	'''
	ComputeFeature (RouteName,AcclH, AcclV, Speed, TriggerMode,ModeInt, Window, SingleTripInfo)#,ComponentType)

'''
def ApplyWindow(BodyAcclX, BodyAcclY, BodyAcclZ,
                GravityX, GravityY, GravityZ,
                GyroX, GyroY, GyroZ, 
                Window):
'''
def ApplyWindow(AcclH, AcclV, Speed, TriggerMode, Window):
	#print('shape: ')
	#print(BodyAcclX.shape)
	WindowLength = Window
	Overlap = int(WindowLength / 2)

	AcclH = windowed_view(AcclH, WindowLength,Overlap)
	AcclV = windowed_view(AcclV, WindowLength,Overlap)
	Speed = windowed_view(Speed, WindowLength,Overlap)
	TriggerMode = windowed_view(TriggerMode, WindowLength,Overlap)

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
	return (AcclH, AcclV, Speed, TriggerMode)

def GetMag(WBodyAcclX,WBodyAcclY):#,WBodyAcclZ):
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
def ComputeFeature (RouteName,AcclH, AcclV, Speed, TriggerMode,ModeInt, Window, SingleTripInfo):#,ComponentType)
	SamplingFreq = 40
	TimeBetweenSamples = 1/40
	index = 0
	# W for Windowed segment
	#for (WBodyAcclX,WBodyAcclY,WBodyAcclZ, WGravityX, WGravityY, WGravityZ, WGyroX, WGyroY, WGyroZ) in zip(BodyAcclX,BodyAcclY,BodyAcclZ, GravityX, GravityY, GravityZ, GyroX, GyroY, GyroZ):
	for (WAcclH , WAcclV, WSpeed, WTriggerMode) in zip (AcclH , AcclV, Speed, TriggerMode):
		FeaturesDict = {}
		
		FeaturesDict = TimeDomainFeatures(WAcclH,FeaturesDict,'TimeAcclH')
		#FeaturesDict = FrequencyComponent(WAcclH,Window,SamplingFreq,FeaturesDict,'FreqAcclH')
		
		FeaturesDict = TimeDomainFeatures(WAcclV,FeaturesDict,'TimeAcclV')
		#FeaturesDict = FrequencyComponent(WAcclV,Window,SamplingFreq,FeaturesDict,'FreqAcclV')
		
		#FeaturesDict = CorrelationBetweenAxis(WAcclH, WAcclV, 'TimeAccl',FeaturesDict)

		'''Jerk'''
		'''
		JerkH = np.ediff1d(WAcclH)#/TimeBetweenSamples
		JerkV = np.ediff1d(WAcclV)#/TimeBetweenSamples

		FeaturesDict = TimeDomainFeatures(JerkH,FeaturesDict,'TimeJerkH')
		FeaturesDict = FrequencyComponent(JerkH,Window,SamplingFreq,FeaturesDict,'FreqJerkH')
		
		FeaturesDict = TimeDomainFeatures(JerkV,FeaturesDict,'TimeJerkV')
		FeaturesDict = FrequencyComponent(JerkV,Window,SamplingFreq,FeaturesDict,'FreqJerkV')
		'''
		#FeaturesDict = CorrelationBetweenAxis(JerkH, JerkV, 'TimeJerk',FeaturesDict)
		
		
		'''AccMag'''
		#AcclMag = GetMag(WAcclH,WAcclV)
		#FeaturesDict = TimeDomainFeatures(AcclMag,FeaturesDict,'TimeAcclMag')
		#FeaturesDict = FrequencyComponent(AcclMag,Window,SamplingFreq,FeaturesDict,'FreqAcclMag')

		
		'''JerkMag'''
		#JerkMag = GetMag(JerkH,JerkV)
		#JerkMag = np.linalg.norm([JerkX,JerkY,JerkZ])
		#FeaturesDict = TimeDomainFeatures(JerkMag,FeaturesDict,'TimeJerkMag')
		#FeaturesDict = FrequencyComponent(JerkMag,Window,SamplingFreq,FeaturesDict,'FreqJerkMag')

		FeaturesDict['ModeInt'] = float(ModeInt) 
		FeaturesDict['index'] = index
		
		#FeaturesDict['TriggerMode'] = mode(WTriggerMode) # List of modes
		FeaturesDict['TriggerMode'] = Counter(WTriggerMode) # List of modes
		FeaturesDict['Speed'] = np.mean(WSpeed)
		con[RouteName][SingleTripInfo+'.HARFeatureForTrigger'].insert_one(FeaturesDict)
		index+=1
		#pprint.pprint(FeaturesDict)
		#print(len(FeaturesDict))
		#input()

#def CorrelationBetweenAxis(WBodyAcclX,WBodyAcclY,WBodyAcclZ, ComponentType,FeaturesDict):
def CorrelationBetweenAxis(WAcclH, WAcclV, ComponentType,FeaturesDict):
    
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
from statistics import mode

def TimeDomainFeatures(WindowIntervalNp,FeaturesDict,ComponentType):
#def TimeDomainFeatures(window,FeaturesDict,ComponentType):
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

	''' For triggers'''
	FeaturesDict['STDByMean'+ComponentType] = WindowIntervalMean / np.std(WindowIntervalNp)
	Q4 = np.percentile(WindowIntervalNp, 100)
	Q3 = np.percentile(WindowIntervalNp, 75)
	Q2 = np.percentile(WindowIntervalNp, 50)
	Q1 = np.percentile(WindowIntervalNp, 25)

	if Q3 != 0:
		FeaturesDict['Q4ByQ3'+ComponentType] = Q4/Q3
	else:
		FeaturesDict['Q4ByQ3'+ComponentType] = np.nan

	if Q2 != 0:
		FeaturesDict['Q4ByQ2'+ComponentType] = Q4/Q2
		FeaturesDict['Q3ByQ2'+ComponentType] = Q3/Q2
	else:
		FeaturesDict['Q4ByQ2'+ComponentType] = np.nan
		FeaturesDict['Q3ByQ2'+ComponentType] = np.nan
	
	if Q1 != 0:
		FeaturesDict['Q4ByQ1'+ComponentType] = Q4/Q1
		FeaturesDict['Q3ByQ1'+ComponentType] = Q3/Q1
		FeaturesDict['Q2ByQ1'+ComponentType] = Q2/Q1
	
	else:
		FeaturesDict['Q4ByQ1'+ComponentType] = Q4/Q1
		FeaturesDict['Q3ByQ1'+ComponentType] = Q3/Q1
		FeaturesDict['Q2ByQ1'+ComponentType] = Q2/Q1

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
    LowerRange =int(round(LowerRangeFreq*Window/SamplingFreq))+1
    UpperRange =int(round(UpperRangeFreq*Window/SamplingFreq))
    
    MagInInterval = [SquareMag[i] for i in range(LowerRange,UpperRange+1)]
    
    return(sum(MagInInterval))
