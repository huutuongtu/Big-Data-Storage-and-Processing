# maven for spark mongodb connector download
https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/2.4.1/mongo-spark-connector_2.12-2.4.1.jar

# install mongodb - 22.04 jammy
# follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
sudo apt-get install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org


#install hdfs and run as localhost:9000
# first we need to make sure that java is installed
java -version
# then install hadoop
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xzvf hadoop-3.3.6.tar.gz
cd hadoop-3.3.6
# set hadoop environment
# write env to hadoop 
nano ~/.bashrc
export HADOOP_HOME=/home/tu/BigData/Big-Data-Project/test_bigdata/hadoop-3.3.6  # Adjust this path to where you installed Hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export SPARK_HOME=/home/tu/BigData/Big-Data-Project/test_bigdata/spark-3.5.3-bin-hadoop3
# apply change
source ~/.bashrc  # or source ~/.bash_profile

# Then config for hadoop
# Hadoop comes with several configuration files located in the etc/hadoop directory. You'll need to modify these files to set up HDFS and make it run on localhost.
# => 
#     Open the core-site.xml file for editing:
nano $HADOOP_CONF_DIR/core-site.xml
# add this:
# config add above the core-site
# <configuration>
#     <property>
#         <name>fs.defaultFS.name</name>
#         <value>hdfs://localhost:9000</value>
#     </property>
# </configuration>

nano $HADOOP_CONF_DIR/hdfs-site.xml
# add this:
# <configuration>
#     <property>
#         <name>dfs.replication</name>
#         <value>1</value>
#     </property>
#     <property>
#         <name>dfs.name.dir</name>
#         <value>/tmp/hadoop/dfs/name</value>
#     </property>
#     <property>
#         <name>dfs.data.dir</name>
#         <value>/tmp/hadoop/dfs/data</value>
#     </property>
# </configuration>

# format hdfs file system
$HADOOP_HOME/bin/hdfs namenode -format

# then start namenode (master)
$HADOOP_HOME/sbin/start-dfs.sh
# stop?
$HADOOP_HOME/sbin/stop-dfs.sh
# verify if hadoop is running
$HADOOP_HOME/bin/hdfs dfsadmin -report
# or check
# http://localhost:9870
# create directory in hdfs
$HADOOP_HOME/bin/hdfs dfs -mkdir /user
$HADOOP_HOME/bin/hdfs dfs -mkdir /user/hadoop
$HADOOP_HOME/bin/hdfs dfs -mkdir /tweets
# copy data to hdfs
$HADOOP_HOME/bin/hdfs dfs -put /home/tu/BigData/Big-Data-Project/test_bigdata/test.csv /tweets/
# remove?
hdfs dfs -rm -R /tweets/*.parquet
# if can't push or remove?: dfsadmin -safemode leave   

# batch processing
# to verify whether data is push or not: 
hdfs dfs -ls /tweets/
# check if data is available?
hdfs dfs -tail /tweets/test.csv
# now we can run spark

# install kafka
wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.13-2.8.0.tgz
tar -xvzf kafka_2.13-2.8.0.tgz

# start zoo keeper with kafka and crreate topic
cd kafka_2.13-2.8.0
# start zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
# start kafka
bin/kafka-server-start.sh config/server.properties
# if fail => check lsof -n -i :9092 | grep LISTEN
# kill 2 pid

# now install spark
wget https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
tar -xvzf spark-3.5.3-bin-hadoop3.tgz
cd spark-3.5.3-bin-hadoop3
pip install pyspark



# then create kafka producer
# install
pip install confluent-kafka
# then kafka producer code, to push data to topics kafka 

# then Set Up Spark to Consume Data from Kafka and Store to HDFS
# create tweet_streaming in spark tweet_streaming.py
# create topic
bin/kafka-topics.sh --create --topic tweets_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic tweets_coin --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# tweets_coin
# verify if data is publish to topic or not:
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic tweets_topic --from-beginning # we see that tweet text is pushed
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic tweets_coin --from-beginning # we see that tweet text is pushed

# remove record in topic?
bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic tweets_topic


# then install flask 
pip install flask


# python /home/tu/BigData/Big-Data-Project/test_bigdata/test_read_data_hdfs.py
