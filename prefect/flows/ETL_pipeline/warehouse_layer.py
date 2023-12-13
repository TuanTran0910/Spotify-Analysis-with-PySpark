from prefect import task
from prefect.tasks import task_input_hash
from datetime import datetime, timedelta
from pyspark.sql.types import *
from pyspark.sql.functions import collect_list, col, concat_ws, substring

@task(name='Searching Table task')
def warehouse_search_task(artist, genre, album, track, track_feat):
    """Merge gold table and return searchs table"""
    hdfs_uri = "hdfs://namenode:8020/model/searchs.parquet"

    # Merge table
    searchs_table = (
        track
        .join(album, "album_id")
        .join(artist, "artist_id")
        .join(track_feat, "track_id")
        .join(genre, "artist_id")
    )
    
    # Concat Genre and groupby
    searchs_table = (
        searchs_table.withColumn("track_release_year", substring("release_date", 1, 4))
        .groupBy(
            "track_id", "track_name", "track_url", "track_popularity", "track_preview",
            "artist_name", "artist_popularity", "artist_image", "track_release_year",
            "album_name", "danceability", "energy", "key", "loudness", "mode",
            "speechiness", "acousticness", "instrumentalness", "liveness", "valence",
            "tempo", "duration_ms", "time_signature"
        )
        # .agg(collect_list('genre')).alias('genre_list')
        .agg(concat_ws(',', collect_list(col('genre'))).alias('genres'))
        .orderBy("track_popularity")
    )

    # Writing to HDFS
    print('Start writing warehouse_search.parquet')
    searchs_table.write.parquet(hdfs_uri, mode='overwrite')
    print(f'Warehouse: Successfully wrote {searchs_table.count()} into warehouse_searchs.parquet')

    return searchs_table

@task(name="Model pre processing task")
def warehouse_model_task(searchs_table):
    pass
