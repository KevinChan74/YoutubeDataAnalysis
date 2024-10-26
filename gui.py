import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import sqlite3
from googleapiclient.discovery import build
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkcalendar import Calendar
from Fetch_all_data import create_table_youtube_hottest_videos_info, create_table_youtube_channels_info, fetch_most_views_videos_stats, fetch_youtube_channels_video_comments_and_replies_with_sentiment
import tkinter as tk
from tkinter import ttk, messagebox

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

def check_existing_videos_records(publish_after, publish_before):
    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()
    publish_after_iso = datetime.strptime(publish_after, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    publish_before_iso = datetime.strptime(publish_before, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = sqlite3.connect('Youtube_database.db')
    cursor = conn.cursor()
    create_table_youtube_hottest_videos_info()
    query = '''SELECT COUNT(*) FROM Youtube_hottest_videos_info
               WHERE publish_after = ? AND publish_before = ?
            '''
    cursor.execute(query, (publish_after_iso, publish_before_iso))
    result = cursor.fetchone()
    count = result[0]
    conn.close()
    return count > 0

def check_existing_channels():
    data_collected_date = datetime.now()
    str_data_collected_date = datetime.strftime(data_collected_date, "%Y-%m-%dT%H:%M:%SZ")
    conn = sqlite3.connect("Youtube_database.db")
    cursor = conn.cursor()
    create_table_youtube_channels_info()
    query = '''SELECT COUNT(*) FROM Youtube_channels_info
               WHERE data_collected_date = ?
            '''
    cursor.execute(query, (str_data_collected_date,))
    result = cursor.fetchone()
    count = result[0]
    conn.close()
    return count > 0

def fetch_videos_data():
    publish_after = calendar_start_date.get_date()
    publish_before = calendar_end_date.get_date()
    publish_after_iso = datetime.strptime(publish_after, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    publish_before_iso = datetime.strptime(publish_before, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    if check_existing_videos_records(publish_after_iso, publish_before_iso):
        print(f"Youtube videos' data from {publish_after_iso} to {publish_before_iso} exists already")
    else:
        print(f"Fetching data from {publish_after_iso} to {publish_before_iso}")
        status_label.config(text = f"Fetching data from {publish_after_iso} to {publish_before_iso}")
        fetch_most_views_videos_stats(youtube, publish_after_iso, publish_before_iso)
        fetch_youtube_channels_video_comments_and_replies_with_sentiment(status_label)
        status_label.config(text = "Data fetching finished!")
        status_label.update()




# Define the custom formatter
def millions_formatter(x, pos):
    return f'{x*1e-6:.1f}M'

def hundred_thousands_formatter(x, pos):
    return f'{x*1e-5:.1f}M'

# Functions of buttons

def most_views_channels():
    conn = sqlite3.connect('Youtube_database.db')
    query = '''SELECT channel_title, SUM(video_viewCount) AS total_view_count, SUM(video_likeCount) AS total_like_count, SUM(video_commentCount) AS total_comment_count
               FROM Youtube_hottest_videos_info
               GROUP BY channel_id, channel_title
               ORDER BY total_view_count DESC'''

    df = pd.read_sql_query(query, conn)
    conn.close()

    bar_width = 0.25
    bar_view_position = range(len(df["channel_title"]))
    bar_like_position = [x + bar_width for x in bar_view_position]
    bar_comment_position = [x + bar_width for x in bar_like_position]


    fig, ax = plt.subplots(figsize = (11, 7))
    ax.set_title("Most Views channels")
    ax.bar(bar_view_position, df["total_view_count"], width = bar_width, color = "r", label = "Total Views")
    ax.bar(bar_like_position, df["total_like_count"], width = bar_width, color = "g", label = "Total Likes")
    ax.bar(bar_comment_position, df["total_comment_count"], width = bar_width, color = "b", label = "Total Comments")
    ax.set_xlabel("Channels")
    ax.set_ylabel("Total Views")
    ax.set_xticks([x + bar_width for x in range(len(df["channel_title"]))])
    ax.set_xticklabels(df["channel_title"], rotation = 90)
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax.legend()
    fig.tight_layout()
    
    popup_window = tk.Toplevel(root)
    popup_window.title("Most Views Channels")
    popup_window.geometry("1200x1200")

    canvas = FigureCanvasTkAgg(fig, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def save_visualization():
        save_path = os.path.join(os.getcwd(), "most_views_channels.png")
        fig.savefig(save_path)
        messagebox.showinfo(f"Save Successful!", "Visualization saved as most_views_channels.png")
        print(f"Visualization saved as {save_path}")

    save_button = tk.Button(popup_window, text="Save Visualization", command=save_visualization)
    save_button.pack()

def most_views_categories():
    conn = sqlite3.connect('Youtube_database.db')
    query = '''SELECT video_category_name, SUM(video_viewCount) AS total_view_count, COUNT(video_id) AS total_number_of_video, SUM(video_viewCount)/COUNT(video_id) AS viewCount_per_video
               FROM Youtube_hottest_videos_info
               GROUP BY video_category_name
               ORDER BY viewCount_per_video DESC'''

    df = pd.read_sql_query(query, conn)
    conn.close()

    fig, ax = plt.subplots(figsize = (11, 7))
    ax.set_title("Most Views Categories")
    ax.bar(df["video_category_name"], df["viewCount_per_video"], color = ["red", "green", "blue", "orange", "purple", "black", "yellow"])
    ax.set_xlabel("Category")
    ax.set_ylabel("Views Per Video")
    ax.yaxis.set_major_formatter(FuncFormatter(hundred_thousands_formatter))
    fig.tight_layout()

    popup_window = tk.Toplevel(root)
    popup_window.title("Most Views Categories")
    popup_window.geometry("1200x1200")

    canvas = FigureCanvasTkAgg(fig, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def save_visualization():
        save_path = os.path.join(os.getcwd(), "most_views_categories.png")
        fig.savefig(save_path)
        messagebox.showinfo(f"Save Successful!", "Visualization saved as most_views_categories.png")
        print(f"Visualization saved as {save_path}")

    save_button = tk.Button(popup_window, text="Save Visualization", command=save_visualization)
    save_button.pack()

def most_views_publish_time():
    conn = sqlite3.connect('Youtube_database.db')
    query = '''SELECT * FROM Youtube_hottest_videos_info'''
    
    df = pd.read_sql_query(query, conn)
    df["publish_time"] = pd.to_datetime(df["publish_time"], format = "%Y-%m-%dT%H:%M:%SZ")
    df["publish_hour"] = df["publish_time"].dt.hour
    hourly_counts = df.groupby(by="publish_hour")["video_viewCount"].sum().reset_index(name = 'total_view_count')

    fig, ax = plt.subplots(figsize = (11, 7))
    ax.set_title("Most Views Publish Time")
    ax.bar(hourly_counts["publish_hour"], hourly_counts["total_view_count"])
    ax.set_xlabel("Hour")
    ax.set_ylabel("Total Views")
    ax.set_xticks(list(range(24)))
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    fig.tight_layout()
    
    popup_window = tk.Toplevel(root)
    popup_window.title("Most Views Publish Time")
    popup_window.geometry("1200x1200")

    canvas = FigureCanvasTkAgg(fig, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def save_visualization():
        save_path = os.path.join(os.getcwd(), "most_views_publish_time.png")
        fig.savefig(save_path)
        messagebox.showinfo(f"Save Successful!", "Visualization saved as most_views_publish_time.png")
        print(f"Visualization saved as {save_path}")

    save_button = tk.Button(popup_window, text="Save Visualization", command=save_visualization)
    save_button.pack()

def load_Youtube_hottest_videos_info_to_csv():
    conn = sqlite3.connect("Youtube_database.db")
    select_all_videos_info_query = '''SELECT * FROM Youtube_hottest_videos_info'''
    df = pd.read_sql_query(select_all_videos_info_query, conn)
    df.to_csv('Youtube_hottest_videos_info.csv')
    conn.close()
    status_load_Youtube_hottest_videos_info_to_csv.config(text="Success! Data loaded to 'Youtube_hottest_videos_info.csv'")
    status_load_Youtube_hottest_videos_info_to_csv.update()
    print("Youtube videos'info successfully loaded to file 'Youtube_hottest_videos_info.csv'")

def load_Youtube_channels_info_to_csv():
    conn = sqlite3.connect("Youtube_database.db")
    select_all_channels_info_query = '''SELECT * FROM Youtube_channels_info'''
    df = pd.read_sql_query(select_all_channels_info_query, conn)
    df.to_csv('Youtube_channels_info.csv')
    conn.close()
    status_load_Youtube_channels_info_to_csv.config(text="Success! Data loaded to 'Youtube_channels_info.csv'")
    status_load_Youtube_channels_info_to_csv.update()
    print("Youtube channels info successfully loaded to file 'Youtube_channels_info.csv'")

def load_Youtube_channels_comments_with_sentiment():
    conn = sqlite3.connect("Youtube_database.db")
    select_all_comments_info_query = '''SELECT * FROM Youtube_channels_comments_with_sentiment'''
    df = pd.read_sql_query(select_all_comments_info_query, conn)
    df.to_csv('Youtube_channels_comments_with_sentiment.csv')
    conn.close()
    status_load_Youtube_channels_comments_with_sentiment.config(text="Success! Data loaded to 'Youtube_channels_comments_with_sentiment.csv'")
    status_load_Youtube_channels_comments_with_sentiment.update()
    print("Youtube videos'comments' info successfully loaded to file 'Youtube_channels_comments_with_sentiment.csv'")

def load_Youtube_channels_replies_with_sentiment():
    conn = sqlite3.connect("Youtube_database.db")
    select_all_replies_info_query = '''SELECT * FROM Youtube_channels_replies_with_sentiment'''
    df = pd.read_sql_query(select_all_replies_info_query, conn)
    df.to_csv('Youtube_channels_replies_with_sentiment.csv')
    conn.close()
    status_load_Youtube_channels_replies_with_sentiment.config(text="Success! Data loaded to 'Youtube_channels_replies_with_sentiment.csv'")
    status_load_Youtube_channels_replies_with_sentiment.update()
    print("Youtube videos'replies' info successfully loaded to file 'Youtube_channels_replies_with_sentiment.csv'")

# Function to display DataFrame in a new window
def display_dataframe(df):
    # Create a new window
    window = tk.Toplevel(root)
    window.title("Ranking Table")

    # Create Treeview
    tree = ttk.Treeview(window)

    # Define columns
    tree['columns'] = list(df.columns)
    tree['show'] = 'headings'  # Hide the first empty column

    # Create column headings
    for column in df.columns:
        tree.heading(column, text=column)  # Set column heading
        tree.column(column, anchor='center')  # Center align column data

    # Insert DataFrame data into Treeview
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    
    # Pack the Treeview
    tree.pack(expand=True, fill='both')
    
    # Define function to save DataFrame as CSV to a default path
    def save_dataframe():
        save_path = os.path.join(os.getcwd(), "Ranking_Table.csv")
        df.to_csv(save_path, index=False)
        messagebox.showinfo("Save Successful", f"Ranking table saved as Ranking_Table.csv")

    # Create Save button
    save_button = tk.Button(window, text="Save Ranking Table", command=save_dataframe)
    save_button.pack(pady=10)  # Add some padding around the button

# Select elements needed in ranking table & display
def alter_db_columns():
    conn = sqlite3.connect("Youtube_database.db")
    query = '''SELECT ROW_NUMBER() OVER (ORDER BY video_view_rate DESC, positive_comment_rate DESC, positive_reply_rate DESC) AS rank, *
               FROM (
                     SELECT 
                           hot.video_id, 
                           hot.video_title,  
                           cha.channel_title,
                           hot.video_viewCount,
                           cha.channel_viewCount,
                           ROUND(CAST(hot.video_viewCount AS REAL) / CAST(cha.channel_viewCount AS REAL) * 100, 2) AS video_view_rate,
                           SUM(CASE WHEN video_comment_textDisplay_sentiment = 'POSITIVE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS positive_comment_rate,   
                           SUM(CASE WHEN reply_textDisplay_sentiment = 'POSITIVE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS positive_reply_rate
                     FROM Youtube_hottest_videos_info AS hot
                     LEFT JOIN Youtube_channels_comments_with_sentiment AS com
                     ON hot.channel_id = com.channel_id
                     LEFT JOIN Youtube_channels_replies_with_sentiment AS rep
                     ON hot.channel_id = rep.channel_id
                     LEFT JOIN Youtube_channels_info AS cha
                     ON hot.channel_id = cha.channel_id
                     GROUP BY hot.video_id, hot.video_title, com.channel_id, cha.channel_title
               ) AS subquery
               ORDER BY video_view_rate DESC, positive_comment_rate DESC, positive_reply_rate DESC;
            '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    display_dataframe(df)  # Call the function to display the DataFrame

def find_numeric_correlation(): # Focus on Youtube_hottest_videos_info & Youtube_channels_info, especially about video_viewCount, channel_viewCount
    conn = sqlite3.connect("Youtube_database.db")
    query = '''SELECT
               hot.video_viewCount,
               hot.video_likeCount,
               hot.video_commentCount,
               cha.channel_viewCount,
               cha.channel_subscriberCount,               
               cha.channel_videoCount
               FROM Youtube_hottest_videos_info AS hot
               INNER JOIN Youtube_channels_info AS cha
               ON hot.channel_id = cha.channel_id
            '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    numeric_correlation_matrix = df.corr()

    fig, ax = plt.subplots(figsize = (11, 7))
    ax.set_title("Correlation Matrix")
    sns.heatmap(numeric_correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax)
    plt.xticks(rotation=0, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.close()
    
    popup_window = tk.Toplevel(root)
    popup_window.title("Correlation Matrix")
    popup_window.geometry("1200x1200")

    canvas = FigureCanvasTkAgg(fig, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def save_visualization():
        save_path = os.path.join(os.getcwd(), "Correlation Matrix.png")
        fig.savefig(save_path)
        messagebox.showinfo(f"Save Successful!", "Visualization saved as Correlation Matrix.png")
        print(f"Visualization saved as {save_path}")

    save_button = tk.Button(popup_window, text="Save Visualization", command=save_visualization)
    save_button.pack()

def remove_database():
    db_path = '/Users/hickeychan/Desktop/JDE/Youtube_analysis_project/Youtube_database.db'

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            messagebox.showinfo("Success", "Database successfully removed!")
        except Exception as e:
            messagebox.showerror("Fail", "Fail on remove database!")
    else:
        messagebox.showwarning("Warning", "No existing database!")

# Create interface with tkinter
root = tk.Tk()
root.title("Youtube Data Analysis")
root.geometry("1000x1000")

Analysis_start_date_label = tk.Label(root, text = "Analysis start date: ")
Analysis_end_date_label = tk.Label(root, text = "Analysis end date: ")
calendar_start_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")
calendar_end_date = Calendar(root, selectmode = "day", date_pattern = "mm/dd/yyyy")
fetch_videos_info_button = tk.Button(root, text = "Fetch videos' data", command=fetch_videos_data)
status_label = tk.Label(root, text="Ready to fetch data?")
status_load_Youtube_hottest_videos_info_to_csv = tk.Label(root, text="Status: None")
status_load_Youtube_channels_info_to_csv = tk.Label(root, text="Status: None")
status_load_Youtube_channels_comments_with_sentiment = tk.Label(root, text="Status: None")
status_load_Youtube_channels_replies_with_sentiment = tk.Label(root, text="Status: None")
load_videos_info_button = tk.Button(root, text = "Load videos' data to csv", command=load_Youtube_hottest_videos_info_to_csv)
load_channels_info_button = tk.Button(root, text = "Load videos' channels' data to csv", command=load_Youtube_channels_info_to_csv)
load_Youtube_channels_comments_with_sentiment_button = tk.Button(root, text = "Load videos' comments data to csv", command=load_Youtube_channels_comments_with_sentiment)
load_Youtube_channels_replies_with_sentiment_button = tk.Button(root, text = "Load videos' replies data to csv", command =load_Youtube_channels_replies_with_sentiment)
most_views_channels_button = tk.Button(root, text = "Most views channels", command=most_views_channels)
most_views_categories_button = tk.Button(root, text = "Most views categories", command=most_views_categories)
most_views_publish_time_button = tk.Button(root, text = "Most views videos' publish time", command=most_views_publish_time)
show_dataframe_button = tk.Button(root, text="Show DataFrame", command=alter_db_columns)
show_correlation_matrix_button = tk.Button(root, text="Show videos & channels' correlation", command=find_numeric_correlation)
remove_database_button = tk.Button(root, text="Remove database", command=remove_database)

# Pack elements in GUI
Analysis_start_date_label.pack()
calendar_start_date.pack()
Analysis_end_date_label.pack()
calendar_end_date.pack()
fetch_videos_info_button.pack()
status_label.pack()
load_videos_info_button.pack()
status_load_Youtube_hottest_videos_info_to_csv.pack()
load_channels_info_button.pack()
status_load_Youtube_channels_info_to_csv.pack()
load_Youtube_channels_comments_with_sentiment_button.pack()
status_load_Youtube_channels_comments_with_sentiment.pack()
load_Youtube_channels_replies_with_sentiment_button.pack()
status_load_Youtube_channels_replies_with_sentiment.pack()
most_views_channels_button.pack()
most_views_categories_button.pack()
most_views_publish_time_button.pack()
show_dataframe_button.pack()
show_correlation_matrix_button.pack()
remove_database_button.pack()

root.mainloop()

