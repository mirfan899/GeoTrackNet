# coding: utf-8

"""
A script to merge AIS messages into AIS tracks.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
# sys.path.append("..")
# import utils
import pickle
import copy
import csv
from datetime import datetime
import time
from io import StringIO
from tqdm import tqdm as tqdm


# ## Aruba
LAT_MIN = 9.0
LAT_MAX = 14.0
LON_MIN = -71.0
LON_MAX = -66.0

D2C_MIN = 2000  # meters


# ===============
# ## Est Aruba
LAT_MIN = 4.7
LAT_MAX = 20.5
LON_MIN = 116.8
LON_MAX = 126.6

dataset_path = "./data/csvs"
l_csv_filename = ["api.csv"]

pkl_filename = "clean_csvs_track.pkl"
pkl_filename_train = "clean_csvs_train_track.pkl"
pkl_filename_valid = "clean_csvs_valid_track.pkl"
pkl_filename_test = "clean_csvs_test_track.pkl"

cargo_tanker_filename = "clean_csvs_cargo_tanker.npy"

t_train_min = time.mktime(time.strptime("01/12/2023 00:00:00", "%d/%m/%Y %H:%M:%S"))
t_train_max = time.mktime(time.strptime("15/01/2024 23:59:59", "%d/%m/%Y %H:%M:%S"))
t_valid_min = time.mktime(time.strptime("01/12/2023 00:00:00", "%d/%m/%Y %H:%M:%S"))
t_valid_max = time.mktime(time.strptime("15/01/2024 23:59:59", "%d/%m/%Y %H:%M:%S"))
t_test_min = time.mktime(time.strptime("01/12/2023 00:00:00", "%d/%m/%Y %H:%M:%S"))
t_test_max = time.mktime(time.strptime("15/01/2024 23:59:59", "%d/%m/%Y %H:%M:%S"))
t_min = time.mktime(time.strptime("01/11/2023 00:00:00", "%d/%m/%Y %H:%M:%S"))
t_max = time.mktime(time.strptime("01/04/2024 23:59:59", "%d/%m/%Y %H:%M:%S"))

# ========================================================================
LAT_RANGE = LAT_MAX - LAT_MIN
LON_RANGE = LON_MAX - LON_MIN
SOG_MAX = 30.0  # the SOG is truncated to 30.0 knots max.

EPOCH = datetime(1970, 1, 1)
LAT, LON, SOG, COG, HEADING, ROT, NAV_STT, TIMESTAMP, MMSI, SHIPTYPE, D2C = list(range(11))

CARGO_TANKER_ONLY = False
if CARGO_TANKER_ONLY:
    pkl_filename = "ct_" + pkl_filename
    pkl_filename_train = "ct_" + pkl_filename_train
    pkl_filename_valid = "ct_" + pkl_filename_valid
    pkl_filename_test = "ct_" + pkl_filename_test


def generate_csv2pkl():
    ## LOADING CSV FILES
    # ======================================
    l_l_msg = []  # list of AIS messages, each row is a message (list of AIS attributes)
    n_error = 0
    for csv_filename in l_csv_filename:
        data_path = os.path.join(dataset_path, csv_filename)
        with open(data_path, "r") as f:
            print("Reading ", csv_filename, "...")
            csvReader = csv.reader(f)
            next(csvReader)  # skip the legend row
            count = 1
            for row in csvReader:
                utc_time = datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%fZ')
                timestamp = (utc_time - EPOCH).total_seconds()
                count += 1
                try:
                    l_l_msg.append([float(row[0]), float(row[1]), float(row[2]),
                                    float(row[3]), int(float(row[4])),
                                    int(float(row[5])), int(float(row[6])),
                                    timestamp, int(float(row[8]))]
                                   )
                except:
                    n_error += 1
                    continue

    m_msg = np.array(l_l_msg)
    del l_l_msg


    def sublist(lst1, lst2):
        ls1 = [element for element in lst1 if element in lst2]
        ls2 = [element for element in lst2 if element in lst1]
        return (len(ls1) != 0) and (ls1 == ls2)


    VesselTypes = dict()
    l_mmsi = []
    n_error = 0
    for v_msg in tqdm(m_msg):
        try:
            mmsi_ = v_msg[MMSI]
            type_ = v_msg[SHIPTYPE]
            if mmsi_ not in l_mmsi:
                VesselTypes[mmsi_] = [type_]
                l_mmsi.append(mmsi_)
            elif type_ not in VesselTypes[mmsi_]:
                VesselTypes[mmsi_].append(type_)
        except:
            n_error += 1
            continue
    for mmsi_ in tqdm(list(VesselTypes.keys())):
        VesselTypes[mmsi_] = np.sort(VesselTypes[mmsi_])

    l_cargo_tanker = []
    l_fishing = []
    for mmsi_ in list(VesselTypes.keys()):
        if sublist(VesselTypes[mmsi_], list(range(70, 80))) or sublist(VesselTypes[mmsi_], list(range(80, 90))):
            l_cargo_tanker.append(mmsi_)
        if sublist(VesselTypes[mmsi_], [30]):
            l_fishing.append(mmsi_)

    np.save(dataset_path + "/" + cargo_tanker_filename, l_cargo_tanker)
    np.save(dataset_path + "/" + cargo_tanker_filename.replace("_cargo_tanker.npy", "_fishing.npy"), l_fishing)

    ## FILTERING
    # ======================================
    # Selecting AIS messages in the ROI and in the period of interest.

    ## LAT LON
    m_msg = m_msg[m_msg[:, LAT] >= LAT_MIN]
    m_msg = m_msg[m_msg[:, LAT] <= LAT_MAX]
    m_msg = m_msg[m_msg[:, LON] >= LON_MIN]
    m_msg = m_msg[m_msg[:, LON] <= LON_MAX]
    # SOG
    m_msg = m_msg[m_msg[:, SOG] >= 0]
    m_msg = m_msg[m_msg[:, SOG] <= SOG_MAX]
    # COG
    m_msg = m_msg[m_msg[:, SOG] >= 0]
    m_msg = m_msg[m_msg[:, COG] <= 360]

    # TIME
    m_msg = m_msg[m_msg[:, TIMESTAMP] >= 0]

    m_msg = m_msg[m_msg[:, TIMESTAMP] >= t_min]
    m_msg = m_msg[m_msg[:, TIMESTAMP] <= t_max]
    m_msg_train = m_msg[m_msg[:, TIMESTAMP] >= t_train_min]
    m_msg_train = m_msg_train[m_msg_train[:, TIMESTAMP] <= t_train_max]
    m_msg_valid = m_msg[m_msg[:, TIMESTAMP] >= t_valid_min]
    m_msg_valid = m_msg_valid[m_msg_valid[:, TIMESTAMP] <= t_valid_max]
    m_msg_test = m_msg[m_msg[:, TIMESTAMP] >= t_test_min]
    m_msg_test = m_msg_test[m_msg_test[:, TIMESTAMP] <= t_test_max]

    # Training set
    Vs_train = dict()
    for v_msg in tqdm(m_msg_train):
        mmsi = int(v_msg[MMSI])
        if not (mmsi in list(Vs_train.keys())):
            Vs_train[mmsi] = np.empty((0, 9))
        Vs_train[mmsi] = np.concatenate((Vs_train[mmsi], np.expand_dims(v_msg[:9], 0)), axis=0)
    for key in tqdm(list(Vs_train.keys())):
        if CARGO_TANKER_ONLY and (not key in l_cargo_tanker):
            del Vs_train[key]
        else:
            Vs_train[key] = np.array(sorted(Vs_train[key], key=lambda m_entry: m_entry[TIMESTAMP]))

    # Validation set
    Vs_valid = dict()
    for v_msg in tqdm(m_msg_valid):
        mmsi = int(v_msg[MMSI])
        if not (mmsi in list(Vs_valid.keys())):
            Vs_valid[mmsi] = np.empty((0, 9))
        Vs_valid[mmsi] = np.concatenate((Vs_valid[mmsi], np.expand_dims(v_msg[:9], 0)), axis=0)
    for key in tqdm(list(Vs_valid.keys())):
        if CARGO_TANKER_ONLY and (not key in l_cargo_tanker):
            del Vs_valid[key]
        else:
            Vs_valid[key] = np.array(sorted(Vs_valid[key], key=lambda m_entry: m_entry[TIMESTAMP]))

    # Test set
    Vs_test = dict()
    for v_msg in tqdm(m_msg_test):
        mmsi = int(v_msg[MMSI])
        if not (mmsi in list(Vs_test.keys())):
            Vs_test[mmsi] = np.empty((0, 9))
        Vs_test[mmsi] = np.concatenate((Vs_test[mmsi], np.expand_dims(v_msg[:9], 0)), axis=0)
    for key in tqdm(list(Vs_test.keys())):
        if CARGO_TANKER_ONLY and (not key in l_cargo_tanker):
            del Vs_test[key]
        else:
            Vs_test[key] = np.array(sorted(Vs_test[key], key=lambda m_entry: m_entry[TIMESTAMP]))

    ## PICKLING
    # ======================================
    for filename, filedict in zip([pkl_filename_train, pkl_filename_valid, pkl_filename_test],
                                  [Vs_train, Vs_valid, Vs_test]
                                  ):
        with open(os.path.join(dataset_path, filename), "wb") as f:
            pickle.dump(filedict, f)
