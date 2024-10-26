# YoutubeDataAnalysis
<img src = "./banner.png" alt = "Banner" height = 300 width = 530>
<br>
<br>

# Table of contents
1. [About](#-about)
2. [Output](#-output)
3. [Key Assumption](#-key-assumption)
4. [Important Notes](#️-important-notes)
5. [Elements Built](#-elements-built)
6. [How to Build](#-how-to-build)
7. [Contact](#-contact)
<br>

# 📚 About
This project aims to create a YouTube video ranking table to help individuals and businesses analyze the top 50 most popular videos within a user-specified time range. The analysis includes metrics such as video_view_rate, positive_comment_rate, and positive_reply_rate, allowing users to use high-ranking videos as benchmarks for improving their own YouTube channels
<br>
<br>

# 💡 Output
## Graphical User Interface (GUI)
<img src= "./GUI.png" alt = "GUI" height = 400 width = 500>

## Sample Output
<img src= "./Ranking Table.png" alt = "analysis_1" height = 400 width = 1200>

# 💬 Key Assumption
1. **Ranking logic:** The ranking table is sorted by video_view_rate, positive_comment_rate, and positive_reply_rate in descending order

2. **video_view_rate:** The proportion of views for a specific video compared to the total views of the channel. Higher rates indicate significant impact

3. **positive_comment_rate:** The ratio of positive sentiment comments to the total sentiment comments for each video, indicating viewer engagement and potential channel support

4. **positive_reply_rate:** The ratio of positive replies to the total sentiment replies on comments, reflecting viewer support and engagement. positive_comment_rate is prioritized over positive_reply_rate as comments are directly visible on the video link, while replies are less prominent
<br>
<br>

# ❗️ Important Notes
1. **First-Time Use:** Select your desired analysis start and end dates using the calendars, then press "Fetch videos' data" to collect data. This initial fetch enables all functions. Until this step is completed and shows "Data fetching finished!", no other buttons will work

2. **Data Fetching Defaults:** The default fetch includes the 50 most-viewed videos in the specified period, with a maximum of 2500 comments and replies per video. Data fetching may take a while. To accelerate, modify the global variable max_results, the maxResults parameter in commentThreads().list(), and comments().list() to lower values (e.g., 5) in Fetch_all_data.py

3. **Saving Visualizations:** Use the "Save" button to keep specific visualizations of interest

4. **Exploring New Date Ranges:** Click "Remove database" before selecting a new date range to ensure accurate results. Once "Success: Database successfully removed!" appears, return to Step 1 to analyze another period
<br>
<br>

# 📝 Elements Built
## Workflow
<img src="./Workflow.png" alt = "workflow.png" height = 100 width = 900>

<br>

**1. Data Extraction:** Data Extracted through methods in [Youtube Data API](https://developers.google.com/youtube/v3), including [Search](https://developers.google.com/youtube/v3/docs/search), [Channels](https://developers.google.com/youtube/v3/docs/channels), [Videos](https://developers.google.com/youtube/v3/docs/videos), [VideoCategories](https://developers.google.com/youtube/v3/docs/videoCategories), [CommentThreads](https://developers.google.com/youtube/v3/docs/commentThreads) and [Comments](https://developers.google.com/youtube/v3/docs/comments)
<br>

**2. Sentiment Analysis:** Applied [DistilBERT](https://huggingface.co/docs/transformers/en/model_doc/distilbert) to do comments' & replies' sentiment analysis
```python
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

for index, video_id_element in enumerate(new_video_id_list):
            request_youtube_channels_video_commentThreads = youtube.commentThreads().list(
                part="snippet, replies",
                videoId=video_id_element,
                maxResults=50
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
                all_video_comment_textDisplay_list.append(comment_info_dict["video_comment_textDisplay"])
                comment_textDisplay_sentiment = analyze_sentiment(comment_info_dict["video_comment_textDisplay"])
                all_comment_textDisplay_sentiment_list.append(comment_textDisplay_sentiment)
```
```python
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
            reply_publishedAt = reply_snippet.get("publishedAt") # Turn to datetime object before fetching into tab
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
```
<br>

**3. Create tables & Insert data:** There are 4 tables created: "Youtube_hottest_videos_info", "Youtube_channels_info", "Youtube_channels_comments_with_sentiment", "Youtube_channels_replies_with_sentiment", Data collected by different methods are inserted to those tables respectively


**4. Functions in tkinter GUI:** Fetch data; Show & Save visualizations; Remove database

Visualization example:

<img src = "./Correlation Matrix.png" alt = "Correlation Matrix" height = 300 width = 530>
<br>
<br>

### Try to find your own Youtube strategy now !!!
copy the following code to your terminal:
```terminal
git clone https://github.com/KevinChan74/YoutubeDataAnalysis.git
```
<br>

# 📧 Contact
If you're interested in my project, please feel free to contact me through email, my email is kevincyhei@gmail.com.