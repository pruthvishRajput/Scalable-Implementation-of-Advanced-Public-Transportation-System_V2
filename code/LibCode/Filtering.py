from scipy.signal import butter, lfilter, stft, medfilt
import pprint
import numpy as np
from pymongo import     MongoClient
con = MongoClient()

def butter_bandpass(lowcut, highcut, fs, order):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	#b, a = butter(order, [low, high], btype='band')
	b, a = butter(order, low, btype='lowpass')
	return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
	b, a = butter_bandpass(lowcut, highcut, fs, order)
	y = lfilter(b, a, data)
	return y

def MedianAverageFiltering(AcclRecordInListX,AcclRecordInListY,AcclRecordInListZ):
	MedAvgAcclRecordInListX = medfilt(AcclRecordInListX,kernel_size=3)
	MedAvgAcclRecordInListY = medfilt(AcclRecordInListY,kernel_size=3)
	MedAvgAcclRecordInListZ = medfilt(AcclRecordInListZ,kernel_size=3)

	return(MedAvgAcclRecordInListX,MedAvgAcclRecordInListY,MedAvgAcclRecordInListZ)

def ButterWorthFiltering(MedAvgAcclRecordInListX,MedAvgAcclRecordInListY,MedAvgAcclRecordInListZ, 
                         LowCutOff, HighCutOff, SamplingFreq, Order):
	FilteredAcclRecordInListX = butter_bandpass_filter(MedAvgAcclRecordInListX,LowCutOff,HighCutOff,SamplingFreq,Order)
	FilteredAcclRecordInListY = butter_bandpass_filter(MedAvgAcclRecordInListY,LowCutOff,HighCutOff,SamplingFreq,Order)
	FilteredAcclRecordInListZ = butter_bandpass_filter(MedAvgAcclRecordInListZ,LowCutOff,HighCutOff,SamplingFreq,Order)

	return(FilteredAcclRecordInListX,FilteredAcclRecordInListY,FilteredAcclRecordInListZ)


def ExtractTypeAndStoreInMongo(RouteName,FilteredAcclRecordInListX,FilteredAcclRecordInListY,FilteredAcclRecordInListZ,
                               SingleTripInfo,AcclMagRecordsListStoppages):
	'''    
	SingleTripInfoSplitted = SingleTripInfo.split('.')
	SingleTripInfoForSave = SingleTripInfoSplitted[1] +'.'+ SingleTripInfoSplitted[2]+'.' + SingleTripInfoSplitted[3]+'.' +SingleTripInfoSplitted[4]
	#print(SingleTripInfoForSave)
	'''
	for index in range(len(FilteredAcclRecordInListX)):
		DictAcclRecord = {}
		DictAcclRecord['X'] = FilteredAcclRecordInListX[index]
		DictAcclRecord['Y'] = FilteredAcclRecordInListY[index]
		DictAcclRecord['Z'] = FilteredAcclRecordInListZ[index]
		DictAcclRecord['GPSIndex'] = AcclMagRecordsListStoppages[index]['GPSIndex']
		DictAcclRecord['AcclIndex'] = AcclMagRecordsListStoppages[index]['AcclIndex']
		
		for key in AcclMagRecordsListStoppages[index]:
			if key == "Mode":
				DictAcclRecord["Mode"] = AcclMagRecordsListStoppages[index][key]
		

		#con[RouteName][SingleTripInfoForSave+'.Filtered.Accl'].insert_one(DictAcclRecord)
		con[RouteName][SingleTripInfo+'.Filtered.Accl'].insert_one(DictAcclRecord)

		#print(DictAcclRecord)
		#print(RouteName,SingleTripInfo+'.Filtered.Accl')
		#input()         


def Filtering(RouteName,AcclMagRecordsListStoppages,SingleTripInfo):
	#X,Y,Z,index

	AcclRecordInListX = [AclR['Ax']/9.80665 for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListY = [AclR['Ay']/9.80665 for AclR in AcclMagRecordsListStoppages]
	AcclRecordInListZ = [AclR['Az']/9.80665 for AclR in AcclMagRecordsListStoppages]

	'''Convert  List to nparray'''
	AcclRecordInListX = np.asarray(AcclRecordInListX)
	AcclRecordInListY = np.asarray(AcclRecordInListY)
	AcclRecordInListZ = np.asarray(AcclRecordInListZ)

	#PlotRawAccData(AcclRecordInListX,AcclRecordInListY,AcclRecordInListZ)

	'''median filtering'''
	MedAvgAcclRecordInListX,MedAvgAcclRecordInListY,MedAvgAcclRecordInListZ = MedianAverageFiltering(AcclRecordInListX,
		                                                                                             AcclRecordInListY,
		                                                                                             AcclRecordInListZ)

	'''Butterworth LPF filtering'''
	LowCutOff = 16
	HighCutOff = 100
	SamplingFreq = 40
	Order = 3
	FilteredAcclRecordInListX,FilteredAcclRecordInListY,FilteredAcclRecordInListZ = ButterWorthFiltering(MedAvgAcclRecordInListX,
		                                                                                                 MedAvgAcclRecordInListY,
		                                                                                                 MedAvgAcclRecordInListZ,
		                                                                                                 LowCutOff, HighCutOff,
		                                                                                                 SamplingFreq, Order)

	'''Based on type extract gravity and linear acc or gyro output and store in mongodb'''
	ExtractTypeAndStoreInMongo(RouteName,FilteredAcclRecordInListX,FilteredAcclRecordInListY,FilteredAcclRecordInListZ,
		                       SingleTripInfo,AcclMagRecordsListStoppages)
	#input()
