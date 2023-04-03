import findspark
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
import logging
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.3.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 pyspark-shell'


findspark.init()

kafka_topic_name = "albums"
kafka_bootstrap_servers = '192.168.209.151:9092'


def write_row_in_mongo(df, dd):
    print(df.show())
    print(df.printSchema())
    df.write.format("com.mongodb.spark.sql.DefaultSource").mode(
        "append").save()
    pass


# spark = SparkSession \
#     .builder \
#     .appName("Spotify") \
#     .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2") \
#     .config("spark.mongodb.input.uri", "mongodb+srv://bkfashionshop:project1@bigdata.mncihbp.mongodb.net/test.Albums")\
#     .config("spark.mongodb.output.uri", "mongodb+srv://bkfashionshop:project1@bigdata.mncihbp.mongodb.net/test.Albums")\
#     .getOrCreate() \

spark = SparkSession \
    .builder \
    .master("spark://192.168.213.151:7077") \
    .appName("Spotify") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2") \
    .config("spark.mongodb.input.uri", "mongodb+srv://nghiango:nghiango23102001@cluster0.pjnmw.mongodb.net/BIGDATA.spotify_db")\
    .config("spark.mongodb.output.uri", "mongodb+srv://nghiango:nghiango23102001@cluster0.pjnmw.mongodb.net/BIGDATA.spotify_db")\
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
    StructField("album_type", StringType(), True),
    StructField("artists", StructType(
        [
            StructField("external_urls", StructType([
                StructField("spotify", StringType(), True)
            ]), True),
            StructField("spotify", StringType(), True),
            StructField("id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("type", StringType(), True),
            StructField("uri", StringType(), True),
        ]
    ), True),
    StructField("available_markets", ArrayType(StringType(), False), True),
    StructField("external_urls", StructType([
        StructField("spotify", StringType(), True)
    ]), True),
    StructField("href", StringType(), True),
    StructField("id", StringType(), True),
    StructField("images", StructType([
        StructField("height", IntegerType(), True),
        StructField("url", StringType(), True),
        StructField("width", IntegerType(), True),
    ]), True),
    StructField("name", StringType(), True),
    StructField("release_date", StringType(), True),
    StructField("release_date_precision", StringType(), True),
    StructField("total_tracks", StringType(), True),
    StructField("type", StringType(), True),
    StructField("uri", StringType(), True),

])


table = songs_df.select(
    from_json(songs_df.value.cast("string"), schema).alias("albums"))

print("=====================")
query = table.select("albums.release_date", "albums.name")
print(query.printSchema())
print("=====================")

transaction_detail_write_stream = query \
    .writeStream \
    .format('console') \
    .foreachBatch(write_row_in_mongo) \
    .start()

transaction_detail_write_stream.awaitTermination()
