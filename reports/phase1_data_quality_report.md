# NYC Taxi Fare Prediction

# Phase 1 Report: Data Understanding and Quality Assessment


## 1. Project Overview

This project focuses on predicting taxi fares using historical New York City taxi trip data.

The objective is to build a machine learning regression model that estimates taxi fare amounts based on trip-related information.

The prediction target is:

- `fare_amount`

The raw features include:

- Pickup datetime
- Pickup coordinates
- Dropoff coordinates
- Passenger count


The project follows the following machine learning workflow:

1. Data understanding
2. Data cleaning
3. Feature engineering
4. Exploratory data analysis
5. Model development and evaluation


---

## 2. Dataset Overview


The dataset is obtained from the Kaggle New York City Taxi Fare Prediction competition.


The original training dataset contains:

- Approximately 55.4 million taxi trip records
- 8 raw variables
- Approximately 5.3 GB CSV file


The original variables are:


| Feature | Description |
|---|---|
| key | Unique trip identifier |
| fare_amount | Taxi fare amount (prediction target) |
| pickup_datetime | Trip pickup timestamp |
| pickup_longitude | Pickup longitude |
| pickup_latitude | Pickup latitude |
| dropoff_longitude | Dropoff longitude |
| dropoff_latitude | Dropoff latitude |
| passenger_count | Number of passengers |


Due to the large dataset size, an initial sample containing 100,000 records was used for exploratory analysis and cleaning rule development.


The purpose of this sample-based analysis was:

- Understand dataset characteristics
- Identify potential data quality problems
- Validate preprocessing logic before scaling to the full dataset


---

# 3. Data Understanding


## 3.1 Dataset Structure


Initial inspection showed that:

- All columns were successfully loaded.
- Data types were correctly interpreted.
- `pickup_datetime` was converted into datetime format.
- No missing values were identified in the development sample.


---

## 3.2 Feature Categories


### Temporal Information

Current feature:

- `pickup_datetime`


Potential engineered features:

- pickup hour
- day of week
- weekend indicator


---

### Geographic Information

Current features:

- pickup longitude
- pickup latitude
- dropoff longitude
- dropoff latitude


Potential engineered feature:

- trip distance


---

### Passenger Information

Current feature:

- `passenger_count`


---

### Target Variable

Prediction target:

- `fare_amount`


---

# 4. Initial Data Quality Assessment


The initial 100,000-row sample was analyzed to identify potential data quality issues.


## 4.1 Missing Values


Missing values were checked using:

```python
df.isnull().sum()
```


Observation:

No missing values were identified in the development sample.

Further validation will be performed when applying the final pipeline to the complete dataset.


---

# 4.2 Fare Amount Analysis


The target variable distribution was analyzed using descriptive statistics and visualization.


Observed characteristics:

- Fare distribution is strongly right-skewed.
- Most taxi trips have relatively low fares.
- A small number of trips have very high fare values.


Potential issues:

## Negative fare values


Some records contain:

```text
fare_amount <= 0
```


These observations are considered invalid because taxi fares should represent positive monetary transactions.


Cleaning rule:

```text
Remove records where fare_amount <= 0
```


Reason:

Negative or zero fares do not represent valid completed taxi trips.


---

## Extreme fare values


Very large fare values were observed.


These values require further investigation because:

- Some may represent legitimate long-distance trips.
- Some may be caused by incorrect records.


Therefore, high fare values will not be removed only based on magnitude.


Further validation will consider:

- Trip distance
- Geographic information
- Fare distribution


---

# 4.3 Geographic Data Quality


Coordinate variables were inspected.


Potential problems:

Some observations contained longitude and latitude values outside realistic geographic ranges.


Invalid conditions:


```text
longitude < -180 or longitude > 180

latitude < -90 or latitude > 90
```


Cleaning rule:

Remove records containing physically impossible coordinates.


Reason:

These values cannot represent real-world geographic locations.


---

# 4.4 NYC Area Filtering


Since the project focuses on NYC taxi trips, geographic filtering was investigated.


A NYC-area bounding box approach was tested to remove observations outside the expected operating region.


This step requires careful validation because taxi trips may include surrounding areas such as airport locations.


The final geographic filtering strategy will be confirmed during full dataset preprocessing.


---

# 4.5 Passenger Count Analysis


Passenger count distribution was analyzed.


Potential issue:


```text
passenger_count = 0
```


These records were considered invalid because they do not represent normal passenger trips.


Cleaning rule:


```text
Remove records where passenger_count <= 0
```


---

# 5. Cleaning Pipeline Design


Based on the initial analysis, the following cleaning pipeline was developed:


## Step 1: Fare Cleaning

Rule:

```text
Remove fare_amount <= 0
```


Purpose:

Remove invalid monetary values.


---

## Step 2: Geographic Validation


Rule:

```text
Remove impossible latitude and longitude values
```


Purpose:

Remove corrupted location records.


---

## Step 3: NYC Area Filtering


Rule:

```text
Keep trips within the defined NYC geographic region
```


Purpose:

Focus the model on NYC taxi operations.


---

## Step 4: Passenger Validation


Rule:

```text
Remove passenger_count <= 0
```


Purpose:

Remove invalid passenger trip records.


---

# 6. Current Development Status


Completed:

- Dataset acquisition
- Dataset structure analysis
- Data type validation
- Statistical analysis
- Target variable exploration
- Initial visualization
- Data quality issue identification
- Cleaning rule development using a 100,000-row sample


Not completed:

- Applying cleaning pipeline to the complete 55.4M-row dataset
- Generating final cleaned dataset
- Feature engineering
- Exploratory data analysis
- Model development


---

# 7. Feature Engineering Plan


After finalizing the cleaning pipeline, the following features will be created:


## Trip Distance

Calculate geographical distance between pickup and dropoff locations.


Purpose:

Capture the relationship between travel distance and taxi fare.


---

## Pickup Hour

Extract hour information from:

```text
pickup_datetime
```


Purpose:

Capture temporal patterns.


---

## Weekend Indicator


Create binary feature:


```text
weekday = 0

weekend = 1
```


Purpose:

Capture differences between weekday and weekend trips.


---

# 8. Next Steps


The next stage will focus on:


1. Convert validated cleaning rules into a reusable preprocessing pipeline.

2. Apply the pipeline to the complete dataset.

3. Generate cleaned dataset.

4. Create engineered features.

5. Perform exploratory data analysis.

6. Build baseline regression models.