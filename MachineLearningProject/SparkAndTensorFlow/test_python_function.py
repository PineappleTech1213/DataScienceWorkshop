# -*- coding = utf-8 -*-
# @Time:4/21/22 5:19 PM
# @Author: Zheng Zeng
# @File: test_python_function.py
# @Goal:
from ProjectTask2 import *
from ProjectTaskI import *

appName = "Fifa Unit Testing"
master = "local"

# Create Configuration object for Spark.
conf = pyspark.SparkConf() \
    .set('spark.driver.host', '192.168.1.216') \
    .setAppName(appName) \
    .setMaster(master)

# Create Spark Context with the new configurations rather than rely on the default one
sc = SparkContext.getOrCreate(conf=conf)

# You need to create SQL Context to conduct some database operations like what we will see later.
sqlContext = SQLContext(sc)

# If you have SQL context, you create the session from the Spark Context
spark = SparkSession.builder.getOrCreate()

def test_read_fifa_data(year):
    assert isinstance(year,str), "The year variable you give is not in a string format"
    assert read_fifa_data(year,sqlContext).toPandas() is not None, "Returned dataframe is None but it should not be"

def test_find_skill_sets():
    test_df = spark.createDataFrame(
        [(10,20,30,"001"),
         (30,40,40,"002"),
         (19,34,54,"003")],
         ["attacking_crossing","skill_dribbling","movement_acceleration","SofifaId"]
    )
    assert find_skill_sets(test_df) is not None,"Returned dataframe is None "
    assert find_skill_sets(test_df).select("SumAcrossAllSkillSets") is not None, "There is no result column"
def test_find_players_with_highest_improvement(x):
    expected_output = spark.createDataFrame(
        [('001', 25),
         ('002', 21),
         ('003', 40),
         ('004', 40),
         ('005', 40),
         ('006', 40),
         ('007', 40)],
        ['SofifaId', 'Avg_Improvement'],
    )
    test_df = spark.createDataFrame(
        [(10,20,30,"001"),
         (30,40,40,"002"),
         (19,34,54,"003"),
         (19,34,51,"004"),
         (23,34,33,"005"),
         (19,10,54,"007"),
         (12,34,54,"006")],
         ["attacking_crossing","skill_dribbling","movement_acceleration","SofifaId"]
    )
    test_df2 = spark.createDataFrame(
        [(24, 20, 30, "001"),
         (31, 40, 40, "002"),
         (55, 34, 54, "003"),
         (19, 54, 41, "004"),
         (25, 14, 33, "005"),
         (19, 10, 24, "007"),
         (12, 34, 34, "006")],
         ["attacking_crossing","skill_dribbling","movement_acceleration","SofifaId"]
    )
    assert  isinstance(x,int), "x is not an integer, which is wrong"

    real_output = find_players_with_highest_improvement(test_df,test_df2,x)
    pd.testing.assert_frame_equal(
        expected_output.toPandas(),
        real_output.toPandas(),
        check_like=True
    )
    assert  real_output.count() == x,"The number of players provided is not correct"

def test_find_club_with_most_player_due(end_year,y):
    assert isinstance(end_year,str),"please enter end_year in a string format"
    assert end_year =="21", "We only look for contracts ending in 2021!"
    assert isinstance(y,int),"the y value is not an integer, which is wrong!"
    test_df = spark.createDataFrame(
        [('abc','001'),
         ('abc', '001'),
         ('abc', '001'),
         ('hhk', '002'),
         ('hhl', '004'),
         ('abc', '001'),
         ('hhk', '002')],
         ["club_name", "club_team_id"]
    )
    expected_output = spark.createDataFrame(
        [('abc','001',20),
         ('edg','002',10),
         ('hhk','003',25)],
        ["club_name", "club_team_id","count"]
    )

    pd.testing.assert_frame_equal(find_club_with_most_player_due(end_year,test_df,y).toPandas(),expected_output.toPandas(),
                                  check_like=True)


def test_find_clubs_with_most_players(z):
    assert isinstance(z,int),"z is not an integer,which is wrong!"
    assert z >=5, "z is smaller than 5, please enter a value that is no less than 5!"
    test_df = spark.createDataFrame(
        [('abc','001'),
         ('abc', '001'),
         ('abc', '001'),
         ('hhk', '002'),
         ('hhl', '004'),
         ('abc', '001'),
         ('hhk', '002')],
         ["club_name", "club_team_id"]
    )
    expected_output = spark.createDataFrame(
        [('abc','001',20),
         ('edg','002',10),
         ('hhk','003',25)],
        ["club_name", "club_team_id","count"]
    )

    pd.testing.assert_frame_equal(find_clubs_with_most_players(z,test_df).toPandas(),expected_output.toPandas(),
                                  check_like=True)

def test_find_most_freq_np_tp():
    test_df1 = spark.createDataFrame(
        [('abc'),
         ('abc'),
         ('abc'),
         ('hhk'),
         ('hhl'),
         ('abc'),
         ('hhk')],
         ["club_position"]
    )
    test_df2 = spark.createDataFrame(
        [('abc'),
         ('abc'),
         ('abc'),
         ('hhk'),
         ('hhl'),
         ('abc'),
         ('hhk')],
         ["team_position"]
    )
    test_df3 = spark.createDataFrame(
        [('abc'),
         ('abc'),
         ('abc'),
         ('hhk'),
         ('hhl'),
         ('abc'),
         ('hhk')],
         ["nation_position"]
    )
    assert find_most_freq_np_tp(test_df1) is True, "The program cannot run because of the data is not correct"
    assert find_most_freq_np_tp(test_df2) is True, "The program cannot run because of the data is not correct"
    assert find_most_freq_np_tp(test_df3) is True, "The program cannot run because of the data is not correct"
def test_find_most_popular_nationality():
    test_df = spark.createDataFrame(
        [('abc','001'),
         ('abc', '001'),
         ('abc', '001'),
         ('hhk', '002'),
         ('hhl', '004'),
         ('abc', '001'),
         ('hhk', '002')],
         ["club_name", "club_team_id"]
    )
    expected_output = spark.createDataFrame(
        [('001','abc',1)],
        ["nationality_id","nationality_name","count"]
    )
    assert find_most_popular_nationality(test_df).count()==1,"The number of result is not correct!"
    pd.testing.assert_frame_equal(find_most_popular_nationality(test_df).toPandas(),expected_output.toPandas(),
                                  check_frame_type=True,
                                  check_column_type=True)



test_read_fifa_data("15")
test_find_skill_sets()
test_find_players_with_highest_improvement(10)
test_find_club_with_most_player_due('21',10)
test_find_clubs_with_most_players(10)
test_find_most_freq_np_tp()
test_find_most_popular_nationality()
