from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, IDF
from pyspark.ml.feature import HashingTF
from pyspark.ml.classification import LogisticRegression

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .appName("Sentiment Analysis") \
    .getOrCreate()

# for hdfs
# file_path = "hdfs://localhost:9000/tweets/test.csv"

# for current device
file_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/cleaned.csv"
data = spark.read.csv(file_path, header=True, inferSchema=True)

data.show()
# should drop nan if we dont want bug
data = data.dropna()

tokenizer = Tokenizer(inputCol="text", outputCol="words")
stop_words_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
count_vectorizer = CountVectorizer(inputCol="filtered_words", outputCol="raw_features")
idf = IDF(inputCol="raw_features", outputCol="features")

label_indexer = StringIndexer(inputCol="sentiment", outputCol="label")

classifier = LogisticRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[tokenizer, stop_words_remover, count_vectorizer, idf, label_indexer, classifier])

train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

model = pipeline.fit(train_data)

predictions = model.transform(test_data)
predictions.select("text", "label", "prediction").show()

model_path = "file:///home/tu/BigData/Big-Data-Project/test_bigdata/big_model.pkl"
model.write().overwrite().save(model_path)

print(f"Model saved to {model_path}")
