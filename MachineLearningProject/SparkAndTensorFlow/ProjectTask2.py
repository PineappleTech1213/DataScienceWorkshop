# Task2 Python functions
# import needed packages
import pyspark
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql import functions as F
from functools import reduce
from pyspark.sql.functions import *
import numpy as np
import os
from functools import reduce



def initiate_spark():
    appName = "Fifa Data Processing"
    master = "local"

    # Create Configuration object for Spark.
    conf = pyspark.SparkConf() \
        .set('spark.driver.host', '127.0.0.1') \
        .setAppName(appName) \
        .setMaster(master)

    # Create Spark Context with the new configurations rather than rely on the default one
    sc = SparkContext.getOrCreate(conf=conf)

    # You need to create SQL Context to conduct some database operations like what we will see later.
    sqlContext = SQLContext(sc)

    # If you have SQL context, you create the session from the Spark Context
    spark = SparkSession.builder.getOrCreate()
    return spark,sc,sqlContext


# read in the data from the file

def read_fifa_data(year, spark):
    tablename = "FIFA.PLAYERS_" + year

    players_df = spark.read.format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/postgres") \
        .option("dbtable", tablename) \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("Driver", "org.postgresql.Driver") \
        .load()
    players_df.printSchema()
    return players_df


def main():
    spark,sc,sqlContext = initiate_spark()
    df_15 = read_fifa_data("15",sqlContext)
    df_16 = read_fifa_data("16", sqlContext)
    df_17 = read_fifa_data("17", sqlContext)
    df_18 = read_fifa_data("18", sqlContext)
    df_19 = read_fifa_data("19", sqlContext)
    df_20 = read_fifa_data("20", sqlContext)
    df_21 = read_fifa_data("21", sqlContext)
    df_22 = read_fifa_data("22", sqlContext)
    datasets = [df_22, df_21, df_20, df_17, df_19, df_18, df_16, df_15]

    # list the players who achieved average highest improvement
    find_players_with_highest_improvement(df_15, df_22, 10)
    for df in datasets:
        # find y clubs with the most players whose contracts end in 2021
        find_club_with_most_player_due("21", df, 10)
        # find  z clubs with the largest number of players in the data set where z >=5
        find_clubs_with_most_players(10, df)
        # find most popular nationality each year
        find_most_popular_nationality(df)
        # find the most frequest nation position and team position
        find_most_freq_np_tp(df)


def column_add(a, b):
    return a.__add__(b)


def find_skill_sets(df):
    prefix = ["attacking","skill", "movement", "power", "mentality", "goalkeeping", "defending"]
    skill_sets = []
    # for each of the skill, find its list of columns
    sum_all = "SumAcrossAllSkillSets"
    for pre in prefix:
        for c in df.columns:
            if c.startswith(pre):
                skill_sets.append(c)
    # add a name to identify players
    player_skill = skill_sets
    player_skill.append("SofifaId")
    df_skill = df.select([c for c in player_skill]) \
        .withColumn(sum_all, reduce(column_add, [df[c] for c in skill_sets]))
    return df_skill


def find_players_with_highest_improvement(df1, df2, x):
    print("List of " + str(x) + " players who achieved highest average improvement across all skill sets")
    df_skillset1 = find_skill_sets(df1)
    df_skillset2 = find_skill_sets(df2).withColumnRenamed("SumAcrossAllSkillSets", "New_Sum").withColumnRenamed(
        "SofifaId", "SofifaId2")
    df_avg = df_skillset1.join(df_skillset2, df_skillset1.SofifaId == df_skillset2.SofifaId2)
    df_result =  df_avg.withColumn("Avg_Improvement",((F.col("New_Sum") - F.col("SumAcrossAllSkillSets"))/(len(df_skillset1.columns)-2)).cast("int"))\
    .select("SofifaId","Avg_Improvement").orderBy(F.desc_nulls_last("Avg_Improvement")).show(x)
    df_result.show()
    return df_result


# find y clubs with the most players whose contracts end in 2021
def find_club_with_most_player_due(end_year, df, y):
    result = df.select("club_name", "club_contract_valid_until", "club_team_id") \
        .filter("club_contract_valid_until == 20" + end_year) \
        .groupBy("club_name", "club_team_id").count().orderBy(F.desc("count")).limit(y)
    result.show()
    return result


# find  z clubs with the largest number of players in the data set where z >=5
def find_clubs_with_most_players(z, df):
    print("for this year:")
    club_player_count = df.select("club_name", "club_team_id").filter("club_name != 'null'").groupBy(
        "club_name").count().orderBy(F.desc_nulls_last("count")).limit(z)
    if club_player_count.select("count").distinct().count() == 1:
        print(" all teams have the same amount of players")
    club_player_count.show()
    return club_player_count


# find most frequent nation position and team position
def find_most_freq_np_tp(df):
    # for the team position
    if "team_position" in df.columns:
        print("Most frequent team position is:")
        result = df.select("team_position").groupBy("team_position").count().orderBy(F.desc("count")).limit(1)
        result.show()
    else:
        print("Most frequent team position is:")
        result = df.select("club_position").groupBy("club_position").count().orderBy(F.desc("count")).limit(1)
        result.show()
    # for the nation position
    if "nation_position" in df.columns:
        print("Most frequent nation position is:")
        df.select("nation_position").groupBy("nation_position").count().orderBy(F.desc("count")).show(1)
    else:
        print("There is no enough data about nation position in this dataset")
    return  True

# find the most popular nationality of players
def find_most_popular_nationality(df):
    print("most famous nationality for this year is: ")
    nationality = df.select("nationality_id", "nationality_name").groupBy("nationality_id", "nationality_name").count().orderBy(
        F.desc("count")).limit(1)
    nationality.show()
    return nationality


if __name__ == '__main__':
    main()
