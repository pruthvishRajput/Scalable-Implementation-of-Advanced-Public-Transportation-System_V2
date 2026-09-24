#!/usr/bin/env python
# coding: utf-8

import subprocess
import os
import sys
import json
from pymongo import     MongoClient

con = MongoClient()

from scipy import integrate

import numpy as np

import pprint

import math

from numpy.lib.stride_tricks import as_strided
# In[50]:

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


def ComputeFeature(BMSingleTripInfo,Component,ModeInt,Window,RecordType,RouteName):
	'''
	input: Trips list, windowed accelerometer records, transport mode value, and trip segment type (Record type)
	output: None 
	function: It computes the time-domain and frequency domain features from the windowed accelerometer records and save it in MongoDB.
	'''
	#Window = IntervalLength # = 160 #4 sec

	#WComponent = windowed_view(Component,Window,0)
	WComponent = windowed_view(Component,Window,int(Window/2))

	#TotalPoint = math.ceil(len(Component)/Window)
	IntervalLength =Window
    
	for Record in WComponent:
		WindowIntervalH = [EAcc['HorizontalComponent'] for EAcc in Record]
		WindowIntervalV = [EAcc['VerticalComponent'] for EAcc in Record]

		#WindowIntervalH = RemoveSpikes(WindowIntervalH)
		#WindowIntervalV = RemoveSpikes(WindowIntervalV)


		FeaturesDict ={}
		'''Time domain features'''
		FeaturesDict['StartGPSIndex'] = float(Record[0][ 'GPSIndex'])
		FeaturesDict['StartAcclIndex'] = float(Record[0][ 'AcclIndex'])

		FeaturesDict = TimeDomainFeatures(WindowIntervalH,FeaturesDict,'H')

		'''Frequency component'''
		SamplingFreq = 40
		FeaturesDict = FrequencyComponent(WindowIntervalH,Window,SamplingFreq,FeaturesDict,'H')

		'''Time domain features'''
		FeaturesDict = TimeDomainFeatures(WindowIntervalV,FeaturesDict,'V')

		'''Frequency component'''
		FeaturesDict = FrequencyComponent(WindowIntervalV,Window,SamplingFreq,FeaturesDict,'V')

		FeaturesDict['ModeInt'] = float(ModeInt)

		con[RouteName][BMSingleTripInfo+'.TransportFeatures'+RecordType].insert_one(FeaturesDict)
        
def RemoveSpikes(WindowIntervalH):
	'''
	input: Windowed acceleration records with noisy spikes
	output: Windowed acceleration records with the removal of noisy spikes
	function: It removes the noisy spikes in the windowed accelerometer record
	'''
	Q1 = np.percentile(WindowIntervalH,25)
	Q2 = np.percentile(WindowIntervalH,50)
	Q3 = np.percentile(WindowIntervalH,75)
	Q4 = np.percentile(WindowIntervalH,100)
		
	OneHalfIQRP = Q3 + 1.5 * (Q3-Q1)
	OneHalfIQRN = Q1 - 1.5 * (Q3-Q1)

	Mean = np.mean(WindowIntervalH)

	for indexi,Record in enumerate(WindowIntervalH):

		if Record< OneHalfIQRN or Record > OneHalfIQRP:
			#print(WindowIntervalH[indexi])
			WindowIntervalH[indexi]=Mean
			#print(WindowIntervalH[indexi])
			#input()
	return(WindowIntervalH)


def TimeDomainFeatures(WindowIntervalNp,FeaturesDict,ComponentType):
	'''
	input: Windowed accelerometer records, Feature Dictonary and feature type
	output: The dictionary having the feature values
	function: It computes the time-domain from the windowed accelerometer records and stores it in the feature dictionary. 
	'''
	WindowIntervalMean = np.mean(WindowIntervalNp)
	FeaturesDict['Mean'+ComponentType] = WindowIntervalMean
	FeaturesDict['STD'+ComponentType] = np.std(WindowIntervalNp)

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

	return (FeaturesDict)


# In[32]:


from scipy.stats import entropy


# In[33]:


def FrequencyComponent(WindowIntervalNp,Window,SamplingFreq,FeaturesDict,ComponentType):
	'''
	input: Windowed accelerometer records, Feature Dictonary and feature type
	output: The dictionary having the feature values
	function: It computes the frequency-domain from the windowed accelerometer records and stores it in the feature dictionary. 
	'''
	spX = np.fft.fft(WindowIntervalNp)

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
	MaxIndex = float(MagList.index(max(MagList)))
	PeakFreq = int(round(MaxIndex * SamplingFreq / Window))
	FeaturesDict['PeakFreq'+ComponentType] = PeakFreq

	'''2Hz,3Hz,5Hz FFT co-eff'''
	TwoHzMag = MagList[int(round(2*Window/SamplingFreq))]

	ThreeHzMag = MagList[int(round(3*Window/SamplingFreq))]

	FiveHzMag = MagList[int(round(5*Window/SamplingFreq))]

	FeaturesDict['TwoHzMag'+ComponentType]= TwoHzMag
	FeaturesDict['ThreeHzMag'+ComponentType]= ThreeHzMag
	FeaturesDict['FiveHzMag'+ComponentType]= FiveHzMag

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
	return (FeaturesDict)


# In[34]:


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


