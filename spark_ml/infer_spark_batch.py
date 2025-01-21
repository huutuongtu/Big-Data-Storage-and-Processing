from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
import time

# 0 is negative or neutral and 1 is positive
spark = SparkSession.builder \
    .appName("CSV File Prediction") \
    .getOrCreate()

# Load the model
model_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/model.pkl"
loaded_model = PipelineModel.load(model_path)

csv_file_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/cleaned.csv"
input_data = spark.read.csv(csv_file_path, header=True, inferSchema=True)

csv_length = input_data.count()
print(f"The CSV file contains {csv_length} rows.")

# Ensure the input column name matches what the model expects
input_data = input_data.select("text")

start = time.time()
# Perform predictions
predictions = loaded_model.transform(input_data)
end = time.time()

print(f"time to predict 20k sentence ...{end-start}")
# ...0.8394625186920166

# Show the predictions along with the text
predictions.select("text", "prediction").show()

# output_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/predictions.csv"
# predictions.select("text", "prediction").write.csv(output_path, header=True)

# print(f"Predictions saved to {output_path}")
