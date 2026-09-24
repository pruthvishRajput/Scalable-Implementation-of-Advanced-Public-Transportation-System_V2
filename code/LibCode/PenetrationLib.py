#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import random
import math
import pprint
import matplotlib.pyplot as plt
import numpy as np


def PeakHourCrowdCountBasedOnPenetration (BusRate, PtDemandDF_Route1, PerStopPenetratationIndex, BusesPropositionN, CommuterThreshold,  BusCapacity): 
    '''
    input: The bus frequency, route demand, transportation modality proportion, threshold of commuters for crowdedness computation, and the passenger capacity of bus.
    output: Proportion of crowded segments
    function: It computes the proportion of crowded segments using the provided information. 
    '''
    NumberOfBuses = int(round( 60 / BusRate))

    #print('NumberOfBuses: ', NumberOfBuses)
    CrowdednessCount = 0
    NumberOfSegments = PtDemandDF_Route1.shape[0] 
    #print('NumberOfSegments',NumberOfSegments)
    for RowNumber, Series in PtDemandDF_Route1.iterrows():

        TotalPassengers  = int(round(BusesPropositionN  * Series['PHPDT_10']))
        PerBusPassengers =  int(round(TotalPassengers / NumberOfBuses))

        TotalCommutersUsingApplication = math.floor(PerBusPassengers * PerStopPenetratationIndex)

        if PerBusPassengers > BusCapacity: 
            PerBusSittingPassengers = BusCapacity
            PerBusStandingPassengers = PerBusPassengers - BusCapacity

            '''
            Equally select the number of commuters using the commuter module app 
            from both stading and sitting commuters
            '''

            SittingCommutersUsingOurApplication = int(round((PerBusSittingPassengers / PerBusPassengers)
                                                            * TotalCommutersUsingApplication))
            StandingCommutersUsingOurApplication = int(round((PerBusStandingPassengers / PerBusPassengers)
                                                             * TotalCommutersUsingApplication))

        if PerBusPassengers < BusCapacity:
            PerBusSittingPassengers = PerBusPassengers
            PerBusStandingPassengers = 0

            SittingCommutersUsingOurApplication = TotalCommutersUsingApplication
            StandingCommutersUsingOurApplication = 0
            
        if SittingCommutersUsingOurApplication >= CommuterThreshold or StandingCommutersUsingOurApplication >= CommuterThreshold:
            #print("Crowdedness detected")
            CrowdednessCount += 1

        #else:
            #print("Crowdedness not detected")
        #input()
    return(CrowdednessCount/NumberOfSegments * 100)


def ApplyPenetrationAndGetCrowdCount(BusRate , PtDemandDF_Route, BusesPropositionN, CommuterThreshold, BusCapacity):
    '''
    input: The bus frequency, route demand, transportation modality proportion, threshold of commuters for crowdedness computation, and the passenger capacity of bus.
    output: The tuple of different penetration values and the proportion of crowded segments which can be computed for the correspoding penetration value.
    function: It computes the crowded segments based on the provided information and varying penetration values. 
    '''
    #BusRate = random.randrange(PeakHourBusesRange[0],PeakHourBusesRange[1])

    PenetrationList = []
    FractionOfRouteList = []
    for PenetratationRate in range(0,100):

        PerStopPenetratationIndex = PenetratationRate / 100
        #print(PerStopPenetratationIndex, PenetratationRate)

        FractionOfRecognizedCrowdedRoute =  PeakHourCrowdCountBasedOnPenetration(BusRate,  PtDemandDF_Route, PerStopPenetratationIndex, BusesPropositionN, CommuterThreshold, BusCapacity)



        PenetrationList.append(PenetratationRate)
        FractionOfRouteList.append(FractionOfRecognizedCrowdedRoute)
        
    return(PenetrationList, FractionOfRouteList)


def PenetrationAnalysisPlot(BusRate, PtDemandDF_Route1, PtDemandDF_Route2, PtDemandDF_Route3, PtDemandDF_Route4, BusesPropositionN, CommuterThreshold, BusCapacity, ResultPathDir):
	'''
	input: The bus frequency, route demand of different routes, transportation modality proportion, threshold of commuters for crowdedness computation, and the passenger capacity of bus. 
	output: None
	function: It applies the penetration based on the provided information and plots the curve of the crowdedness detection for different penetration rate.
	'''
	PenetrationList1, FractionOfRouteList1 = ApplyPenetrationAndGetCrowdCount(BusRate, PtDemandDF_Route1, BusesPropositionN, CommuterThreshold, BusCapacity)
	PenetrationList2, FractionOfRouteList2 = ApplyPenetrationAndGetCrowdCount(BusRate, PtDemandDF_Route2, BusesPropositionN, CommuterThreshold, BusCapacity)
	PenetrationList3, FractionOfRouteList3 = ApplyPenetrationAndGetCrowdCount(BusRate, PtDemandDF_Route3, BusesPropositionN, CommuterThreshold, BusCapacity)
	PenetrationList4, FractionOfRouteList4 = ApplyPenetrationAndGetCrowdCount(BusRate, PtDemandDF_Route4, BusesPropositionN, CommuterThreshold, BusCapacity)


	fig, ax = plt.subplots()
	#ax.plot(x, y)
	ax.plot(PenetrationList1, FractionOfRouteList1, 'ro-', markevery=2, label = 'Route: 1', markerfacecolor="None")
	ax.plot(PenetrationList2, FractionOfRouteList2, 'b^-', markevery=2, label = 'Route: 2', markerfacecolor="None")
	ax.plot(PenetrationList3, FractionOfRouteList3, 'gs-', markevery=2, label = 'Route: 3', markerfacecolor="None")
	ax.plot(PenetrationList4, FractionOfRouteList4, 'kx-', markevery=2, label = 'Route: 4', markerfacecolor="None")

	'''
	if CommuterThreshold ==3:
		ax.set_xlim([0,65])
	else:
		ax.set_xlim([0,45])
	'''

	ax.set_xlim([0,65])

	'''
	if CommuterThreshold ==3:
		plt.xticks([0,5,10,15,20,25,30,35,40,45,50,55,60,65])
	else:
		plt.xticks([0,5,10,15,20,25,30,35,40,45])
	'''
	plt.xticks([0,5,10,15,20,25,30,35,40,45,50,55,60,65])

	plt.yticks([0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100])

	if CommuterThreshold ==3:
		plt.axvline(x=12,linestyle='dashed',color='k')
	else:
		plt.axvline(x=8,linestyle='dashed',color='k')

	ax.legend()

	plt.ylabel('Crowdedness detected route segments (in %)')
	#plt.ylabel('Fraction of route segments')
	plt.xlabel('Penetration level (in %)')

	plt.tight_layout()

	plt.savefig(f'{ResultPathDir}PenetrationAnalysisForCountOf{CommuterThreshold}_WithMarker.png',dpi = 600)
	plt.show()

