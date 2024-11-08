# An ML Project using Spark and TensorFlow in Python
## Project goal: build ETL pipeline of data from players and plays with Spark.


### 1 Spark Initiation
Apache Spark is a distributive data processing library that supports many data enigneering functions such as queries and manipulations. Its distributive manner will showcase once it is uploaded onto a distributed system. When run locally, it utilizes your local machine as the master.

To use Spark in Python, we use pyspark. To start using it, we need to configure the spark environment, set an app name and the master's location (since it is on our laptop, we call it the master). Later, we need to set up a spark context using this configuration, and then initiate a sqlContext with this spark context. The logic is :

Spark Context (config parameters) -> provides an environment for -> SQL in Spark.

All the packages we are going to need (and possibly more if you require them) are here. There are other packages for other data engineering purposes.
```{python}
import pyspark
from pyspark import SparkContext #for unabling to set up sc by yourself
from pyspark.sql import SparkSession, SQLContext #spark dataframe = spark sql
from pyspark.ml.feature import Imputer
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, StringType
import pandas as pd
import numpy as np
#export data into postgresql
from pyspark import SparkContext, SparkConf, SQLContext
import os
 
 ```
 Now let's initiate the spark environment like this.
 
 ```{python}
def initiate_spark():
    #define the configuration parameters
    appname = "courseproject" #define app name
    master = "local"
    #create a configuration object
    config = pyspark.SparkConf().setAppName(appname).setMaster(master) #we do not have any workers.

    #start a session
    #with sql context, create session from it
    sc  = SparkContext.getOrCreate(conf=config)
    sqlContext = SQLContext(sc)
    #don't create many sessions, take up too much room!
    #create a SQL session for later use
    sp_session = sqlContext.sparkSession.builder.getOrCreate()
    return sp_session
```

### 2 PostgreSQL set up
Here we use PostgreSQL to store the processed data for later retrieval or simply for keeping the record on cloud. Firstly, you need to set up postgreSQL on your PC, initiate a username and password, and define its port number. You can find out how to set up your postgreSQL online (ask GPT!)
```{python}
def initiate_postgres():
    db_properties={}
    db_properties['username']="postgres"
    db_properties['password']="postgres"
    # make sure to use the correct port number. These
    db_properties['url']= "jdbc:postgresql://localhost:5432/postgres"
    db_properties['driver']="org.postgresql.Driver"

#define the function to store players data each year
#take the name of the spark table and the name of the table to be created
```
We also create a function to iteratively store the data into postgreSQL. It looks like this. We pass along the username and passwords and port number as parameters to them each time we need to write something.
```{python}
def write_to_postgres(df,table_name):
     df.write.format("jdbc").mode("overwrite").option("url", "jdbc:postgresql://localhost:5432/postgres").option("dbtable", table_name).option("user", "postgres").option("password", "postgres").option("Driver", "org.postgresql.Driver").save()

```

### 3 Use Spark for Data Engineering

The goal of the data cleaning process consists of :

- drop those F.columns have >50% empty cells
- impute F.columns have < 50% empty cells
- do not impute categorical columns
- compute proper values for some columns
- conduct the operations in some columns

Thus the functions we mostly use from Spark include:
- cast some columns into correct data types : col.cast(right-data-type)
- create new columns with the right formats : withColumn(new-col, col(old))
- clean null values/columns: select()
- compute numbers based on string values using regular expression - regexp_extract()
- impute (fill missing values) the data: Imputer()
```{python}
#define the function to clean the data
def clean_fifa(df,year,sp_session):
    #read in the data
    players_df= (sp_session.read.format("csv")\
    .option("inferSchema","true").option("header","true")\
    .load(df))
    #cast some columns into correct data type
    players_cast= players_df.withColumn("SofifaId", col("sofifa_id").cast("string")).drop("sofifa_id")    .withColumn("DOB",to_date(col("dob"))).withColumn("Year", lit(year))
    #find out columns that have too many null values
    null_counts = players_cast.select([(count(when(isnan(c)| col(c).isNull(),c))/players_cast.count()).alias(c)
                         for c in players_cast.drop("DOB").columns]).collect()[0].asDict()
    to_drop = [k for k, v in null_counts.items() if v > 0.5]
    # drop multiple columns 
    players_drop = players_cast.drop(*to_drop)
#     drop columns that have less than 50% values
    print("dropped empty columns")
#     players_drop.printSchema()
    #compute proper values for some numeric columns
    players_int_col = players_drop.select("ls","st","rs","lw","lf","cf","rf","rw","lam","cam",
                        "ram","lm","lcm","cm","rcm","rm","lwb","ldm","cdm",
                        "rdm","rwb","lb","lcb","cb","rcb","rb","gk").columns
    #in those columns the data look like (1+2) or (10-4)
    #if we can extract integers (resulting in is not null), then we have a value for it, otherwise we assign it 0.
    for column in players_int_col:
        int_full = 'full_{}'.format(column)
        int_first = 'first_{}'.format(column)
        int_operand = 'op_{}'.format(column)
        int_second = 'second_{}'.format(column)
        int_value = "cleaned_{}".format(column)
        players_drop = players_drop.withColumn(int_full,when(col(column).cast("int").isNotNull(),col(column).cast("int")).otherwise(0))        \
            .withColumn(int_first,when(Fregexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',1).cast("int").isNotNull(),
                                     regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',1).cast("int")).otherwise(0))\
        .withColumn(int_operand,when(regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',2).isNotNull(),
                                     regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',2)).otherwise("null"))\
        .withColumn(int_second,when(regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',3).cast("int").isNotNull(),
                                     regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',3).cast("int")).otherwise(0))\
        .withColumn(int_value,when(col(int_operand) =="+",
                                     col(int_first)+col(int_second)).when(col(int_operand) =="-",col(int_first)-col(int_second)).otherwise(col(int_full)))\
        .drop(int_operand,int_full,int_first,int_second,column)
    print("numeric data have been cleaned.")
#     players_drop.show(10)
    #impute the data
    #using an Imputer()
    na_col = ["value_eur","wage_eur","pace","shooting","passing","dribbling"]
    na_imp_col = ["{}_imputed".format(c) for c in na_col]
    player_imputer = Imputer(inputCols = na_col,
                             outputCols = na_imp_col).setMissingValue(0).setStrategy("mean")
    players_imputed = player_imputer.fit(players_drop)    .transform(players_drop)    .drop("value_eur","wage_eur","pace","shooting","passing","dribbling")
    print("finishing imputation.")                                    
    tablename = "FIFA.PLAYERS_"+str(year)
    #use the method to write to postgres
    write_to_postgres(players_imputed, tablename)
    print("ingested into postgres.")
    return "clean and write successfully."
```
Lastly, we write a function to iterate over all the data sets. We can also use a with function to open all csv files one by one.
```{python}
def clean_fifa_data(sp):
    clean_fifa("../Data/players_15.csv",15,sp)

    clean_fifa("../data/players_16.csv",16,sp)

    clean_fifa("../data/players_17.csv",17,sp)

    clean_fifa("../data/players_18.csv",18,sp)

    clean_fifa("../data/players_19.csv",19,sp)


    clean_fifa("../data/players_20.csv",20,sp)

    clean_fifa("../data/players_21.csv",21,sp)

    clean_fifa("../data/players_22.csv",22,sp)

def main():
    sp_session = initiate_spark()
    initiate_postgres()
    clean_fifa_data(sp=sp_session)


#end of Task1
```

### END
