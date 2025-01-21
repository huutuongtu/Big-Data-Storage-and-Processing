from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, StructField, Row
from pyspark.ml import PipelineModel
from pymongo import MongoClient

spark = SparkSession.builder \
    .appName("KafkaToMongoDBWithSentiment") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/test_database.test_collection") \
    .getOrCreate()

model_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/model.pkl"
loaded_model = PipelineModel.load(model_path)

schema = StructType([
    StructField("tweet_id", StringType(), True),
    StructField("time", StringType(), True),
    StructField("tweet_text", StringType(), True)
])

# kafka config
kafka_brokers = 'localhost:9092'
topic = 'tweets_coin'

# Read Kafka stream
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", topic) \
    .option("failOnDataLoss", "false") \
    .load()

tweets = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Rename to match model input
tweets = tweets.withColumnRenamed("tweet_text", "text")

def write_to_mongo(batch_df, batch_id):
    if batch_df.isEmpty():
        print(f"Batch {batch_id} is empty. Skipping.")
        return
    
    batch_data = batch_df.toPandas().to_dict(orient='records')
    
    if not batch_data:  # if no new data => return
        print(f"Batch {batch_id} contains no valid data after conversion. Skipping.")
        return
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_database"]
    collection = db["test_collection"]
    
    collection.insert_many(batch_data)
    print(f"Batch {batch_id} successfully written to MongoDB.")

# predict
predicted_tweets = loaded_model.transform(tweets) \
    .select("tweet_id", "time", "text", "prediction")

# them write to mongo
query = predicted_tweets \
    .writeStream \
    .foreachBatch(write_to_mongo) \
    .outputMode("append") \
    .start()
    # .trigger(processingTime='20 seconds') \
    # .start()

query.awaitTermination()
