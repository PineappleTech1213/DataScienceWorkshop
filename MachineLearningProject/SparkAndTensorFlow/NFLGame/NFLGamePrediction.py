
import pyspark
from pyspark.sql import SparkSession, SQLContext
from pyspark.ml.feature import Imputer
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number
from pyspark import SparkContext, SparkConf, SQLContext
import os

def main():
    spark = SparkIngestion()
    
    player_path ='/home/bigdata/Big-Data-Bowl/Data/players.csv'
    players = cleanPlayerData()
    plays = cleanPlayerData()
    saveData(players, 'NFL','PLAYERS')
    saveData(plays,'NFL','PLAYS')

def SparkIngestion():
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
    return spark

def readData(path = "/home/bigdata/Big-Data-Bowl/Data/plays.csv"):
#Ingest data from the players CSV into Spark Dataframe.
    plays_df = (spark.read
            .format("csv")
            .option("inferSchema", "true")
            .option("header","true")
            .load(path)
        )

    plays_df.printSchema()
    return plays_df

def cleanPlayerData(players):
    players_df = readData("/home/bigdata/Big-Data-Bowl/Data/players.csv")
    casted_types_df = (players_df.withColumn("nfl_id", players_df["nflId"].cast("string")).drop("nflId")
              .withColumn("Draft_Round", players_df["DraftRound"].cast("integer")).drop("DraftRound")
              .withColumn("Draft_Number", players_df["DraftNumber"].cast("integer")).drop("DraftNumber")
              .distinct()
           )
    
    casted_types_df.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in casted_types_df.columns]).show()
    filled_df = casted_types_df.fillna(0,['Draft_Round','Draft_Number'])

# process NA/Null values of the numeric columns
    imputer = Imputer (
    inputCols=['Draft_Round','Draft_Number'],
    outputCols=["{}_imputed".format(c) for c in ['Draft_Round','Draft_Number']]
    ).setStrategy("mean").setMissingValue(0)

    imputed_df = imputer.fit(filled_df).transform(filled_df)

    imputed_df_with_dropped_columns = imputed_df.drop('Draft_Round','Draft_Number')

    full_df_final = imputed_df_with_dropped_columns.withColumnRenamed("Draft_Round_imputed","Draft_Round").withColumnRenamed("Draft_Number_imputed","Draft_Number")

    full_df_final.printSchema()
    #now normalize the data, removing duplicates of draft results by adding entry ids.
    entry_df = full_df_final.select("EntryYear","Draft_Round","Draft_Number").distinct()
    print(entry_df.count())
    entry_df_with_id = entry_df.withColumn("entry_id", monotonically_increasing_id()+1)
    entry_df_with_id.show()
    joined_df = full_df_final.join(entry_df_with_id,(entry_df_with_id.Draft_Round==full_df_final.Draft_Round)&(entry_df_with_id.Draft_Number==full_df_final.Draft_Number)&(full_df_final.EntryYear==entry_df_with_id.EntryYear))
    #now we can drop the useless columns
    final_players_df = joined_df.drop("EntryYear","Draft_Round","Draft_Number")
                                    
def cleanPlaysData(plays_df):
    plays_df_with_players_columns = plays_df.withColumn('Player_1', regexp_extract(col('playDescription'), '(\w+)(\.)(\w+)', 3))\
                    .withColumn('Player_2', regexp_extract(col('playDescription'), '(\w+)(\.)(\w+)(.*?)(\w+)(\.)(\w+)', 7))\
                    .withColumn('Player_3', regexp_extract(col('playDescription'), '(\w+)(\.)(\w+)(.*?)(\w+)(\.)(\w+)(.*?)(\w+)(\.)(\w+)', 11))

    #use players id and map them into the plyaers
    plays_df = readData("/home/bigdata/Big-Data-Bowl/Data/players.csv")
    players_id_and_lname_df = casted_players_df.select("nflId","LastName").distinct()
    #check palyers' names and last name count
    print(players_id_and_lname_df.count())
    players_id_and_lname_df.groupBy("lastName").count().show()
    #using window function to find unique player last names
    w2 = Window.partitionBy("LastName").orderBy(col("nflId"))
    single_last_name_players_df = players_id_and_lname_df.withColumn("row",row_number().over(w2)) \
                                  .filter(col("row") == 1).drop("row")
    plays_with_player_1 = plays_df_with_players_columns.join(single_last_name_players_df,plays_df_with_players_columns.Player_1==single_last_name_players_df.LastName)
    return plays_with_player_1

def saveData(df, schema = '', name = 'table'):
    location = schema+'.'+name
    db_properties={}
    db_properties['username']="postgres"
    db_properties['password']="postgres"
# make sure to use the correct port number. These 
    db_properties['url']= "jdbc:postgresql://localhost:5432/postgres"
    db_properties['driver']="org.postgresql.Driver"
    df.write.format("jdbc")\
    .mode("overwrite")\
    .option("url", "jdbc:postgresql://localhost:5432/postgres")\
    .option("dbtable", location)\
    .option("user", "postgres")\
    .option("password", "postgres")\
    .option("Driver", "org.postgresql.Driver")\
    .save()

#if you need to read back the data 
def readFromSQL(tablename):
    df_after_db_read = sqlContext.read.format("jdbc")\
    .option("url", "jdbc:postgresql://localhost:5432/postgres")\
    .option("dbtable", tablename)\
    .option("user", "postgres")\
    .option("password", "postgres")\
    .option("Driver", "org.postgresql.Driver")\
    .load()
    df_after_db_read.show(5)
    df_after_db_read.printSchema()


main()