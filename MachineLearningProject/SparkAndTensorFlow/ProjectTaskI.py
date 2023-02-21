#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[52]:


#building spark session
appname = "courseproject" #define app name
master = "local"

config = pyspark.SparkConf().setAppName(appname).setMaster(master) #we do not have any workers.


#session
#with sql context, create session from it
sc  = SparkContext.getOrCreate(conf=config)
sqlContext = SQLContext(sc)
#don't create many sessions, take up too much room!
sp_session = sqlContext.sparkSession.builder.getOrCreate();
#export data into postgresql
from pyspark import SparkContext, SparkConf, SQLContext
import os
db_properties={}
db_properties['username']="postgres"
db_properties['password']="postgres"
# make sure to use the correct port number. These 
db_properties['url']= "jdbc:postgresql://localhost:5432/postgres"
db_properties['driver']="org.postgresql.Driver"

#define the function to store players data each year
#take the name of the spark table and the name of the table to be created

def write_to_postgres(df,table_name):
     df.write.format("jdbc")    .mode("overwrite")    .option("url", "jdbc:postgresql://localhost:5432/postgres")    .option("dbtable", table_name)    .option("user", "postgres")    .option("password", "postgres")    .option("Driver", "org.postgresql.Driver")    .save()
    


# In[83]:


#drop those columns have >50% empty cells
#impute columns have < 50% empty cells
#do not impute categorical columns
#compute proper values for some columns
#conduct the operations in some columns
import pandas as pd
import numpy as np


#define the function to clean the data
def clean_fifa(df,year):
    #read in the data
    players_df= (sp_session.read.format("csv")                 .option("inferSchema","true")                 .option("header","true").load(df))
    #cast some columns into correct data type
    players_cast= players_df.withColumn("SofifaId", col("sofifa_id").cast("string")).drop("sofifa_id")    .withColumn("DOB",to_date(col("dob"))).withColumn("Year", lit(year))
    #find out columns that have too many null values
    null_counts = players_cast.select([(count(when(isnan(c)| col(c).isNull(),c))/players_cast.count()).alias(c) 
                         for c in players_cast.drop("DOB").columns]).collect()[0].asDict()
    to_drop = [k for k, v in null_counts.items() if v > 0.5]
    players_drop = players_cast.drop(*to_drop)
#     drop columns that have less than 50% values
    print("dropped empty columns")
#     players_drop.printSchema()
    #compute proper values for some columns
    players_int_col = players_drop.select("ls","st","rs","lw","lf","cf","rf","rw","lam","cam",
                        "ram","lm","lcm","cm","rcm","rm","lwb","ldm","cdm",
                        "rdm","rwb","lb","lcb","cb","rcb","rb","gk").columns
    for column in players_int_col:
        int_full = 'full_{}'.format(column) 
        int_first = 'first_{}'.format(column)
        int_operand = 'op_{}'.format(column)
        int_second = 'second_{}'.format(column)
        int_value = "cleaned_{}".format(column)
        players_drop = players_drop.withColumn(int_full,when(col(column).cast("int").isNotNull(),col(column).cast("int")).otherwise(0))        .withColumn(int_first,when(regexp_extract(col(column),'([0-9]*)([-+])([0-9]*)',1).cast("int").isNotNull(),
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
    na_col = ["value_eur","wage_eur","pace","shooting","passing","dribbling"]
    na_imp_col = ["{}_imputed".format(c) for c in na_col]
    player_imputer = Imputer(inputCols = na_col,
                             outputCols = na_imp_col).setMissingValue(0).setStrategy("mean")
    players_imputed = player_imputer.fit(players_drop)    .transform(players_drop)    .drop("value_eur","wage_eur","pace","shooting","passing","dribbling")
    print("finishing imputation.")
                                         
    tablename = "FIFA.PLAYERS_"+str(year)
    write_to_postgres(players_imputed, tablename)
    print("ingested into postgres.")
    


# In[84]:


clean_fifa("../Data/players_15.csv",15)


# In[85]:


clean_fifa("../data/players_16.csv",16)


# In[86]:


clean_fifa("../data/players_17.csv",17)


# In[87]:


clean_fifa("../data/players_18.csv",18)


# In[88]:


clean_fifa("../data/players_19.csv",19)


# In[89]:


clean_fifa("../data/players_20.csv",20)


# In[90]:


clean_fifa("../data/players_21.csv",21)


# In[91]:


clean_fifa("../data/players_22.csv",22)


# In[ ]:


#end of Task1

