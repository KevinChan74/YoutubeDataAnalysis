from googleapiclient.discovery import build
from datetime import datetime
# import pyodbc
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

'''The following documentations are applicable when using Azure SQL database'''
# server = os.getenv("server")
# database = os.getenv("database")
# username = os.getenv("username")
# password = os.getenv("password")
# driver = os.getenv("driver")

# connection_string = f'DRIVER={driver};SERVER=tcp:{server};PORT=1433;DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;'

# Function of creating database and table using Azure SQL database

# def create_table():
#     conn = pyodbc.connect(connection_string)
#     cursor = conn.cursor()
#     cursor.execute('''IF OBJECT_ID('Search_list_table', 'U') IS NULL
#                    BEGIN 
#                    CREATE TABLE Search_list_table(
#                 data_collected_date NVARCHAR(20) NOT NULL,
#                 video_id NVARCHAR(50) NOT NULL,
#                 video_title NVARCHAR(255) NOT NULL,
#                 publish_time DATETIME NOT NULL,
#                 publish_month_day NVARCHAR(50) NOT NULL,
#                 publish_month INT NOT NULL,
#                 publish_day INT NOT NULL,
#                 publish_after DATETIME NOT NULL,
#                 publish_before DATETIME NOT NULL,
#                 channel_id NVARCHAR(50) NOT NULL,
#                 channel_title NVARCHAR(50) NOT NULL,
#                 video_description NVARCHAR(4000) NOT NULL,
#                 video_thumbnails NVARCHAR(4000) NOT NULL,
#                 liveBroadcastContent NVARCHAR(50),
#                 view_count INT,
#                 like_count INT,
#                 comment_count INT,
#                 video_length NVARCHAR(255) NOT NULL,
#                 video_category_id NVARCHAR(255) NOT NULL,
#                 video_category_name NVARCHAR(255) NOT NULL,
#                 video_default_language NVARCHAR(20),
#                 video_tags NVARCHAR(4000),
#                 video_made_For_Kids BIT
#                 )
#                 END''')
#     conn.commit()
#     conn.close()


# Create database and table using sqlite
def create_table():
    conn = sqlite3.connect('Youtube_database.db')
    cursor = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Youtube_videos_info (
                 data_collected_date NVARCHAR(20) NOT NULL,
                 video_id NVARCHAR(50) NOT NULL,
                 video_title NVARCHAR(255) NOT NULL,
                 publish_time DATETIME NOT NULL,
                 publish_month_day NVARCHAR(50) NOT NULL,
                 publish_month INT NOT NULL,
                 publish_day INT NOT NULL,
                 publish_after DATETIME NOT NULL,
                 publish_before DATETIME NOT NULL,
                 channel_id NVARCHAR(50) NOT NULL,
                 channel_title NVARCHAR(50) NOT NULL,
                 video_description NVARCHAR(4000) NOT NULL,
                 video_thumbnails NVARCHAR(4000) NOT NULL,
                 liveBroadcastContent NVARCHAR(50),
                 view_count INT,
                 like_count INT,
                 comment_count INT,
                 video_length NVARCHAR(255) NOT NULL,
                 video_category_id NVARCHAR(255) NOT NULL,
                 video_category_name NVARCHAR(255) NOT NULL,
                 video_default_language NVARCHAR(20),
                 video_tags NVARCHAR(4000),
                 video_made_For_Kids BIT)
            '''
    cursor.execute(query)
    conn.commit()
    conn.close()



# Create a resource object to interact with google specific API
youtube = build('youtube', 'v3', developerKey = api_key)

'''Function to get most view videos in 2024
   three methods needed to acquire comprehensive videos' stats'''

# Initializing empty lists to store retrieved data
all_video_basic_data = []
all_video_detail_data = []
all_video_category_id_name_data_list_of_dict = []

