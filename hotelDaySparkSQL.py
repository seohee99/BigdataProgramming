from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark = SparkSession.builder.appName("hotelPrice").getOrCreate()

    df1 = spark.read.load("hdfs:///user/maria_dev/data/hoteldata.csv",
                            format="csv", sep=",", inferSchema = "true", header = "true")

    df1.createOrReplaceTempView("hotel")

    result = spark.sql("""
        select weekday, area_big as area , avg(price) as price
        from hotel
        group by weekday, area_big
        order by area_big, weekday desc
    """)

    for row in result.collect():
        print(row.weekday, row.area, row.price)