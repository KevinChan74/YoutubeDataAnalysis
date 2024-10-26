from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import sqlite3
import json
import os
from dotenv import load_dotenv
from transformers import pipeline
from time import sleep
load_dotenv()

api_key = os.getenv("api_key")

# Create a resource object to interact with google specific API
youtube = build('youtube', 'v3', developerKey = api_key)

'''Function to get most view videos in 2024
   three methods needed to acquire comprehensive videos' stats'''

max_results = 50
# Initializing empty lists to store retrieved data
all_video_basic_data_list = []
all_video_detail_data_list = []
all_video_category_id_name_data_list_of_dict = []
merged_data_list = []
all_video_data_list = []
all_videos_id_list = []
all_channels_id_list = []
all_channels_info_list = []
all_channels_subscriber_info_list = []
all_channels_uploads_playlist_id_list = []
all_playlistItems_video_id = []
all_playlistItems_video_detail_data_list = []

all_video_comment_info_list_of_dict = []
all_video_comment_textDisplay_list = []
all_video_comment_replies_textDisplay_list = []
all_video_comment_textDisplay_content_sentiment_list = []
all_video_comment_replies_textDisplay_content_sentiment_list = []

all_video_comment_id_list = []

all_reply_info_list_of_dict = []
all_reply_id_list = []
all_reply_textDisplay_list = []
all_comment_textDisplay_sentiment_list = []
all_reply_textDisplay_sentiment_list = []


'''Create database and tables using sqlite'''
def create_table_youtube_hottest_videos_info():
    conn = sqlite3.connect('Youtube_database.db')
    cursor = conn.cursor() 
    query_create_youtube_hottest_videos_info = '''CREATE TABLE IF NOT EXISTS Youtube_hottest_videos_info (
                                       video_id NVARCHAR(50) NOT NULL,
                                       video_title NVARCHAR(255) NOT NULL,
                                       video_localized_title NVARCAHR(255),
                                       video_localized_description NVARCHAR(4000),
                                       video_default_audio_language NVARCHAR(4000),
                                       video_duration NVARCHAR(500) NOT NULL,
                                       video_dimension NVARCHAR(300),
                                       video_definition NVARCHAR(300),
                                       video_caption NVARCHAR(20),
                                       video_licensed_content BIT,
                                       video_fco_rating NVARCHAR(20),
                                       publish_time DATETIME NOT NULL,
                                       publish_month_day NVARCHAR(50) NOT NULL,
                                       publish_month INT NOT NULL,
                                       publish_day INT NOT NULL,
                                       publish_after DATETIME NOT NULL,
                                       publish_before DATETIME NOT NULL,
                                       channel_id NVARCHAR(50) NOT NULL,
                                       channel_title NVARCHAR(50) NOT NULL,
                                       video_description NVARCHAR(4000),
                                       liveBroadcastContent NVARCHAR(50),
                                       video_viewCount INT,
                                       video_likeCount INT,
                                       video_commentCount INT,
                                       video_category_id NVARCHAR(255) NOT NULL,
                                       video_category_name NVARCHAR(255) NOT NULL,
                                       video_default_language NVARCHAR(20),
                                       video_made_For_Kids BIT)
                                       '''                   
    cursor.execute(query_create_youtube_hottest_videos_info)
    conn.commit()
    conn.close()

