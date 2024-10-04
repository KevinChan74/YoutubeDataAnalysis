import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# import pyodbc
import sqlite3
from googleapiclient.discovery import build
# from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from datetime import datetime
from tkcalendar import Calendar
from Youtube_analysis import fetch_most_views_videos_stats
import tkinter as tk

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

youtube = build('youtube', 'v3', developerKey = api_key)

def test_fetch_data():
    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()
    publish_after_iso = datetime.strptime(publish_after, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    publish_before_iso = datetime.strptime(publish_before, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Fetching data from {publish_after_iso} to {publish_before_iso}")

    fetch_most_views_videos_stats(youtube, publish_after_iso, publish_before_iso)

def test_visualization():
    conn = sqlite3.connect('Youtube_database.db')
    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()

    # Convert to proper date format (YYYY-MM-DD)
    publish_after_formatted = datetime.strptime(publish_after, "%m/%d/%Y").strftime("%Y-%m-%d")
    publish_before_formatted = datetime.strptime(publish_before, "%m/%d/%Y").strftime("%Y-%m-%d")

    query = '''SELECT channel_title, SUM(view_count) AS total_view_count
               FROM Youtube_videos_info
               WHERE publish_time BETWEEN ? AND ?
               GROUP BY channel_id, channel_title
               ORDER BY total_view_count DESC'''
    
    # Pass the formatted dates as parameters
    df = pd.read_sql_query(query, conn, params=[publish_after_formatted, publish_before_formatted])
    conn.close()

    # Visualization
    fig, ax = plt.subplots()
    ax.bar(df["channel_title"], df['total_view_count'])
    plt.show()


root = tk.Tk()
root.title("Testing")
root.geometry("1000x1000")
calendar_start_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")
calendar_end_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")

test_fetch_data_button = tk.Button(root, text="Test Fetch Data", command=test_fetch_data)
test_visualization_button = tk.Button(root, text="Test Visualization", command=test_visualization)

calendar_start_date.pack()
calendar_end_date.pack()
test_fetch_data_button.pack()
test_visualization_button.pack()


root.mainloop()

