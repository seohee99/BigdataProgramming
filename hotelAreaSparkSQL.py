from pyspark.sql import SparkSession
import sys

if __name__ == '__main__':

    spark = SparkSession.builder.appName("hotelPrice").getOrCreate()

    df1 = spark.read.load("hdfs:///user/maria_dev/data/hoteldata.csv",
                            format="csv", sep=",", inferSchema = "true", encoding='utf8',header = "true")

    df1.createOrReplaceTempView("hotel")

    result = spark.sql("""
        select stars, area_big as area, avg(price) as price
        from hotel
        group by stars, area_big
        order by area_big, stars desc
    """)

    for row in result.collect():
        print(row.stars, row.area, row.price)