from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType, MapType, DoubleType
from pymongo import MongoClient

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaToMongoDBWithPriceChanges") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/test_database.coingecko_collection") \
    .getOrCreate()

# Define Kafka topic and brokers
kafka_brokers = 'localhost:9092'
topic = 'coingecko_coin'

# Schema for Kafka data
schema = StructType([
    StructField("id", StringType(), True),
    StructField("change", StringType(), True),
])


# Read Kafka stream
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", topic) \
    .option("failOnDataLoss", "false") \
    .load()

# Parse Kafka messages
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")  # Flatten the structure


def write_to_mongo(batch_df, batch_id):
    if batch_df.isEmpty():
        print(f"Batch {batch_id} is empty. Skipping.")
        return

    # Debug: Show batch data
    batch_df.show(truncate=False) 
    
    # Convert to Pandas for processing
    batch_data = batch_df.toPandas().to_dict(orient='records')
    print(f"Batch {batch_id} data: {batch_data}") 

    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_database"]
    collection = db["coingecko_collection"]
    
    for record in batch_data:
        if record["id"] is None or record["change"] is None:
            print(f"Skipping record due to missing fields: {record}")  # Debug: Skip invalid records
            continue

        collection.update_one(
            {"id": record["id"]},  # Match document by "id"
            {"$set": record},      # Update fields or insert if not exists
            upsert=True            # Enable upsert
        )
    
    print(f"Batch {batch_id} successfully written to MongoDB.")


    
# Write processed stream to MongoDB
query = parsed_df \
    .writeStream \
    .foreachBatch(write_to_mongo) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
