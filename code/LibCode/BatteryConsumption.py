#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np


def Analysis(ResultPathDir):
	'''
	input: None
	output: The plot of battery consumption for continuous GPS sensing and opportunistic activation of GPS sensor
	function: The battery consumption plot is created based on the values obtained from battery historian tool
	'''
	Charge_1 = [2902,2901,2898,2890,2888,2883,2873,2866,2863, 
		      2862, 2859, 2857, 2849, 2832, 2828, 2825, 2819,
		      2814, 2796,  2794, 2792, 2790, 2784, 2782, 2780,
		      2775, 2774, 2771, 2768, 2768, 2766, 2764, 2762, 
		      2758, 2756, 2755, 2750, 2748
		     ]
	Times_1 = [57,119,211,63,149,316,273, 65, 59, 
		     113, 59, 281, 600, 165, 81, 233, 161, 595, 84, 93,
		     361, 115, 70, 128, 59, 80, 121, 62, 62, 60, 78, 127, 
		     119, 59, 151, 60, 90
		     
		    ]

	Voltage_1 = [4380, 4310, 4275, 4275, 4275,
		       4275, 4275, 4275, 4275, 4275,
		       4275, 4275, 4275, 4275, 4275,
		       4275, 4254, 4254, 4254, 4254, 
		       4254, 4254, 4254, 4254, 4233,
		       4233, 4233, 4233, 4233, 4233, 
		       4233, 4233, 4233, 4233, 4233, 
		       4233, 4233
		      ]


	Charge_2 = [2887, 2886, 2882, 2880, 2876, 2875, 2869, 2867, 2866, 2863, 2855,
		      2853, 2849, 2847, 2842, 2841, 2840, 2839, 2834, 2833 , 2832, 2830, 
		      2827, 2828, 2824, 2822, 2821, 2819, 2818, 2817
		     ]


	Times_2 = [15, 139, 86, 228, 130, 600, 165, 110, 240, 600, 185, 300, 215, 338,
		    92, 81, 112, 422, 61, 86, 151, 300, 70, 72, 107, 60, 204, 86, 60, 
		    349
		
	]

	Voltage_2 = [4353, 4298, 4263, 4263, 4289, 
		       4289, 4289, 4289, 4289, 4289,
		       4289, 4289, 4289, 4289, 4289,
		       4289, 4289, 4289, 4289, 4289,
		       4289, 4289, 4289, 4289, 4261,
		       4261, 4261, 4261, 4261, 4261,
		       
		      ]


	BatteryConsumptionList1 = []
	for index,(Charge, Time) in enumerate(zip(Charge_1,Times_1)):
		
		#print(index)
		#print(Time, Charge,Charge_1[index],Charge_1[index+1])
		
		CurrentChargeValue = Charge_1[index]
		NextChargeValue = Charge_1[index+1]
		#input()
		for indexj,TimeFrame in enumerate(range(Time-1)):
		    BatteryValue = CurrentChargeValue - (((CurrentChargeValue - NextChargeValue) * (indexj+1)) / (len(range(Time-1))))
		    
		    
		    #print(BatteryValue)
		    BatteryConsumptionList1.append(BatteryValue)
		
		#input()
	#BatteryConsumptionList1

	BatteryConsumptionList2 = []
	for index,(Charge, Time) in enumerate(zip(Charge_2,Times_2)):
		if index +1 < len(Times_2):
		    #print(index)
		    #print(Time, Charge,Charge_2[index],Charge_2[index+1])
		    CurrentChargeValue = Charge_2[index]
		    NextChargeValue = Charge_2[index+1]
		    #input()
		    for indexj,TimeFrame in enumerate(range(Time-1)):
		        BatteryValue = CurrentChargeValue - (((CurrentChargeValue - NextChargeValue) * (indexj+1)) / (len(range(Time-1))))


		        #print(BatteryValue)
		        BatteryConsumptionList2.append(BatteryValue)

		    #input()
		#BatteryConsumptionList2


	BatteryConsumptionList1 = BatteryConsumptionList1[255:-1]

	xTickLabelList =[0,10,20,30,40,50,60,70,80,90]
	xTickList = [0*60,10*60,20*60,30*60,40*60,50*60,60*60,70*60,80*60,90*60]

	BatteryConsumptionList1np = 3080 - 7 - 178 - np.asarray(BatteryConsumptionList1)
	BatteryConsumptionList2np = 3080 - 193 - np.asarray(BatteryConsumptionList2)

	print(BatteryConsumptionList1np[-1],BatteryConsumptionList2np[-1])

	fig, ax = plt.subplots()
	ax.set_xlim([0,90*60])
	plt.plot(BatteryConsumptionList1np, 'ro-', markevery=400, label = 'Continuous Sensing', markerfacecolor="None")
	plt.plot(BatteryConsumptionList2np, 'b^-', markevery=400, label = 'Process scheduling', markerfacecolor="None")
	plt.ylabel("Battery Consumption (in mAh)")
	plt.xlabel("Time (in min)")
	plt.xticks(xTickList, xTickLabelList)
	plt.legend()
	plt.tight_layout()
	plt.savefig(f'{ResultPathDir}PowerConsumption_WithMarker.png', dpi =600)
	plt.show()
