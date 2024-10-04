import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pyodbc
from googleapiclient.discovery import build
from matplotlib import font_manager
from datetime import datetime
from tkcalendar import Calendar
from Youtube_analysis import fetch_most_views_videos_stats
import tkinter as tk

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

youtube = build('youtube', 'v3', developerKey = api_key)

# Correctly configure the font settings
# Register each font path

font_paths = [
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans_KR/NotoSansKR-VariableFont_wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans_SC/NotoSansSC-VariableFont_wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Sans_Arabic/NotoSansArabic-VariableFont_wdth,wght.ttf',
    '/Users/hickeychan/Desktop/Noto_Sans,Noto_Sans_JP,Noto_Sans_KR,Noto_Sans_SC,Noto_Sans_TC,Noto_Sans_Arabic,Noto_Naskh_Arabic/Noto_Naskh_Arabic/NotoNaskhArabic-VariableFont_wght.ttf',
]

for path in font_paths:
    fm.fontManager.addfont(path)

# Refresh the font cache to include newly added fonts
fm._load_fontmanager(try_read_cache=False)  # Load the font manager without cache

# Set font properties globally for matplotlib
plt.rcParams["font.family"] = ["Noto Sans", "Noto Sans JP", "Noto Sans KR", "Noto Sans SC", "Noto Sans TC"]

'''Define functions in GUI'''

def fetch_data():
    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()
    publish_after_iso = datetime.strptime(publish_after, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    publish_before_iso = datetime.strptime(publish_before, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Fetching data from {publish_after_iso} to {publish_before_iso}")

    fetch_most_views_videos_stats(youtube, publish_after_iso, publish_before_iso)

def most_views_channels():
    server = os.getenv("server")
    database = os.getenv("database")
    username = os.getenv("username")
    password = os.getenv("password")
    driver = os.getenv("driver")

    connection_string = f'DRIVER={driver};SERVER=tcp:{server};PORT=1433;DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;'
    conn = pyodbc.connect(connection_string)

    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()

    query = '''SELECT channel_title, SUM(view_count) AS total_view_count, SUM(like_count) AS total_like_count, SUM(comment_count) AS total_comment_count
               FROM [dbo].[Search_list_table]
               WHERE data_collected_date = FORMAT(GETDATE(), 'yyyy-MM-dd') AND publish_time BETWEEN ? AND ?
               GROUP BY channel_id, channel_title
               ORDER BY total_view_count DESC'''
    df = pd.read_sql_query(query, conn, params = [publish_after, publish_before])
    conn.close()

    bar_width = 0.25
    bar_view_position = range(len(df["channel_title"]))
    bar_like_position = [x + bar_width for x in bar_view_position]
    bar_comment_position = [x + bar_width for x in bar_like_position]

    plt.figure(figsize = (12, 8))
    plt.bar(bar_view_position, df["total_view_count"], width = bar_width, color = "r", label = "Total Views")
    plt.bar(bar_like_position, df["total_like_count"], width = bar_width, color = "g", label = "Total Likes")
    plt.bar(bar_comment_position, df["total_comment_count"], width = bar_width, color = "b", label = "Total Comments")
    plt.title("Most view channels")
    plt.xlabel("Channels")
    plt.ylabel("Counts")
    plt.xticks([x + bar_width for x in range(len(df["channel_title"]))], df["channel_title"], rotation = 90)
    plt.legend()
    plt.tight_layout()
    plt.show()

def most_views_categories():
    server = os.getenv("server")
    database = os.getenv("database")
    username = os.getenv("username")
    password = os.getenv("password")
    driver = os.getenv("driver")

    connection_string = f'DRIVER={driver};SERVER=tcp:{server};PORT=1433;DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;'
    conn = pyodbc.connect(connection_string)

    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()

    query = '''SELECT video_category_name, SUM(view_count) AS total_view_count, COUNT(video_id) AS total_number_of_video, SUM(view_count)/COUNT(video_id) AS number_of_audience_per_video
               FROM [dbo].[Search_list_table]
               WHERE data_collected_date = FORMAT(GETDATE(), 'yyyy-MM-dd') AND publish_time BETWEEN ? AND ?
               GROUP BY video_category_name
               ORDER BY number_of_audience_per_video DESC'''
    
    df = pd.read_sql_query(query, conn, params = [publish_after, publish_before])
    conn.close()

    plt.figure(figsize = (12, 8))
    plt.bar(df["video_category_name"], df["number_of_audience_per_video"], color = ["red", "green", "blue", "orange", "purple", "black", "yellow"])
    plt.xlabel("Category")
    plt.ylabel("Audience per video")
    plt.title("Most views categories")
    plt.tight_layout()
    plt.show()

def most_views_publish_time():
    server = os.getenv("server")
    database = os.getenv("database")
    username = os.getenv("username")
    password = os.getenv("password")
    driver = os.getenv("driver")

    connection_string = f'DRIVER={driver};SERVER=tcp:{server};PORT=1433;DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;'
    conn = pyodbc.connect(connection_string)

    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()

    query = '''SELECT * FROM [dbo].[Search_list_table]
               WHERE data_collected_date = FORMAT(GETDATE(), 'yyyy-MM-dd') AND publish_time BETWEEN ? AND ?'''
    
    df = pd.read_sql_query(query, conn, params = [publish_after, publish_before])
    df["publish_time"] = pd.to_datetime(df["publish_time"], format = "%Y-%m-%dT%H:%M:%SZ")
    df["publish_hour"] = df["publish_time"].dt.hour
    hourly_counts = df.groupby(by="publish_hour")["view_count"].sum().reset_index(name = 'total_view_count')

    plt.figure(figsize = (12, 8))
    plt.bar(hourly_counts["publish_hour"], hourly_counts["total_view_count"])
    plt.xlabel("Hour")
    plt.ylabel("Total views")
    plt.xticks(list(range(24)))
    plt.title("Most views videos' publish hour")
    plt.tight_layout()
    plt.show()






# Create interface with tkinter
root = tk.Tk()
root.title("Youtube Data Analysis")
root.geometry("1000x1000")

Analysis_start_date_label = tk.Label(root, text = "Analysis start date: ")
Analysis_end_date_label = tk.Label(root, text = "Analysis end date: ")
calendar_start_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")
calendar_end_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")
fetch_button = tk.Button(root, text = "Fetch data", command=fetch_data)
most_views_channels_button = tk.Button(root, text = "Most views channels", command=most_views_channels)
most_views_categories_button = tk.Button(root, text = "Most views categories", command=most_views_categories)
most_views_publish_time_button = tk.Button(root, text = "Most views videos' publish time", command=most_views_publish_time)

# Pack elements in GUI
Analysis_start_date_label.pack()
calendar_start_date.pack()
Analysis_end_date_label.pack()
calendar_end_date.pack()
fetch_button.pack()
most_views_channels_button.pack()
most_views_categories_button.pack()
most_views_publish_time_button.pack()

root.mainloop()

