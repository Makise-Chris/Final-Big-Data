import findspark
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
import logging
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.3.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 pyspark-shell'


findspark.init()

kafka_topic_name = "tracks"
#kafka_bootstrap_servers = 'localhost:9092,192.168.209.195:9092'
kafka_bootstrap_servers = '192.168.209.151:9092'


def write_row_in_mongo(df, dd):
    print(df.show())
    print(df.printSchema())
    df.write.format("com.mongodb.spark.sql.DefaultSource").mode(
        "append").save()
    pass


spark = SparkSession \
    .builder \
    .master("spark://192.168.209.151:7077,192.168.209.195:7077") \
    .appName("Spotify") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2") \
    .config("spark.mongodb.input.uri", "mongodb+srv://nghiango:nghiango23102001@cluster0.pjnmw.mongodb.net/BIGDATA.Tracks")\
    .config("spark.mongodb.output.uri", "mongodb+srv://nghiango:nghiango23102001@cluster0.pjnmw.mongodb.net/BIGDATA.Tracks")\
    .getOrCreate() \

spark.sparkContext.setLogLevel("ERROR")

# Construct a streaming DataFrame that reads from test-topic
songs_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .load()

schema = StructType([
    StructField("artists", ArrayType(StructType([
        StructField("external_urls", StructType(
                [StructField("spotify", StringType(), True)]), True),
        StructField("href", StringType(), True),
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("type", StringType(), True),
        StructField("uri", StringType(), True)]), True), True),
    StructField("available_markets", ArrayType(StringType(), True), True),
    StructField("disc_number", IntegerType(), True),
    StructField("duration_ms", IntegerType(), True),
    StructField("explicit", BooleanType(), True),
    StructField("external_urls", StructType(
        [StructField("spotify", StringType(), True)]), True),
    StructField("href", StringType(), True),
    StructField("id", StringType(), True),
    StructField("is_local", BooleanType(), True),
    StructField("name", StringType(), True),
    StructField("preview_url", StringType(), True),
    StructField("track_number", IntegerType(), True),
    StructField("type", StringType(), True),
    StructField("uri", StringType(), True),
    StructField("feature", StructType([
        StructField("danceability", DoubleType(), True),
        StructField("energy", DoubleType(), True),
                StructField("key", IntegerType(), True),
                StructField("loudness", DoubleType(), True),
                StructField("mode", IntegerType(), True),
                StructField("speechiness", DoubleType(), True),
                StructField("acousticness", DoubleType(), True),
                StructField("instrumentalness", IntegerType(), True),
                StructField("liveness", DoubleType(), True),
                StructField("valence", DoubleType(), True),
                StructField("tempo", DoubleType(), True),
                StructField("type", StringType(), True),
                StructField("id", StringType(), True),
                StructField("uri", StringType(), True),
                StructField("track_href", StringType(), True),
                StructField("analysis_url", StringType(), True),
                StructField("duration_ms", IntegerType(), True),
                StructField("time_signature", IntegerType(), True),
                ]), True),
    StructField("popularity", IntegerType(), True),
    StructField("release_year", StringType(), True),
])

table = songs_df.select(
    from_json(songs_df.value.cast("string"), schema).alias("tracks"))

query = table.select("tracks.*")

transaction_detail_write_stream = query \
    .writeStream \
    .format('console') \
    .foreachBatch(write_row_in_mongo) \
    .start()

transaction_detail_write_stream.awaitTermination()