def fetch_most_views_videos_stats(youtube, publish_after, publish_before):
    global new_video_id_list
    new_video_id_list = []
    request_basic_data = youtube.search().list(
        part = "id, snippet",
        channelType="any",
        location="22.381581, 114.133992",  # centre location of hong kong
        locationRadius="37km", # it setted as the farthest distance from hong kong's centre, which would cover all videos uploaded in Hong Kong
        maxResults=max_results,
        order="viewCount",
        publishedAfter=f"{publish_after}",
        publishedBefore=f"{publish_before}",
        type="video"
    )
    response_basic_data = request_basic_data.execute()


    ''' fetch videos' basic_data '''
    for i in range(len(response_basic_data["items"])):
        publish_time_value = response_basic_data["items"][i]["snippet"]["publishTime"]
        publish_time = datetime.strptime(publish_time_value, "%Y-%m-%dT%H:%M:%SZ")
        publish_month_day = datetime.strftime(publish_time, "%m-%d")
        publish_month = int(publish_time.month)
        publish_day = int(publish_time.day)
        thumbnails_str = json.dumps(response_basic_data["items"][i]["snippet"]["thumbnails"])

        basic_data = dict(
                    video_id = response_basic_data["items"][i]["id"]["videoId"], 
                    video_title = response_basic_data["items"][i]["snippet"]["title"],
                    publish_date = response_basic_data["items"][i]["snippet"]["publishedAt"],
                    publish_time = response_basic_data["items"][i]["snippet"]["publishTime"],
                    publish_month_day = publish_month_day,
                    publish_month = publish_month,
                    publish_day = publish_day,
                    publish_after = publish_after,
                    publish_before = publish_before,
                    channel_id = response_basic_data["items"][i]["snippet"]["channelId"],
                    channel_title = response_basic_data["items"][i]["snippet"]["channelTitle"],
                    video_thumbnails = thumbnails_str,
                    liveBroadcastContent = response_basic_data["items"][i]["snippet"]["liveBroadcastContent"]
                    )
        all_video_basic_data_list.append(basic_data)
        all_videos_id_list.append(basic_data["video_id"])
        all_channels_id_list.append(basic_data["channel_id"])
        new_video_id_list.append(basic_data["video_id"])

    ''' fetch videos' channels_details'''
    fetched_channel_ids = set()
    for i in range(0, len(all_channels_id_list), 50):
        request_channels_details = youtube.channels().list(
            part = "id, snippet,contentDetails,statistics,topicDetails,status,brandingSettings,localizations",
            id = ','.join(all_channels_id_list[i:i+50]),
            maxResults=max_results
        )
        response_channels_details = request_channels_details.execute()

        for i in range(len(response_channels_details["items"])):
            channel_id = response_channels_details["items"][i]["id"],
            if channel_id in fetched_channel_ids:
                continue
        
            data_collected_date = datetime.now().strftime("%Y-%m-%d")
            channel_thumbnails_json_str = json.dumps(response_channels_details["items"][i]["snippet"].get("thumbnails", None))
            channel_localized_title_json_str = json.dumps(response_channels_details["items"][i]["snippet"]["localized"].get("title", None))
            channel_localized_description_json_str = json.dumps(response_channels_details["items"][i]["snippet"]["localized"].get("description", None))
            channel_topicIds_json_str = json.dumps(response_channels_details["items"][i].get("topicDetails", {}).get("topicIds", None))
            channel_topicCategories_json_str = json.dumps(response_channels_details["items"][i].get("topicDetails", {}).get("topicCategories", None))
            channels_info = dict(
                data_collected_date = data_collected_date,
                channel_id = response_channels_details["items"][i]["id"],
                channel_title = response_channels_details["items"][i]["brandingSettings"]["channel"]["title"],
                channel_description = response_channels_details["items"][i]["brandingSettings"]["channel"].get("description", None),
                channel_keywords = response_channels_details["items"][i]["brandingSettings"]["channel"].get("keywords", None),
                channel_trackingAnalyticAccountId = response_channels_details["items"][i]["brandingSettings"]["channel"].get("trackingAnalyticAccountId", None),
                channel_unsubscribedTrailer = response_channels_details["items"][i]["brandingSettings"]["channel"].get("unsubcribedTrailer", None),
                channel_defaultLanguage = response_channels_details["items"][i]["brandingSettings"]["channel"].get("defaultLanguage", None),
                channel_country = response_channels_details["items"][i]["brandingSettings"]["channel"].get("country", None),
                channel_customUrl = response_channels_details["items"][i]["snippet"].get("customUrl", None),
                channel_publishedAt = response_channels_details["items"][i]["snippet"].get("publishedAt", None),
                channel_thumbnails = channel_thumbnails_json_str,
                channel_viewCount = response_channels_details["items"][i]["statistics"]["viewCount"],
                channel_subscriberCount = response_channels_details["items"][i]["statistics"]["subscriberCount"],
                channel_hiddenSubscriberCount = response_channels_details["items"][i]["statistics"]["hiddenSubscriberCount"],
                channel_videoCount = response_channels_details["items"][i]["statistics"]["videoCount"],
                channel_topicIds = channel_topicIds_json_str,
                channel_topicCategories = channel_topicCategories_json_str,
                channel_madeForKids = response_channels_details["items"][i]["status"].get("madeForKids", None),
                channel_localized_title = channel_localized_title_json_str,
                channel_localizations_title = response_channels_details["items"][i].get("localizations", {}).get("title", None),
                channel_localizations_description = response_channels_details["items"][i].get("localizations", {}).get("description", None),
                channel_localized_description = channel_localized_description_json_str,
                channel_uploads_playlist_id = response_channels_details["items"][i]["contentDetails"]["relatedPlaylists"].get("uploads")
                )
            
            all_channels_uploads_playlist_id_list.append(channels_info['channel_uploads_playlist_id'])

            fetched_channel_ids.add(channel_id)
            all_channels_info_list.append(channels_info)
            all_channels_info_list_dict = {"items" : all_channels_info_list}
            # with open('all_channels_info.json', 'w') as f:
            #     json.dump(all_channels_info_list_dict, f, indent=4)


            '''Create table and fetch most views videos's channels' data into table'''
            create_table_youtube_channels_info()


            '''Insert data into Youtube_channels_info table'''
            conn = sqlite3.connect('Youtube_database.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Youtube_channels_info 
                        (data_collected_date, channel_id, channel_title, channel_description, channel_keywords, channel_trackingAnalyticAccountId, channel_unsubscribedTrailer, channel_defaultLanguage, channel_country, channel_customUrl, channel_publishedAt, channel_viewCount, channel_subscriberCount, channel_hiddenSubscriberCount, channel_videoCount, channel_status_madeForKids, channel_localized_title, channel_localizations_title, channel_localizations_description, channel_localized_description, channel_uploads_playlist_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                        (channels_info["data_collected_date"], channels_info["channel_id"], channels_info["channel_title"], channels_info["channel_description"], channels_info["channel_keywords"], channels_info["channel_trackingAnalyticAccountId"], channels_info["channel_unsubscribedTrailer"], channels_info["channel_defaultLanguage"], channels_info["channel_country"], channels_info["channel_customUrl"], channels_info["channel_publishedAt"], channels_info["channel_viewCount"], channels_info["channel_subscriberCount"], channels_info["channel_hiddenSubscriberCount"], channels_info["channel_videoCount"], channels_info["channel_madeForKids"], channels_info["channel_localized_title"], channels_info["channel_localizations_title"], channels_info["channel_localizations_description"], channels_info["channel_localized_description"], channels_info["channel_uploads_playlist_id"]))
            conn.commit() 
            conn.close()

    ''' fetch videos' detail_data '''         
    for i in range(0, len(new_video_id_list), 50):
        request_video_details = youtube.videos().list(
            part = "snippet, contentDetails, status, statistics",
            id = ','.join(new_video_id_list[i:i+50]),
            maxResults=max_results
        )

        response_video_details = request_video_details.execute()
        

        for i in range(len(response_video_details["items"])):
            tags_str = json.dumps(response_video_details["items"][i]["snippet"].get("tags", None))
            detail_data = dict(video_description = response_video_details["items"][i]["snippet"].get("description", None),
                                 video_tags = tags_str,
                                 video_category_id = response_video_details["items"][i]["snippet"]["categoryId"],
                                 video_default_language = response_video_details["items"][i]["snippet"].get("defaultLanguage", None),
                                 video_localized_title = response_video_details["items"][i]["snippet"]["localized"].get("title", None),
                                 video_localized_description = response_video_details["items"][i]["snippet"]["localized"].get("description", None),
                                 video_default_audio_language = response_video_details["items"][i]["snippet"].get("defaultAudioLanguage", None),
                                 video_duration = response_video_details["items"][i]["contentDetails"].get("duration", None),
                                 video_dimension = response_video_details["items"][i]["contentDetails"].get("dimension", None),
                                 video_definition = response_video_details["items"][i]["contentDetails"].get("definition", None),
                                 video_caption = bool(response_video_details["items"][i]["contentDetails"].get("caption")),
                                 video_licensed_content = response_video_details["items"][i]["contentDetails"].get("licensedContent", None),
                                 video_region_restriction_allowed = response_video_details["items"][i]["contentDetails"].get("regionRestriction", {}).get("allowed", None),
                                 video_region_restriction_blocked = response_video_details["items"][i]["contentDetails"].get("regionRestriction", {}).get("blocked", None),
                                 video_fco_rating = response_video_details["items"][i]["contentDetails"]["contentRating"].get("fcoRating", None),
                                 video_viewCount = response_video_details["items"][i]["statistics"]["viewCount"],
                                 video_likeCount = response_video_details["items"][i]["statistics"].get("likeCount", None),
                                 video_commentCount = response_video_details["items"][i]["statistics"].get("commentCount", None),
                                 video_made_For_Kids = response_video_details["items"][i]["status"].get("madeForKids", None)
                                 )
            all_video_detail_data_list.append(detail_data)

    '''fetch videos' category data'''
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
    # Transform list of dictionaries to one dictionary
    all_video_category_id_name_data_dict = {}
    for category_id_name_dict in all_video_category_id_name_data_list_of_dict: 
        video_category_id = category_id_name_dict["video_category_id"]
        video_category_name = category_id_name_dict["video_category_name"]
        all_video_category_id_name_data_dict[video_category_id] = video_category_name

    print(f"There are {len(all_video_basic_data_list)} video basic data")
    print(f"There are {len(all_video_detail_data_list)} video detail data")
    print(f"There are {len(all_video_category_id_name_data_list_of_dict)} video category id : video category name elements(dictionary) in this list")
    

    if len(all_video_basic_data_list) != len(all_video_detail_data_list):
        raise ValueError("Lists must be the same length to merge completely")
    

    for basic_data, detail_data in zip(all_video_basic_data_list, all_video_detail_data_list):
        video_category_id = str(detail_data["video_category_id"])
        video_category_name = all_video_category_id_name_data_dict.get(video_category_id, "Unknown")
        merged_data = {**basic_data, **detail_data, "video_category_name" : video_category_name} 
        merged_data_list.append(merged_data)

    '''Create table and fetch most views videos's data into table'''
    create_table_youtube_hottest_videos_info()

    for merged_data_detail in merged_data_list:
        most_views_data = {
            "video_id" : merged_data_detail["video_id"],
            "video_title" : merged_data_detail["video_title"],
            "video_localized_title" : merged_data_detail["video_localized_title"],
            "video_localized_description" : merged_data_detail["video_localized_description"],
            "video_default_audio_language" : merged_data_detail["video_default_audio_language"],
            "video_duration" : merged_data_detail["video_duration"],
            "video_dimension" : merged_data_detail["video_dimension"],
            "video_definition" : merged_data_detail["video_definition"],
            "video_caption" : merged_data_detail["video_caption"],
            "video_licensed_content" : merged_data_detail["video_licensed_content"],
            "video_fco_rating" : merged_data_detail["video_fco_rating"],
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
            "video_viewCount" : merged_data_detail["video_viewCount"],
            "video_likeCount" : merged_data_detail["video_likeCount"],
            "video_commentCount" : merged_data_detail["video_commentCount"],
            "video_category_id" : str(merged_data_detail["video_category_id"]),
            "video_category_name" : merged_data_detail["video_category_name"],
            "video_default_language" : merged_data_detail["video_default_language"],
            "video_tags" : merged_data_detail["video_tags"],
            "video_made_For_Kids" : 1 if merged_data_detail["video_made_For_Kids"] else 0
        }

        all_video_data_list.append(most_views_data)
        all_video_data_dict = {"items" : all_video_data_list}
        # with open('all_videos_info.json', 'w') as f:
        #     json.dump(all_video_data_dict, f, indent=4)

        '''Insert data into Youtube_hottest_videos_info'''
        conn = sqlite3.connect('Youtube_database.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Youtube_hottest_videos_info 
                    (video_id, video_title, video_localized_title, video_localized_description, video_default_audio_language, video_duration, video_dimension, video_definition, video_caption, video_licensed_content, video_fco_rating, publish_time, publish_month_day, publish_month, publish_day, publish_after, publish_before, channel_id, channel_title, video_description, liveBroadcastContent, video_viewCount, video_likeCount, video_commentCount, video_category_id, video_category_name, video_default_language, video_made_For_Kids) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                    (most_views_data["video_id"], most_views_data["video_title"], most_views_data["video_localized_title"], most_views_data["video_localized_description"], most_views_data["video_default_audio_language"], most_views_data["video_duration"], most_views_data["video_dimension"], most_views_data["video_definition"], most_views_data["video_caption"], most_views_data["video_licensed_content"], most_views_data["video_fco_rating"], most_views_data["publish_time"], most_views_data["publish_month_day"], most_views_data["publish_month"], most_views_data["publish_day"], most_views_data["publish_after"], most_views_data["publish_before"], most_views_data["channel_id"], most_views_data["channel_title"], most_views_data["video_description"], most_views_data["liveBroadcastContent"], most_views_data["video_viewCount"], most_views_data["video_likeCount"], most_views_data["video_commentCount"], most_views_data["video_category_id"], most_views_data["video_category_name"], most_views_data["video_default_language"], most_views_data["video_made_For_Kids"]))
        conn.commit() 
        conn.close()
    return merged_data_list

def create_table_youtube_channels_info():
    conn = sqlite3.connect("Youtube_database.db")
    cursor = conn.cursor()
    query_create_youtube_channels_info = '''CREATE TABLE IF NOT EXISTS Youtube_channels_info(
                                            data_collected_date NVARCHAR(50),
                                            channel_id NVARCHAR(50),
                                            channel_title NVARHCAR(50),
                                            channel_description NVARCHAR(4000),
                                            channel_keywords NVARCHAR(4000),
                                            channel_trackingAnalyticAccountId NVARCHAR(50),
                                            channel_unsubscribedTrailer NVARCHAR(300),
                                            channel_customUrl NVARCHAR(300),
                                            channel_publishedAt DATETIME,
                                            channel_defaultLanguage NVARCHAR(50),
                                            channel_country NVARCHAR(50),
                                            channel_viewCount INT,
                                            channel_subscriberCount INT,
                                            channel_hiddenSubscriberCount BIT,
                                            channel_videoCount INT, 
                                            channel_status_madeForKids BIT,
                                            channel_localized_title NVARCHAR(300),
                                            channel_localized_description NVARCHAR(4000),
                                            channel_localizations_title NVARCHAR(300),
                                            channel_localizations_description NVARCHAR(300),
                                            channel_uploads_playlist_id NVARCHAR(300))
                                        '''
    cursor.execute(query_create_youtube_channels_info)
    conn.commit()
    conn.close()

def create_table_youtube_channels_video_comments_with_sentiment():
    conn = sqlite3.connect('Youtube_database.db')
    cursor = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Youtube_channels_comments_with_sentiment
               (data_collected_date DATATIME NOT NULL,
                channel_id NVARCHAR(50),
                video_id NVARCHAR(50),
                video_comment_id NVARCHAR(4000) NOT NULL,
                video_comment_textDisplay NVARCHAR(4000),
                video_comment_textOriginal NVARCHAR(4000),
                video_comment_authorDisplayName NVARCHAR(400),
                video_comment_canRate BIT,
                video_comment_likeCount INT,
                video_comment_publishedAt_datetime TIMESTAMP,
                video_comment_canReply BIT,
                video_comment_totalReplyCount INT,
                video_comment_isPublic BIT,
                video_comment_textDisplay_sentiment NVARCHAR(9)
               )'''
    cursor.execute(query)
    conn.commit()
    conn.close()

def create_table_youtube_channels_replies_with_sentiment():
    conn = sqlite3.connect('Youtube_database.db')
    cursor = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS Youtube_channels_replies_with_sentiment
               (data_collected_date DATETIME NOT NULL, 
               channel_id NVARCHAR(50),
               reply_id NVARCHAR(4000),
               reply_authorDisplayName NVARCHAR(400),
               reply_textDisplay NVARCHAR(4000),
               reply_textOriginal NVARCHAR(4000),
               reply_parentId NVARCHAR(4000),
               reply_canRate BIT,
               reply_likeCount INT,
               reply_publishedAt_datetime TIMESTAMP NOT NULL,
               reply_textDisplay_sentiment NVARCHAR(9)
               )'''
    cursor.execute(query)
    conn.commit()
    conn.close()

def fetch_youtube_channels_video_comments_and_replies_with_sentiment(status_label):
    try:
        status_label.config(text = f"Top {len(new_video_id_list)} videos' data will be fetched")
        status_label.update()
        sleep(3)
        for index, video_id_element in enumerate(new_video_id_list):
            request_youtube_channels_video_commentThreads = youtube.commentThreads().list(
                part="snippet, replies",
                videoId=video_id_element,
                maxResults=50
            )
            response_youtube_channels_video_commentThreads = request_youtube_channels_video_commentThreads.execute()
            status_label.config(text = f"Fetching video data {index+1}/{len(new_video_id_list)} ...")
            status_label.update()

            for i in range(len(response_youtube_channels_video_commentThreads["items"])):
                video_top_comment_snippet = response_youtube_channels_video_commentThreads["items"][i]["snippet"]["topLevelComment"]["snippet"]
                video_comment_publishedAt = video_top_comment_snippet.get("publishedAt", None) # Turn to datetime object before fetching into table
                video_comment_id = response_youtube_channels_video_commentThreads["items"][i].get("id")

                comment_info_dict = dict(
                                        data_collected_date = datetime.now(),
                                        channel_id = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("channelId"),
                                        video_id = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("videoId"),
                                        video_comment_canReply = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("canReply"),
                                        video_comment_totalReplyCount = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("totalReplyCount"),
                                        video_comment_isPublic = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("isPublic"),

                                        video_comment_id = response_youtube_channels_video_commentThreads["items"][i].get("id"),
                                        video_comment_textDisplay = video_top_comment_snippet.get("textDisplay"),
                                        video_comment_textOriginal = video_top_comment_snippet.get("textOriginal"),
                                        video_comment_authorDisplayName = video_top_comment_snippet.get("authorDisplayName"),
                                        video_comment_canRate = video_top_comment_snippet.get("canRate"),
                                        video_comment_likeCount = video_top_comment_snippet.get("likeCount"),
                                        video_comment_publishedAt_datetime = datetime.strptime(video_comment_publishedAt, "%Y-%m-%dT%H:%M:%SZ") if video_comment_publishedAt else None, # will be None if there is no comment on the comment
                                        )
                all_video_comment_info_list_of_dict.append(comment_info_dict)
                all_video_comment_id_list.append(comment_info_dict["video_comment_id"])
                all_video_comment_textDisplay_list.append(comment_info_dict["video_comment_textDisplay"])

                totalReplyCount = response_youtube_channels_video_commentThreads["items"][i]["snippet"].get("totalReplyCount", 0)
                if totalReplyCount > 0:

                    request_youtube_channels_replies = youtube.comments().list(
                        part="id,snippet",
                        parentId=video_comment_id,
                        maxResults=50
                    )
                    response_youtube_channels_replies = request_youtube_channels_replies.execute()

                    for i in range(len(response_youtube_channels_replies["items"])):
                        reply_snippet = response_youtube_channels_replies["items"][i]["snippet"]
                        reply_publishedAt = reply_snippet.get("publishedAt") # Turn to datetime object before fetching into table

                        reply_info_dict = dict(
                            data_collected_date = datetime.now(),
                            channel_id = reply_snippet["channelId"],
                            reply_id = response_youtube_channels_replies["items"][i]["id"],
                            reply_authorDisplayName = reply_snippet["authorDisplayName"],
                            reply_textDisplay = reply_snippet["textDisplay"],
                            reply_textOriginal = reply_snippet["textOriginal"],
                            reply_parentId = reply_snippet["parentId"],
                            reply_canRate = reply_snippet["canRate"],
                            reply_likeCount = reply_snippet["likeCount"],
                            reply_publishedAt_datetime = datetime.strptime(reply_publishedAt, "%Y-%m-%dT%H:%M:%SZ") if reply_publishedAt else None
                        )
                        all_reply_info_list_of_dict.append(reply_info_dict)
                        all_reply_id_list.append(reply_info_dict["reply_id"])
                        all_reply_textDisplay_list.append(reply_info_dict["reply_textDisplay"])

                        print(reply_info_dict["reply_textDisplay"])
                        reply_textDisplay_sentiment = analyze_sentiment(reply_info_dict["reply_textDisplay"])
                        all_reply_textDisplay_sentiment_list.append(reply_textDisplay_sentiment)
                    
                        # For each reply, do sentiment analysis & add to respective dictionary
                        for reply_info_dict, reply_textDisplay_sentiment in zip(all_reply_info_list_of_dict, all_reply_textDisplay_sentiment_list):
                            reply_info_dict["reply_textDisplay_sentiment"] = reply_textDisplay_sentiment

                        # Create Youtube_channels_replies_with_sentiment table
                        create_table_youtube_channels_replies_with_sentiment()

                        for reply_info_detail in all_reply_info_list_of_dict:
                            reply_info_detail_dict = {
                                "data_collected_date" : reply_info_detail["data_collected_date"],
                                "channel_id" : reply_info_detail["channel_id"],
                                "reply_id" : reply_info_detail["reply_id"],
                                "reply_authorDisplayName" : reply_info_detail["reply_authorDisplayName"],
                                "reply_textDisplay" : reply_info_detail["reply_textDisplay"],
                                "reply_textOriginal" : reply_info_detail["reply_textOriginal"],
                                "reply_parentId" : reply_info_detail["reply_parentId"],
                                "reply_canRate" : reply_info_detail["reply_canRate"],
                                "reply_likeCount" : reply_info_detail["reply_likeCount"],
                                "reply_publishedAt_datetime" : reply_info_detail["reply_publishedAt_datetime"],
                                "reply_textDisplay_sentiment" : reply_info_detail["reply_textDisplay_sentiment"]
                                }

                        # Insert values into Youtube_channels_replies_with_sentiment table
                        conn = sqlite3.connect("Youtube_database.db")
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO Youtube_channels_replies_with_sentiment
                                        (data_collected_date, channel_id, reply_id, reply_authorDisplayName, reply_textDisplay, reply_textOriginal, reply_parentId, reply_canRate, reply_likeCount, reply_publishedAt_datetime, reply_textDisplay_sentiment)
                                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                        (reply_info_detail_dict["data_collected_date"], reply_info_detail_dict["channel_id"], reply_info_detail_dict["reply_id"], reply_info_detail_dict["reply_authorDisplayName"], reply_info_detail_dict["reply_textDisplay"], reply_info_detail_dict["reply_textOriginal"], reply_info_detail_dict["reply_parentId"], reply_info_detail_dict["reply_canRate"], reply_info_detail_dict["reply_likeCount"], reply_info_detail_dict["reply_publishedAt_datetime"], reply_info_detail_dict["reply_textDisplay_sentiment"]))
                        conn.commit()
                        conn.close()

                # For each comment, do sentiment analysis & add to respective dictionary
                print(comment_info_dict["video_comment_textDisplay"])
                comment_textDisplay_sentiment = analyze_sentiment(comment_info_dict["video_comment_textDisplay"])
                all_comment_textDisplay_sentiment_list.append(comment_textDisplay_sentiment)
        
                for comment_info_dict, comment_textDisplay_sentiment in zip(all_video_comment_info_list_of_dict, all_comment_textDisplay_sentiment_list):
                    comment_info_dict["video_comment_textDisplay_sentiment"] = comment_textDisplay_sentiment
        
                create_table_youtube_channels_video_comments_with_sentiment()

                for comment_info_detail in all_video_comment_info_list_of_dict:
                    comment_info_detail_dict = {
                        "data_collected_date" : comment_info_detail["data_collected_date"],
                        "channel_id" : comment_info_detail["channel_id"],
                        "video_id" : comment_info_detail["video_id"],
                        "video_comment_id" : comment_info_detail["video_comment_id"],
                        "video_comment_textDisplay" : comment_info_detail["video_comment_textDisplay"],
                        "video_comment_textOriginal" : comment_info_detail["video_comment_textOriginal"],
                        "video_comment_authorDisplayName" : comment_info_detail["video_comment_authorDisplayName"],
                        "video_comment_canRate" : comment_info_detail["video_comment_canRate"],
                        "video_comment_likeCount" : comment_info_detail["video_comment_likeCount"],
                        "video_comment_publishedAt_datetime" : comment_info_detail["video_comment_publishedAt_datetime"],
                        "video_comment_canReply" : comment_info_detail["video_comment_canReply"],
                        "video_comment_totalReplyCount" : comment_info_detail["video_comment_totalReplyCount"],
                        "video_comment_isPublic" : comment_info_detail["video_comment_isPublic"],
                        "video_comment_textDisplay_sentiment" : comment_info_detail["video_comment_textDisplay_sentiment"]
                    }

                conn = sqlite3.connect("Youtube_database.db")
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Youtube_channels_comments_with_sentiment
                                    (data_collected_date, channel_id, video_id, video_comment_id, video_comment_textDisplay, video_comment_textOriginal, video_comment_authorDisplayName, video_comment_canRate, video_comment_likeCount, video_comment_publishedAt_datetime, video_comment_canReply, video_comment_totalReplyCount, video_comment_isPublic, video_comment_textDisplay_sentiment)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (comment_info_detail_dict["data_collected_date"], comment_info_detail_dict["channel_id"], comment_info_detail_dict["video_id"], comment_info_detail_dict["video_comment_id"], comment_info_detail_dict["video_comment_textDisplay"], comment_info_detail_dict["video_comment_textOriginal"], comment_info_detail_dict["video_comment_authorDisplayName"], comment_info_detail_dict["video_comment_canRate"], comment_info_detail_dict["video_comment_likeCount"], comment_info_detail_dict["video_comment_publishedAt_datetime"], comment_info_detail_dict["video_comment_canReply"], comment_info_detail_dict["video_comment_totalReplyCount"], comment_info_detail_dict["video_comment_isPublic"], comment_info_detail_dict["video_comment_textDisplay_sentiment"]))
                conn.commit()
                conn.close()
            status_label.config(text = f"Video data {index+1}/{len(new_video_id_list)} successfully fetched!")
            status_label.update()
    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in e.content.decode():
            print(f"Comments are disabled for video {video_id_element}. Skipping comment fetch.")
        else:
            print(f"HttpError: Failed to fetch comments for video {video_id_element}: {str(e)}")

    print("---------------------------Fetch Done---------------------------")





    """
    Analyzes the sentiment of a given comment using a pre-trained BERT model.

    This function takes a customer comment as input, processes it using the specified BERT model,
    and returns the sentiment label ('positive' or 'negative').

    Args:
        comment (str): The customer's comment.

    Returns:
        str: The sentiment label ('positive' or 'negative').
    """

def analyze_sentiment(comment: str) -> str:
    
    if comment is None:
        print("There is no comment here")
        return
    elif len(comment) > 512:
        each_comment_content = comment[:511]
    else:
        each_comment_content = comment[:]

    sentiment_analyzer = pipeline(model='distilbert/distilbert-base-uncased-finetuned-sst-2-english', device=0)
    result = sentiment_analyzer(each_comment_content)[0]
    return result['label']