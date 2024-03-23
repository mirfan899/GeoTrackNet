import csv
import os
from datetime import datetime
import dateutil.parser as dp
EPOCH = datetime(1970, 1, 1)

l_csv_filename = ["output_7.csv"]
l_l_msg = [] # list of AIS messages, each row is a message (list of AIS attributes)
n_error = 0
dataset_path = "./"
for csv_filename in l_csv_filename:
    data_path = os.path.join(dataset_path,csv_filename)
    with open(data_path,"r") as f:
        print("Reading ", csv_filename, "...")
        csvReader = csv.reader(f)
        next(csvReader) # skip the legend row
        count = 1
        for row in csvReader:
            utc_time = datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%fZ')

            timestamp = (utc_time - EPOCH).total_seconds()
            count += 1
            try:
                l_l_msg.append([float(row[0]), float(row[1]),float(row[2]),
                               float(row[3]),int(row[4]),
                               int(row[5]),int(row[6]),
                               timestamp, int(row[8])]
                               )
            except:
                n_error += 1
                continue
print(n_error)