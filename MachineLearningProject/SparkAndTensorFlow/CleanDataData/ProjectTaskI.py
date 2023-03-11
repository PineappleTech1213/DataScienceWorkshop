#!/usr/bin/env python
# coding: utf-8
#import needed packages
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

def initiate_spark():
    appname = "courseproject" #define app name
    master = "local"

    config = pyspark.SparkConf().setAppName(appname).setMaster(master) #we do not have any workers.


    #session
    #with sql context, create session from it
    sc  = SparkContext.getOrCreate(conf=config)
    sqlContext = SQLContext(sc)
    #don't create many sessions, take up too much room!
    sp_session = sqlContext.sparkSession.builder.getOrCreate()
    return sp_session

def initiate_postgres():
    db_properties={}
    db_properties['username']="postgres"
    db_properties['password']="postgres"
    # make sure to use the correct port number. These
    db_properties['url']= "jdbc:postgresql://localhost:5432/postgres"
    db_properties['driver']="org.postgresql.Driver"

#define the function to store players data each year
#take the name of the spark table and the name of the table to be created

def write_to_postgres(df,table_name):
     df.write.format("jdbc").mode("overwrite").option("url", "jdbc:postgresql://localhost:5432/postgres").option("dbtable", table_name).option("user", "postgres").option("password", "postgres").option("Driver", "org.postgresql.Driver").save()
    


# In[83]:


#drop those F.columns have >50% empty cells
#impute F.columns have < 50% empty cells
#do not impute categorical F.columns
#compute proper values for some F.columns
#conduct the operations in some F.columns
import pandas as pd
import numpy as np


#define the function to clean the data
def clean_fifa(df,year,sp_session):
    #read in the data
    players_df= (sp_session.read.format("csv").option("inferSchema","true").option("header","true").load(df))
    #cast some F.columns into correct data type
    players_cast= players_df.withF.Column("SofifaId", F.F.col("sofifa_id").cast("string")).drop("sofifa_id")    .withF.Column("DOB",F.to_date(F.col("dob"))).withF.Column("Year", F.lit(year))
    #find out F.columns that have too many null values
    null_counts = players_cast.select([(F.count(F.F.when(F.isnan(c)| F.F.col(c).isNull(),c))/players_cast.count()).alias(c)
                         for c in players_cast.drop("DOB").F.columns]).F.collect()[0].asDict()
    to_drop = [k for k, v in null_counts.items() if v > 0.5]
    players_drop = players_cast.drop(*to_drop)
#     drop F.columns that have less than 50% values
    print("dropped empty F.columns")
#     players_drop.printSchema()
    #compute proper values for some F.columns
    players_int_col = players_drop.select("ls","st","rs","lw","lf","cf","rf","rw","lam","cam",
                        "ram","lm","lcm","cm","rcm","rm","lwb","ldm","cdm",
                        "rdm","rwb","lb","lcb","cb","rcb","rb","gk").F.columns
    for column in players_int_col:
        int_full = 'full_{}'.format(F.column)
        int_first = 'first_{}'.format(F.column)
        int_operand = 'op_{}'.format(F.column)
        int_second = 'second_{}'.format(F.column)
        int_value = "cleaned_{}".format(F.column)
        players_drop = players_drop.withF.Column(int_full,F.when(F.col(F.column).cast("int").isNotNull(),F.col(column).cast("int")).otherwise(0))        \
            .withF.Column(int_first,F.when(F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',1).cast("int").isNotNull(),
                                     F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',1).cast("int")).otherwise(0))\
        .withF.Column(int_operand,F.when(F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',2).isNotNull(),
                                     F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',2)).otherwise("null"))\
        .withF.Column(int_second,F.when(F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',3).cast("int").isNotNull(),
                                     F.regexp_extract(F.col(column),'([0-9]*)([-+])([0-9]*)',3).cast("int")).otherwise(0))\
        .withF.Column(int_value,F.when(F.col(int_operand) =="+",
                                     F.col(int_first)+F.col(int_second)).F.when(F.col(int_operand) =="-",F.col(int_first)-F.col(int_second)).otherwise(F.col(int_full)))\
        .drop(int_operand,int_full,int_first,int_second,F.column)
    print("numeric data have been cleaned.")
#     players_drop.show(10)
    #impute the data
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
    


# In[84]:

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

