import numpy as np
import pandas as pd
import os
import pysiology.electromyography as electromyography
from itertools import combinations

# This data set contains only 8 channels of EMG signals (no MMG data)

print(" ")

results_folder = 'results/Barbara_13_05_2022_AB/'
main_folder = 'C:/Users/alepa/Desktop/MGR/datasets/Barbara_13_05_2022_AB/'
folder_path = results_folder
os.makedirs(folder_path, exist_ok=True)  
classes_array = ['1', '2', '3', '4', '5']

WL_table = []
ZC_table = []
VAR_table = []
MAV_table = []
SSC_table = []

for class_number in classes_array:
    for file_index, filename in enumerate(os.listdir(main_folder+class_number)):

        dataset = pd.read_csv(main_folder+class_number+'/'+filename, sep=";", decimal=",", header=None)

        WL_arr = np.zeros(9)
        ZC_arr = np.zeros(9).astype(int)
        VAR_arr = np.zeros(9)
        MAV_arr = np.zeros(9)
        SSC_arr = np.zeros(9).astype(int)

        for idx, col in enumerate(dataset.columns):
            column = dataset.loc[:, col]
            y = column.to_numpy()

            # Get the waveform length of the signal, a measure of complexity of the EMG Signal.
            WL_arr[idx] = electromyography.getWL(y)
            # How many times does the signal crosses the 0 (+-threshold).
            ZC_arr[idx] = electromyography.getZC(y, threshold=1)
            # Summation of average square values of the deviation of a variable.
            VAR_arr[idx] = electromyography.getVAR(y)
            # Thif functions compute the average of EMG signal Amplitude - Mean Absolute Value
            MAV_arr[idx] = electromyography.getMAV(y)
            # Number of times the slope of the EMG signal changes sign.
            SSC_arr[idx] = electromyography.getSSC(y, threshold=1)

        WL_arr[8] = int(class_number)
        ZC_arr[8] = int(class_number)
        VAR_arr[8] = int(class_number)
        MAV_arr[8] = int(class_number)
        SSC_arr[8] = int(class_number)      

        WL_table.append(WL_arr)
        ZC_table.append(ZC_arr)
        VAR_table.append(VAR_arr)
        MAV_table.append(MAV_arr)
        SSC_table.append(SSC_arr)

    print(f"Class {class_number} processed...")

headers = ["1", "2", "3", "4", "5", "6", "7", "8", "class"]
WL_df = pd.DataFrame(columns=headers, data=WL_table)
WL_df = WL_df.astype({"class": int})
ZC_df = pd.DataFrame(columns=headers, data=ZC_table)
ZC_df = ZC_df.astype({"class": int})
VAR_df = pd.DataFrame(columns=headers, data=VAR_table)
VAR_df = VAR_df.astype({"class": int})
MAV_df = pd.DataFrame(columns=headers, data=MAV_table)
MAV_df = MAV_df.astype({"class": int})
SSC_df = pd.DataFrame(columns=headers, data=SSC_table)
SSC_df = SSC_df.astype({"class": int})

list_combinations_tables = list()
list_combinations_names= list()
list_of_methods_tables = [WL_df, ZC_df, VAR_df, MAV_df, SSC_df]
list_of_methods_names = ["WL", "ZC", "VAR", "MAV", "SSC"]

for n in range(len(list_of_methods_tables) + 1):
    list_combinations_tables += list(combinations(list_of_methods_tables, n))
for n in range(len(list_of_methods_names) + 1):
    list_combinations_names += list(combinations(list_of_methods_names, n))

for comb_id, comb in enumerate(list_combinations_names):
    if len(comb) > 1:
        comb_name = '_'.join(comb)
        print(comb_name)
        comb_df = pd.concat(list_combinations_tables[comb_id], axis=1)
        comb_df = comb_df.loc[:,~comb_df.T.duplicated(keep='last')] #remove duplicate columns except last
        comb_df.to_csv(f'{folder_path}features_{comb_name}.csv', header=False, index=False)

print("\n\nFINISHED SUCCESSFULLY")