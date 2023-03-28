# Build NFL Game Result Model Using Spark and TensorFlow.

## Data Ingestion

Check out how to initiate a spark session and read in csv files with the readData() function in DataProcessing.py

## Data Preprocessing
Check out how to process plays data and players data and extract important features using spark sql functions in DataProcessing.py

## Modeling
Check out how to modify data into correct format and use them to fit a TF model in Modeling.py.

## Measuring Performance
The usual measurement of a model's fitness:
- R-squared. How is the dependent variable explained by your chosen independent variables?
- MSE. How accurate is the prediction on test dataset?
- AUC (Area Under Curve). Also to measure how accurate a prediction model is when you change certain parameters.

...
