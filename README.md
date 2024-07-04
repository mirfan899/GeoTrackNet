# GeoTrackNet

TensorFlow implementation of the model proposed in "A Multi-Task Deep Learning Architecture for Maritime Surveillance Using AIS Data Streams" (https://ieeexplore.ieee.org/abstract/document/8631498) and "GeoTrackNet—A Maritime Anomaly Detector using Probabilistic Neural Network Representation of AIS Tracks and A Contrario Detection" (https://arxiv.org/abs/1912.00682).
(GeoTrackNet is the anomaly detection module of MultitaskAIS).

All the codes related to the Embedding block are adapted from the source code of Filtering Variational Objectives:
https://github.com/tensorflow/models/tree/master/research/fivo


#### Directory Structure
The elements of the code are organized as follows:

```
geotracknet.py                   # script to run the model (except the A contrario detection).
runners.py                        # graph construction code for training and evaluation.
bounds.py                         # code for computing each bound.
contrario_kde.py                  # script to run the A contrario detection.
contrario_utils.py
distribution_utils.py
nested_utils.py
utils.py
data
├── datasets.py                   # reader pipelines.
├── calculate_AIS_mean.py         # calculates the mean of the AIS "four-hot" vectors.
├── dataset_preprocessing.py      # preprocesses the AIS datasets.
└── csv2pkl.py                    # parse raw AIS messages from aivdm format to csv files.
└── csv2pkl.py                    # loads AIS data from *.csv files.
models
└── vrnn.py                       # VRNN implementation.
chkpt
└── ...                           # directory to keep checkpoints and summaries in.
results
└── ...                           # directory to save results to.
```

Conda isntallation
```shell
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```

Activate miniconda on your os.
Now replace the data and chkpt from previous results.
#### Requirements: 
See requirements.yml

### Datasets:

The MarineC dataset is provided by MarineCadastre.gov, Bureau of Ocean Energy Management, and National Oceanic and Atmospheric Administration, (marinecadastre.gov), and availble at (https://marinecadastre.gov/ais/)

The Brittany dataset is provided by CLS-Collecte Localisation Satellites (https://www.cls.fr/en/) and Erwan Guegueniat, comprises AIS messages captured by a coastal receiving station in Ushant, from 07/2011 to 07/2019. We provide here a set of processed AIS messages (data/ct_2017010203_10_20.zip) on which readers can re-produce the results in the paper GeoTrackNet. This set comprises dynamic information of AIS tracks (LAT, LON, SOG, COG, HEADING, ROT, NAV_STT, TIMESTAMP, MMSI) of cargo and tanker vessels from 01/2017 to 03/2017, downsampled to a resolution of 5 minutes. For the full Brittany dataset, please contact CLS (G. Hajduch, ghajduch@groupcls.com).

#### Preprocess the Data
run 
```shell
python csv2pkl.py
```
It will generate dataset in `csvs` directory

Now run `dataset_preprocessing.py`.
```shell
python dataset_preprocessing.py --dataset_dir ../data/csvs/ --l_input_filepath clean_csvs_train_track.pkl --output_filepath ../data/csvs/clean_csvs_train_track_out.pkl
python dataset_preprocessing.py --dataset_dir ../data/csvs/ --l_input_filepath clean_csvs_valid_track.pkl --output_filepath ../data/csvs/clean_csvs_valid_track_out.pkl
python dataset_preprocessing.py --dataset_dir ../data/csvs/ --l_input_filepath clean_csvs_test_track.pkl --output_filepath ../data/csvs/clean_csvs_test_track_out.pkl


#ais-gis-3
python dataset_preprocessing.py --dataset_dir ../data/ais-gis-3/ --l_input_filepath clean_csvs_train_track.pkl --output_filepath ../data/ais-gis-3/clean_csvs_train_track_out.pkl
python dataset_preprocessing.py --dataset_dir ../data/ais-gis-3/ --l_input_filepath clean_csvs_valid_track.pkl --output_filepath ../data/ais-gis-3/clean_csvs_valid_track_out.pkl
python dataset_preprocessing.py --dataset_dir ../data/ais-gis-3/ --l_input_filepath clean_csvs_test_track.pkl --output_filepath ../data/ais-gis-3/clean_csvs_test_track_out.pkl
```

Now run `calculate_AIS_mean.py` to get the mean pickle file.

```shell
python calculate_AIS_mean.py
```
### Training the Embedding layer
First we must train the Embedding layer:
```shell
python geotracknet.py \
  --mode=train \
  --dataset_dir=./data \
  --trainingset_name=csvs/clean_csvs_train_track_out.pkl \
  --testset_name=csvs/clean_csvs_valid_track_out.pkl \
  --lat_min=4.7 \
  --lat_max=20.5 \
  --lon_min=116.8 \
  --lon_max=126.6 \
  --latent_size=50 \
  --batch_size=4 \
  --num_samples=4 \
  --learning_rate=0.0003 \
```

A model trained on the dataset comprising AIS messages can be found at `elbo-clean_csvs_train_track_out.pkl-data_dim-2662-latent_size-50-batch_size-4/model.ckpt`.

### Running task-specific submodels
After the Embedding layer is trained, we can run task-specific blocks.

#### save_logprob
Now run `save_logprob`
```shell
python geotracknet.py \
  --mode=save_logprob \
  --dataset_dir=./data \
  --trainingset_name=csvs/clean_csvs_train_track_out.pkl \
  --testset_name=csvs/clean_csvs_valid_track_out.pkl \
  --lat_min=4.7 \
  --lat_max=20.5 \
  --lon_min=116.8 \
  --lon_max=126.6 \
  --latent_size=50 \
  --batch_size=4 \
  --num_samples=4 \
  --learning_rate=0.0003 \
```
Similarly for the test set (```testset_name=csvs/clean_csvs_test_track_out.pkl```).

#### local_logprob
*log_logprob* divides the ROI into small cells and saves the <img src="/tex/7170cb0578591c3ef08c6b900abb2023.svg?invert_in_darkmode&sanitize=true" align=middle width=86.82290429999999pt height=24.65753399999998pt/> of AIS messages in each cell.
```shell
python geotracknet.py \
  --mode=local_logprob \
  --dataset_dir=./data \
  --trainingset_name=csvs/clean_csvs_train_track_out.pkl \
  --testset_name=csvs/clean_csvs_valid_track_out.pkl \
  --lat_min=4.7 \
  --lat_max=20.5 \
  --lon_min=116.8 \
  --lon_max=126.6 \
  --latent_size=50 \
  --batch_size=4 \
  --num_samples=4 \
  --learning_rate=0.0003 \
```

#### contrario_detection
*contrario_detection* detects abnormal vessels' behaviors using *a contrario* detection and plots the results.
```shell
python geotracknet.py \
  --mode=contrario_detection \
  --dataset_dir=./data \
  --trainingset_name=csvs/clean_csvs_train_track_out.pkl \
  --testset_name=csvs/clean_csvs_test_track_out.pkl \
  --lat_min=4.7 \
  --lat_max=20.5 \
  --lon_min=116.8 \
  --lon_max=126.6 \
  --latent_size=50 \
  --batch_size=4 \
  --num_samples=4 \
  --learning_rate=0.0003 \
```


### Acknowledgement

We would like to thank MarineCadastre, CLS and Erwan Guegueniat, Kurt Schwehr, Tensorflow team, QGIS and OpenStreetmap for the data and the open-source codes.

We would also like to thank Jetze Schuurmans for helping convert the code from Python2 to Python3.

### Contact
For any questions, please open an issue.


### Tracks info
12 csvs have
```text
Writing to  ./ais-gis-3/clean_csvs_train_track.pkl ...
Total number of tracks:  7167
Writing to  ./ais-gis-3/clean_csvs_valid_track.pkl ...
Total number of tracks:  6038
Writing to  ./ais-gis-3/clean_csvs_test_track.pkl ...
Total number of tracks:  3528
```

6 csvs
