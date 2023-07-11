# Build NFL Game Result Model Using Spark and TensorFlow.
The NFL, which stands for the National Football League, is a professional American football league. It is the highest level of competition in the sport and is composed of 32 teams, divided equally between the National Football Conference (NFC) and the American Football Conference (AFC). 

## Project Goal: to predict a game's playout based on previous NFL games data.
We need to collect  comprehensive data on NFL games, plays, and players. This can include historical game results, player statistics, team performance metrics, weather conditions, and more. We can find them on the Kaggle Platform: https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/data.
Then, we utilize machine learning technologies and data processing tools to build an ETL pipeline that streamline building prediction models.

## Data Ingestion
Using Spark to read in csv files. First establish a Spark Session and import related functions.

First we need to download Spark into your development environment. use ```pip install pyspark``` in your environment's terminal to download it. 

Test it with

```
import pyspark
print(pyspark.__version__)
```
And build connections with

```{python}
    appName = "Big Data Analytics"
    master = "local"

# Create Configuration object for Spark.
    conf = pyspark.SparkConf()\
        .set('spark.driver.host','127.0.0.1')\
        .setAppName(appName)\
        .setMaster(master)

# Create Spark Context with the new configurations rather than rely on the default one
    sc = SparkContext.getOrCreate(conf=conf)

# You need to create SQL Context to conduct some database operations like what we will see later.
#sqlContext = SQLContext(sc)

# If you have SQL context, you create the session from the Spark Context
    spark = SparkSession.builder.getOrCreate()
```
With a Spark Session, read in csv files with the readData() function in DataProcessing.py. For example, read in plays data.
```{python}
plays_df = (spark.read
            .format("csv")
            .option("inferSchema", "true")
            .option("header","true")
            .load(path)
        )

    plays_df.printSchema()
```

## Data Preprocessing
Check out how to process plays data and players data and extract important features using spark sql functions in DataProcessing.py.

We need to process games, plays and players data to gather useful numeric as well as categorical data.

## Data Storage
We need to store the processed data somewhere for easier access later. We use PostgreSQL to store those data. Download PgAdmin for PostgreSQL here:
https://www.pgadmin.org/.


## Modeling
Check out how to modify data into correct format and use them to fit a TF model in Modeling.py.

We can use the most comprehensive ML libraries TensorFlow to build all kinds of ML models for use, comparing them basic on a common metric.
Download TensorFlow by using ```pip install tensorflow```, and then ```import tensorflow as tf```. 

## Measuring Performance
The usual measurement of a model's fitness:
- R-squared. How is the dependent variable explained by your chosen independent variables?
- MSE. How accurate is the prediction on test dataset?
- AUC (Area Under Curve). Also to measure how accurate a prediction model is when you change certain parameters.

...
