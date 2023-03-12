
#deal with outliers
#here is to deal with outliers with codes from lectures
from functools import reduce
#import 
import pyspark
from pyspark import SparkContext #for unabling to set up sc by yourself
from pyspark.sql import SparkSession, SQLContext #spark dataframe = spark sql
from pyspark.sql.functions import to_date, col, count,when,lit,rand,to_timestamp,udf
from pyspark.sql.functions import concat_ws, substring,isnan,regexp_replace,concat
from pyspark.sql.functions import udf,regexp_extract, monotonically_increasing_id
from pyspark.ml.feature import Imputer

from pyspark.ml.feature import StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler

#decision tree regressor
from pyspark.ml.regression import GBTRegressor

#read the data from the databse
def read_data(tablename,sqlContext):
    play_df = sqlContext.read.format("jdbc")\
    .option("url", "jdbc:postgresql://localhost:5432/postgres")\
    .option("dbtable", tablename)\
    .option("user", "postgres")\
    .option("password", "postgres")\
    .option("Driver", "org.postgresql.Driver")\
    .load()
    play_df.printSchema()
    return play_df

#define sql functions
def column_add(a,b):
     return  a.__add__(b)
#define find outliers' function
def find_outliers(df):
    # Identifying the numerical columns in a spark dataframe
    numeric_columns = [column[0] for column in df.dtypes if column[1]=='int']

    # Using the `for` loop to create new columns by identifying the outliers for each feature
    for column in numeric_columns:

        less_Q1 = 'less_Q1_{}'.format(column)
        more_Q3 = 'more_Q3_{}'.format(column)
        Q1 = 'Q1_{}'.format(column)
        Q3 = 'Q3_{}'.format(column)

        # Q1 : First Quartile ., Q3 : Third Quartile
        Q1 = df.approxQuantile(column,[0.25],relativeError=0)
        Q3 = df.approxQuantile(column,[0.75],relativeError=0)
        
        # IQR : Inter Quantile Range
        # We need to define the index [0], as Q1 & Q3 are a set of lists., to perform a mathematical operation
        # Q1 & Q3 are defined seperately so as to have a clear indication on First Quantile & 3rd Quantile
        IQR = Q3[0] - Q1[0]
        
        #selecting the data, with -1.5*IQR to + 1.5*IQR., where param = 1.5 default value
        less_Q1 =  Q1[0] - 1.5*IQR
        more_Q3 =  Q3[0] + 1.5*IQR
        
        isOutlierCol = 'is_outlier_{}'.format(column)
        
        df = df.withColumn(isOutlierCol,when((df[column] > more_Q3) | (df[column] < less_Q1), 1).otherwise(0))
    

    # Selecting the specific columns which we have added above, to check if there are any outliers
    selected_columns = [column for column in df.columns if column.startswith("is_outlier")]
    # Adding all the outlier columns into a new colum "total_outliers", to see the total number of outliers
    df = df.withColumn('total_outliers',reduce(column_add, ( df[col] for col in  selected_columns)))

    # Dropping the extra columns created above, just to create nice dataframe., without extra columns
    df = df.drop(*[column for column in df.columns if column.startswith("is_outlier")])

    return df

def main():
        #ingest data from previous play data in postgres
        #building spark session
    appname = "homework4" #define app name
    master = "local"

    config = pyspark.SparkConf().setAppName(appname)\
    .setMaster(master) #we do not have any workers.


    #session
    #with sql context, create session from it
    sc  = SparkContext.getOrCreate(conf=config)
    sqlContext = SQLContext(sc)
    #don't create many sessions, take up too much room!
    sp_session = sqlContext.sparkSession.builder.getOrCreate();
    #export data into postgresql


    plays_df =read_data("NFL.PLAYS")
    games= read_data("NFL.GAMES")
    team_plays = read_data("NFL.SPECIAL_TM_PLAY")

    #clean the data
    #join plays with team play type data
    plays_df.select("PassResult").distinct().show()
    plays_with_teamplay = plays_df.join(team_plays,plays_df.SpTeamPlayId  == team_plays.SpTeamPlayId).drop("SpTeamPlayId")
    #rename the id in games data
    renamed_games = games.withColumnRenamed('gameid','gameid2')\
    .withColumn("gamelength", col("GameLength").cast("int")).drop("GameLength")

    # renamed_games.printSchema()
    #join plays with games 
    plays_with_games = plays_with_teamplay.join(renamed_games, renamed_games.gameid2 == plays_with_teamplay.gameid)
    # plays_with_games.show(1,vertical=True)
    #calculate games' incomplete pass
    games_pass = plays_with_games.select("gameid","PassResult")\
    .groupBy(col("gameid")).agg(count(when(col("PassResult") == 'I',1)).alias("IPcount"))
    # games_pass.show(1,vertical=True)

    #join the pass result count with plays_with_games
    games_df = plays_with_games.join(games_pass,plays_with_games.gameid == games_pass.gameid).drop('gameid')\
    .select("playid","gameid2","IPcount","SpecialTeamsPlayType","possessionTeam","isSTPlay","offenseFormation",
            "personnel_off","personnel_def","yardlineSide",
            "yardlineNumber","KickReturn","number_PassRushers","defenders_InTheBox","YardAfterCatch",
        "Pass_Length","yardsToGo","HomeScore","VisitorScore").withColumn("yardline_number", col("yardLineNumber").cast("int")).drop("yardLineNumber")
    games_df.printSchema()
    #see the distribution of the incomplete pass count
    games_df.groupBy("IPcount").count().show()
    #start data cleaning process 
