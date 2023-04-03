import logging
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.3.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import findspark

findspark.init()

kafka_topic_name = "artists"
#kafka_bootstrap_servers = 'localhost:9092,192.168.213.168:9092'
kafka_bootstrap_servers = '192.168.213.151:9092'

def write_row_in_mongo(df, dd):
    print(df.show())
    print(df.printSchema())
    df.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
    pass

spark = SparkSession \
        .builder \
        .master("spark://192.168.213.151:7077") \
        .appName("Spotify") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2") \
        .config("spark.mongodb.input.uri","mongodb+srv://bkfashionshop:project1@bigdata.mncihbp.mongodb.net/test.Artists2")\
        .config("spark.mongodb.output.uri","mongodb+srv://bkfashionshop:project1@bigdata.mncihbp.mongodb.net/test.Artists2")\
        .getOrCreate() \

spark.sparkContext.setLogLevel("ERROR")

# Construct a streaming DataFrame that reads from test-topic
# artists_df = spark \
#         .readStream \
#         .format("kafka") \
#         .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
#         .option("subscribe", kafka_topic_name) \
#         .option("group.id", "testgroup") \
#         .load()

artists_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic_name) \
        .load()

schema = StructType([ \
        StructField("external_urls",
               StructType([StructField("spotify",StringType(),True)]),True), \
        StructField("followers",
                StructType(
                        [StructField("href",StringType(),True), 
                        StructField("total",IntegerType(),True)]),True), \
        StructField("genres",StringType(),True), \
        StructField("href", StringType(), True), \
        StructField("id", StringType(), True), \
        StructField("images", 
                StructType(
                        [StructField("image1",StringType(),True),
                        StructField("image2",StringType(),True),
                        StructField("image3",StringType(),True)]), True), \
        StructField("name", StringType(), True), \
        StructField("popularity", IntegerType(), True), \
        StructField("type", StringType(), True), \
        StructField("uri", StringType(), True), \
  ])

table = artists_df.select(from_json(artists_df.value.cast("string"), schema).alias("artists"))

# print("=====================")
# query = table.select("artists.*")
# print(query.printSchema())
# print("=====================")

# transaction_detail_write_stream = query \
#                                 .writeStream \
#                                 .format('console') \
#                                 .foreachBatch(write_row_in_mongo) \
#                                 .start()
                                
# transaction_detail_write_stream.awaitTermination()

print("=====================")
query = table.select("artists.name", "artists.followers.total", "artists.popularity")
print(query.printSchema())
print("=====================")


transaction_detail_write_stream = query \
                                .writeStream \
                                .format("console") \
                                .foreachBatch(write_row_in_mongo) \
                                .start()

transaction_detail_write_stream.awaitTermination()