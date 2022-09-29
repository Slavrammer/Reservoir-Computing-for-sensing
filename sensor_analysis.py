import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re

# function for loading data, background correction, data normalisation (vs 1st peak in the loop0 file of given
# series) and analysis
def Normalize(root, filename):
    global data, peak_mean
    # Load data
    raw_data = pd.read_csv(root + "\\" + filename, sep='\t')
    # Parse string to float
    raw_data['Analog IN 1/V'] = pd.to_numeric(
        raw_data['Analog IN 1/V'].apply(lambda x: re.sub(',', '.', str(x))))

    # Parsing data to numpy array
    raw_data = raw_data['Analog IN 1/V']
    data = raw_data.to_numpy()

    # Background correction (vs first 2000 points of each file)
    bg_mean = np.mean(data[:2000])
    data = data - bg_mean

    # Normalization to 1 vs first peak in series
    if filename.endswith('loop0.txt'):
        peak_mean = np.mean(data[3250:3400])
    data = data / peak_mean

    return data

# Collect values of peaks into data bins
def Analyse(data):
    global first_peak_values
    global second_peak_values
    global third_peak_values

    first_peak_values = np.append(first_peak_values, np.mean(data[3450:3510]))
    second_peak_values = np.append(second_peak_values, np.mean(data[6450:6510]))
    third_peak_values = np.append(third_peak_values, np.mean(data[9450:9510]))

# Calculate mean and standard error across repeated data samples
def Mean_STE(x, y, z):
    global mean
    global ste

    mean = (x + y + z) / 3
    deviation1 = abs((x - mean)) ** 2
    deviation2 = abs((y - mean)) ** 2
    deviation3 = abs((z - mean)) ** 2
    variance = (deviation1 + deviation2 + deviation3) / 3
    std = np.sqrt(variance)
    ste = std / np.sqrt(3)
    SaveToFile()
    return mean, ste

def SaveToFile():
    print(root)
    mean_save = pd.DataFrame(mean, columns=["1st peak",'2nd peak', '3rd peak'])
    ste_save = pd.DataFrame(ste, columns=["1st peak", '2nd peak', '3rd peak'])
    mean_save.to_csv(r'{}\mean'.format(root), index=False, sep='\t')
    ste_save.to_csv(r'{}\std'.format(root), index=False, sep='\t')

# Sorting files by enumerator of loop. Different filenames are allowed, only the ending matters
def Sorting_filenames(filename_list):
    for x in filename_list:
        x = x[-6:]
        x = x[:2]
        try:
            x = int(x)
        except:
            x = x[1]
            x = int(x)
        x_list.append(x)

# Data bins
collected_peaks1 = np.array([])
collected_peaks2 = np.array([])
collected_peaks3 = np.array([])

# Walking over all folders
walk = "D:\\Doc\\Projekty\\rezerwura TiO2\export"
for root, dirs, files in os.walk(walk, topdown=False):
    # Control over current directory and sorting of files
    print("Root:" + root)
    try:
        folder_number = int(root[-1])
    except:
        folder_number = 0
    x_list = []
    Sorting_filenames(files)
    sorted_filenames = [x for _, x in sorted(zip(x_list, files))]

    # Data bins
    first_peak_values = np.array([])
    second_peak_values = np.array([])
    third_peak_values = np.array([])

    iterator = 0
    # Analysis of all files in given directory walk
    for filename in sorted_filenames:
        if filename.endswith(".txt"):
            Normalize(root, filename)
            Analyse(data)
            iterator += 1

            # Collect all the peaks for further processing (mean, standard error)
            if iterator == 21:
                if folder_number == 1:
                    collected_peaks1 = np.stack((first_peak_values, second_peak_values, third_peak_values), axis=1)
                    # print(collected_peaks1)
                elif folder_number == 2:
                    collected_peaks2 = np.stack((first_peak_values, second_peak_values, third_peak_values), axis=1)
                    # print(collected_peaks2)
                elif folder_number == 3:
                    collected_peaks3 = np.stack((first_peak_values, second_peak_values, third_peak_values), axis=1)
                    # print(collected_peaks3)
                else:
                    pass

            if iterator == 21 and folder_number == 3:
                Mean_STE(collected_peaks1, collected_peaks2, collected_peaks3)

                # Reset data bins
                collected_peaks1 = np.array([])
                collected_peaks2 = np.array([])
                collected_peaks3 = np.array([])