#make sure there is no null value

    numeric_cols = [column[0] for column in games_df.dtypes if column[1]=="int"]
    games_df.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in numeric_cols]).show(vertical=True)
    #yardline_number is not imputed
    games_df_filled_na = games_df.fillna(-200, 'yardline_number')

    imputer = Imputer (
                inputCol='yardline_number',
                outputCol='yardlin_number_imputed')\
                    .setStrategy("median").setMissingValue(-200)

    games_df_imputed = imputer.fit(games_df_filled_na).transform(games_df_filled_na).drop('yardline_number')


    numeric_cols = [column[0] for column in games_df_imputed.dtypes if column[1]=="int"]
    games_df_imputed.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in numeric_cols]).show(vertical=True)
#find outliers in games
    
    games_with_outliers = find_outliers(games_df_imputed)
    encoded_games_df = handleCategoricalData(games_without_outliers)
    #vectorize the categories

    vector_assembler = VectorAssembler(
    inputCols=['special_teamplay_encoded','possessionTeam_encoded','personnel_offense_encoded','personnel_defense_encoded',
               'offenseFormation_encoded','yardlineSide_encoded','isSTPlay_encoded',
                              'yardsToGo', "yardlin_number_imputed","Pass_Length","KickReturn",
               "defenders_InTheBox","number_PassRushers","YardAfterCatch"], 
    outputCol="vectorized_features")

    assembled_games_df = vector_assembler.transform(encoded_games_df)

# view the transformed data
    assembled_games_df.printSchema()
    #create ML model data
    games_model_df = assembled_games_df.withColumn("outcome", col("IPcount").cast("int")).drop("IPcount")
    train, test = games_model_df.randomSplit([0.8, 0.2], seed = 1125)
    print("Number of records for training purposes is: " + str(train.count()))
    print("Number of records for testing purposes is: " + str(test.count()))
                

def handleCategoricalData(games_without_outliers):

#handling categorical variables
    games_df_without_binary = (games_without_outliers.drop("total_outliers")\
                                    .withColumn("isSTPlay_encoded", 
                                                games_without_outliers["isSTPlay"].cast("integer")).drop("isSTPlay"))

    #create pipeline to index categorical values
    stage_1 = StringIndexer(inputCol= 'possessionTeam', outputCol= 'possessionTeam_index', handleInvalid="keep")

    stage_2 = StringIndexer(inputCol= 'personnel_off', outputCol= 'personnel_offense_index', handleInvalid="keep")

    stage_3 = StringIndexer(inputCol= 'personnel_def', outputCol= 'personnel_defense_index', handleInvalid="keep")

    stage_4 = StringIndexer(inputCol= 'offenseFormation', outputCol= 'offenseFormation_index', handleInvalid="keep")

    stage_5 = StringIndexer(inputCol= 'yardlineSide', outputCol= 'yardlineSide_index', handleInvalid="keep")

    stage_6 = StringIndexer(inputCol='SpecialTeamsPlayType',outputCol = 'special_teamplay_index',handleInvalid = "keep")



    # define one hot encode of the numeric columns
    stage_7 = OneHotEncoder(inputCols=['special_teamplay_index','possessionTeam_index','personnel_offense_index','personnel_defense_index',
                                    'offenseFormation_index','yardlineSide_index'], 
                            outputCols=['special_teamplay_encoded','possessionTeam_encoded','personnel_offense_encoded','personnel_defense_encoded',
                                    'offenseFormation_encoded','yardlineSide_encoded'])

    # setup the pipeline
    pipeline = Pipeline(stages=[stage_1, stage_2, stage_3, stage_4, stage_5, stage_6, stage_7])

    # fit the pipeline model and transform the data as defined
    pipeline_model = pipeline.fit(games_df_without_binary)
    encoded_games_df = pipeline_model.transform(games_df_without_binary)

    # view the transformed data

    encoded_games_df.printSchema()
    return encoded_games_df
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import BinaryClassificationEvaluator

#linear regression
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
def createModel(train, test,model_type = "linear"):
    if model_type =='linear':
        #since outcome is a continuous variable, we can do regression 
    #use cross validation to find the best hyper parameters
        lr = LinearRegression(featuresCol='vectorized_features',labelCol='outcome')
        lr_evaluator = RegressionEvaluator(predictionCol="prediction", \
                        labelCol="outcome",metricName="r2")
        # Create ParamGrid for Cross Validation
        paramGrid = (ParamGridBuilder()
                    .addGrid(lr.regParam, [0.01, 0.1, 0.5])# regularization parameter
                    .addGrid(lr.maxIter, [5, 10, 15])#Number of iterations
                    .addGrid(lr.elasticNetParam, [0.1,0.3,0.8])
                    .build())
        cv = CrossValidator(estimator=lr, estimatorParamMaps=paramGrid, 
                            evaluator=lr_evaluator, numFolds=5)
        lrModel = cv.fit(train)
        lr_predictions = lrModel.transform(test)
        print("R Squared (R2) of linear regression model on test data = %g" % lr_evaluator.evaluate(lr_predictions))
    elif model_type == 'gbt':
        gbt = GBTRegressor(featuresCol = 'vectorized_features', labelCol = 'outcome')

        gbt_evaluator = RegressionEvaluator(
            labelCol="outcome", predictionCol="prediction", metricName="r2")
        param_grid = (ParamGridBuilder().addGrid(gbt.maxDepth,[5,7,9]).addGrid(gbt.maxIter, [20,30,40]).build())
        gbt_cv  = CrossValidator(estimator = gbt,estimatorParamMaps=param_grid,evaluator=gbt_evaluator,numFolds=5)
        gbt_model = gbt_cv.fit(train)

        gbt_predictions = gbt_model.transform(test)

        gbt_r2 = gbt_evaluator.evaluate(gbt_predictions)
        print("R Squared (R2) of decision tree model on test data = %g" % gbt_r2)