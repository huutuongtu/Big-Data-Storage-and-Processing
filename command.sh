# config hdfs
# nano $HADOOP_CONF_DIR/core-site.xml
# nano $HADOOP_CONF_DIR/hdfs-site.xml
$HADOOP_HOME/bin/hdfs namenode -format
#start hdfs
$HADOOP_HOME/sbin/start-dfs.sh
# veryfy if running?
=> Go http://localhost:9870 or check $HADOOP_HOME/bin/hdfs dfsadmin -report
# create directory in hdfs
$HADOOP_HOME/bin/hdfs dfs -mkdir /user
$HADOOP_HOME/bin/hdfs dfs -mkdir /user/hadoop
$HADOOP_HOME/bin/hdfs dfs -mkdir /tweets
# copy data to hdfs
$HADOOP_HOME/bin/hdfs dfs -put /home/tu/BigData/Big-Data-Project/test_bigdata/cleaned.csv /tweets/
# remove? 
hdfs dfs -rm -R /tweets/*.parquet (path)
# how to stop hdfs?
$HADOOP_HOME/sbin/stop-dfs.sh

# start mongodb
systemctl start mongod
# check mongo status
systemctl status mongod
# stop? 
systemctl stop mongod

# For Kafka
cd kafka_2.13-2.8.0
# start zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
# start kafka
bin/kafka-server-start.sh config/server.properties
# if fail because port is used => check and kill id
lsof -n -i :9092 | grep LISTEN

# create topic: 
bin/kafka-topics.sh --create --topic tweets_coin --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic coingecko_coin --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# push data to kafka (streaming)
python /home/tu/BigData/Big-Data-Project/test_bigdata/kafka/tweet_to_kafka.py
python /home/tu/BigData/Big-Data-Project/test_bigdata/kafka/coingecko_to_kafka.py
python /home/tu/BigData/Big-Data-Project/test_bigdata/kafka/binance_to_kafka.py


# check which data push to topic
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic tweets_coin --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic coingecko_coin --from-beginning

# remove topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic tweets_coin
bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic coingecko_coin

# stream data from kafka to mongodb, use spark kafka mongodb connector maven (packages and jars):
/home/tu/BigData/Big-Data-Project/test_bigdata/spark-3.5.3-bin-hadoop3/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --jars /home/tu/BigData/Big-Data-Project/test_bigdata/mongo-spark-connector_2.12-2.4.1.jar /home/tu/BigData/Big-Data-Project/test_bigdata/spark/tweet_kafka_to_mongo_spark.py
/home/tu/BigData/Big-Data-Project/test_bigdata/spark-3.5.3-bin-hadoop3/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --jars /home/tu/BigData/Big-Data-Project/test_bigdata/mongo-spark-connector_2.12-2.4.1.jar /home/tu/BigData/Big-Data-Project/test_bigdata/spark/coingecko_kafka_to_mongo_spark.py
/home/tu/BigData/Big-Data-Project/test_bigdata/spark-3.5.3-bin-hadoop3/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --jars /home/tu/BigData/Big-Data-Project/test_bigdata/mongo-spark-connector_2.12-2.4.1.jar /home/tu/BigData/Big-Data-Project/test_bigdata/spark/binance_kafka_to_mongo_spark.py

# streaming remove old data from mongodb
python /home/tu/BigData/Big-Data-Project/test_bigdata/mongo/streaming_remove_old.py

# check data mongo

python /home/tu/BigData/Big-Data-Project/test_bigdata/mongo/get_mongo_data.py

# flask be
cd /home/tu/BigData/Big-Data-Project/test_bigdata/flask
python main.py
# kafka to hdfs using spark
# $/home/tu/BigData/Big-Data-Project/test_bigdata/spark-3.5.3-bin-hadoop3/bin/spark-submit --master local[2] --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --conf spark.hadoop.hdfs.client.use.datanode.hostname=true /home/tu/BigData/Big-Data-Project/test_bigdata/spark/tweet_streaming.py

# crawl du lieu tweet ve thi dua qua sparkml luon roi moi roi dua vao db => sparkml co the xu ly nhu streaming, de 0.5s 1 tweet co ve van ok
# => thay vi save vao mongodb moi dua qua sparkml se bi do tre luc doc ra => save lai tweet, time, sentiment, ten coin roi moi dua vao mongodb tang trai nghiem nguoi dung