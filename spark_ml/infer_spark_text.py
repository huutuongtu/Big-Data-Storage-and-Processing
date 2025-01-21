from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.ml import PipelineModel

# 0 is negative or neutral and 1 is positive
spark = SparkSession.builder \
    .appName("Single Text Prediction") \
    .getOrCreate()

model_path = "hdfs://localhost:9000/models/model.pkl"
loaded_model = PipelineModel.load(model_path)

text_input = "top crypto trend momentum wan bts icx iost rlc best coins read"
single_data = spark.createDataFrame([Row(text=text_input)])
prediction = loaded_model.transform(single_data)

# Show the prediction result
prediction.select("text", "prediction").show()

predicted_label = prediction.collect()[0]["prediction"]
print(f"Predicted label: {predicted_label}")


# Dataset: https://www.kaggle.com/datasets/gautamchettiar/bitcoin-sentiment-analysis-twitter-data?resource=download
# 0: negative/neutral
# 1: positive
# import pandas as pd

# data = pd.read_csv("/home/tu/BigData/Big-Data-Project/test_bigdata/bitcoin_tweets1000000.csv", encoding='latin1', on_bad_lines='skip',)

# filtered_data = data[['cleanText', 'sentiment']]

# # Save the filtered data to a new CSV file
# output_csv = "/home/tu/BigData/Big-Data-Project/test_bigdata/cleaned.csv"
# filtered_data.to_csv(output_csv, index=False)

# print(f"Filtered CSV saved to: {output_csv}")