def fetch_most_views_videos_stats(youtube, publish_after, publish_before):
    # print("Fetching data...")
    request = youtube.search().list(
        part = "id, snippet",
        channelType="any",
        location="22.381581, 114.133992",  # centre location of hong kong
        locationRadius="37km", # it setted as the farthest distance from hong kong's centre, which would cover all videos uploaded in Hong Kong
        maxResults=50,
        order="viewCount",
        publishedAfter=f"{publish_after}",
        publishedBefore=f"{publish_before}",
        type="video"
    )
    response = request.execute()


    ''' fetch video's basic_data '''
    all_video_id = []
    for i in range(len(response["items"])):
        publish_time_value = response["items"][i]["snippet"]["publishTime"]
        publish_time = datetime.strptime(publish_time_value, "%Y-%m-%dT%H:%M:%SZ")
        publish_month_day = datetime.strftime(publish_time, "%m-%d")
        publish_month = int(publish_time.month)
        publish_day = int(publish_time.day)
        data_collected_time = datetime.now()
        data_collected_date = data_collected_time.strftime("%Y-%m-%d")
        thumbnails_str = json.dumps(response["items"][i]["snippet"]["thumbnails"])

        basic_data = dict(data_collected_date = data_collected_date,
                    video_id = response["items"][i]["id"]["videoId"],
                    video_title = response["items"][i]["snippet"]["title"],
                    publish_date = response["items"][i]["snippet"]["publishedAt"],
                    publish_time = response["items"][i]["snippet"]["publishTime"],
                    publish_month_day = publish_month_day,
                    publish_month = publish_month,
                    publish_day = publish_day,
                    publish_after = publish_after,
                    publish_before = publish_before,
                    channel_id = response["items"][i]["snippet"]["channelId"],
                    channel_title = response["items"][i]["snippet"]["channelTitle"],
                    video_description = response["items"][i]["snippet"]["description"],
                    video_thumbnails = thumbnails_str,
                    liveBroadcastContent = response["items"][i]["snippet"]["liveBroadcastContent"]
                    )
        all_video_basic_data.append(basic_data)
        all_video_id.append(basic_data["video_id"])

    str_all_video_id = ','.join(all_video_id)


    ''' fetch video's detail_data '''
    request_video_details = youtube.videos().list(
        part = "snippet, contentDetails, status, statistics",
        id = f"{str_all_video_id}"
    )

    response_video_details = request_video_details.execute()
    # save_response_to_file(response_video_details)
    
    for i in range(len(response_video_details["items"])):
        tags_str = json.dumps(response_video_details["items"][i]["snippet"].get("tags", None))
        detail_data = dict(view_count = response_video_details["items"][i]["statistics"]["viewCount"],
                             like_count = response_video_details["items"][i]["statistics"]["likeCount"],
                             comment_count = response_video_details["items"][i]["statistics"].get("commentCount", None),
                             video_length = response_video_details["items"][i]["contentDetails"]["duration"],
                             video_category_id = response_video_details["items"][i]["snippet"]["categoryId"],
                             video_default_language = response_video_details["items"][i]["snippet"].get("defaultLanguage", None),
                             video_tags = tags_str,
                             video_made_For_Kids = response_video_details["items"][i]["status"].get("madeForKids", None)
                             )
        all_video_detail_data.append(detail_data)

    '''fetch video's category data'''
    request_video_category = youtube.videoCategories().list(
        part = "snippet",
        regionCode = "HK"
    )

    response_video_category = request_video_category.execute()

    for i in range(len(response_video_category["items"])):
        category_detail_dict = dict(video_category_id = response_video_category["items"][i]["id"],
                               video_category_name = response_video_category["items"][i]["snippet"]["title"]
                            )
        all_video_category_id_name_data_list_of_dict.append(category_detail_dict)


    '''Merge video_data together'''
    all_video_category_id_name_data_dict = {}
    for category_id_name_dict in all_video_category_id_name_data_list_of_dict:
        video_category_id = category_id_name_dict["video_category_id"]
        video_category_name = category_id_name_dict["video_category_name"]
        all_video_category_id_name_data_dict[video_category_id] = video_category_name

    print(f"There are {len(all_video_basic_data)} video basic data")
    print(f"There are {len(all_video_detail_data)} video detail data")
    print(f"There are {len(all_video_category_id_name_data_list_of_dict)} video category id : video category name elements(dictionary) in this list")

    if len(all_video_basic_data) != len(all_video_detail_data):
        raise ValueError("Lists must be the same length to merge completely")
    
    merged_data_list = []
    for basic_data, detail_data in zip(all_video_basic_data, all_video_detail_data):
        video_category_id = str(detail_data["video_category_id"])
        video_category_name = all_video_category_id_name_data_dict.get(video_category_id, "Unknown")
        merged_data = {**basic_data, **detail_data, "video_category_name" : video_category_name} 
        merged_data_list.append(merged_data)

    '''Create table and fetch most views videos's data into table'''
    create_table()

    for merged_data_detail in merged_data_list:
        most_views_data = {
            "data_collected_date" : merged_data_detail["data_collected_date"],
            "video_id" : merged_data_detail["video_id"],
            "video_title" : merged_data_detail["video_title"],
            "publish_time" : merged_data_detail["publish_time"],
            "publish_month_day" : merged_data_detail["publish_month_day"],
            "publish_month" : merged_data_detail["publish_month"],
            "publish_day" : merged_data_detail["publish_day"],
            "publish_after" : merged_data_detail["publish_after"],
            "publish_before" : merged_data_detail["publish_before"],
            "channel_id" : merged_data_detail["channel_id"],
            "channel_title" : merged_data_detail["channel_title"],
            "video_description" : merged_data_detail["video_description"],
            "video_thumbnails" : merged_data_detail["video_thumbnails"],
            "liveBroadcastContent" : merged_data_detail["liveBroadcastContent"],
            "view_count" : merged_data_detail["view_count"],
            "like_count" : merged_data_detail["like_count"],
            "comment_count" : merged_data_detail["comment_count"],
            "video_length" : merged_data_detail["video_length"],
            "video_category_id" : str(merged_data_detail["video_category_id"]),
            "video_category_name" : merged_data_detail["video_category_name"],
            "video_default_language" : merged_data_detail["video_default_language"],
            "video_tags" : merged_data_detail["video_tags"],
            "video_made_For_Kids" : 1 if merged_data_detail["video_made_For_Kids"] else 0
        }

        conn = sqlite3.connect('Youtube_database.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Youtube_videos_info 
                    (data_collected_date, video_id, video_title, publish_time, publish_month_day, publish_month, publish_day, publish_after, publish_before, channel_id, channel_title, video_description, video_thumbnails, liveBroadcastContent, view_count, like_count, comment_count, video_length, video_category_id, video_category_name, video_default_language, video_tags, video_made_For_Kids) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                    (most_views_data["data_collected_date"], most_views_data["video_id"], most_views_data["video_title"], most_views_data["publish_time"], most_views_data["publish_month_day"], most_views_data["publish_month"], most_views_data["publish_day"], most_views_data["publish_after"], most_views_data["publish_before"], most_views_data["channel_id"], most_views_data["channel_title"], most_views_data["video_description"], most_views_data["video_thumbnails"], most_views_data["liveBroadcastContent"], most_views_data["view_count"], most_views_data["like_count"], most_views_data["comment_count"], most_views_data["video_length"], most_views_data["video_category_id"], most_views_data["video_category_name"], most_views_data["video_default_language"], most_views_data["video_tags"], most_views_data["video_made_For_Kids"]))
        conn.commit()
        conn.close()

    return merged_data_list

# def run_scheduler():
#     print("Scheduler started")
#     interval = 1
#     schedule.every().day.at("21:25").do(fetch_most_views_videos_stats_2024, youtube)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# if __name__ == "__main__":
#     run_scheduler()



# most_views_videos_stats_2024 = fetch_most_views_videos_stats_2024(youtube, publish_after, publish_before)
# print(most_views_videos_stats_2024)
# print(all_video_basic_data)


