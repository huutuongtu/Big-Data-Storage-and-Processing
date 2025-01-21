from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, StructField

# Initialize Spark
spark = SparkSession.builder \
    .appName("KafkaToHDFS_CSV") \
    .getOrCreate()

# Schema for tweets
schema = StructType([
    StructField("tweet_id", StringType(), True),
    StructField("time", StringType(), True),
    StructField("tweet_text", StringType(), True)
])

# Kafka topic and HDFS path
kafka_brokers = 'localhost:9092'
topic = 'tweets_coin'
hdfs_path = 'hdfs://localhost:9000/tweets/output.csv'

# Read Kafka stream
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", topic) \
    .option("failOnDataLoss", "false") \
    .load()

# Parse and transform data
tweets = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Save to HDFS as a single CSV file
# if error metadata 0 => , we can change the checkpointLocation here, so it can continue running
query = tweets \
    .coalesce(1) \
    .writeStream \
    .format("csv") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints_csv_") \
    .option("path", hdfs_path) \
    .option("header", "true") \
    .trigger(processingTime='20 seconds') \
    .start()

# Wait for the query to finish
query.awaitTermination()
