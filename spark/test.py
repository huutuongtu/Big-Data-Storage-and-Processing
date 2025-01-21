from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark
spark = SparkSession.builder \
    .appName("ReadLast10Rows") \
    .getOrCreate()

# HDFS path for the output CSV file
hdfs_path = 'hdfs://localhost:9000/tweets/output.csv'

# Read the CSV file
df = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(hdfs_path)

# Enforce ordering by tweet_id (or any other column indicating order)
ordered_df = df.orderBy(col("tweet_id").desc())

# Select the last 10 rows
latest_rows = ordered_df.limit(10)

# Show the last 10 rows
latest_rows.show(truncate=False)
