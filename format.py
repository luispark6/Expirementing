
import os
from sys import api_version
import googleapiclient.discovery
from googleapiclient.discovery import build
import googleapiclient.errors
import mysql.connector
import matplotlib.pyplot as plt

##Primary ID could be the time cause no time can be the same.
#good way to uniquely identify each register of channel's databin/mysqladmin -u root shutdown -p

def main():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyC22GFWR6balVvcOFszYZ9ce0GTGmgff14" #my api key
    youtube = build(api_service_name, api_version, developerKey=api_key)

    #connecting to local host which is my computer
    mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Leoluis02",
    database = "Youtube_Statistics"
    )
    #creating object that allows me to execute SQL queries
    cursor = mydb.cursor()

    #will output table named "channels", and we will fetch
    #this output with fetchone
    cursor.execute("SHOW TABLES LIKE 'Information'")
    result = cursor.fetchone()
    #if result is true(there is data with table name channels),
    #the tabel already exists which means we dont need to create
    #a row of the necessary columns(likes, views, channel name, etc.)
    if result:
        # Table exists, do nothing
        print("Table already exists")
    else:
        # Create the channels table
        cursor.execute("""
            CREATE TABLE Information (
                id INT NOT NULL AUTO_INCREMENT,
                channel VARCHAR(255),
                views INT,
                likes INT,
                time INT,
                subscribers VARCHAR(255),
                PRIMARY KEY (id)
            )
        """)
        print("Table created successfully")

    

    rick= "UCJquYOG5EL82sKTfH9aMA9Q" #the id for ricks channel
    vert = "UCHnyfMqiRRG1u-2MsSQLbXA" #id code for vertasiums channel

    #requesting the channel information from youtube server
    request_channel_info = youtube.channels().list( 
        part="snippet,contentDetails,statistics",
        id=vert
    )
    #executes the request and feeds the information to response channel
    response_channel = request_channel_info.execute()

    #this gets the upload id which gives us a playlist id of the most recent uploads from
    #the channel
    playlistid = response_channel['items'][0]["contentDetails"]["relatedPlaylists"]['uploads']

    #this requests the information for the lastest uploads  information from the channel 
    #and we can specify how many recently uploaded videos we want
    request_videos = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlistid,
        maxResults=1
    )
    #executes the request
    response_videos = request_videos.execute()

    #creating new dictionary with more organized data
    vertasium = {}
    vertasium["channel"] = response_channel["items"][0]["snippet"]['title']
    vertasium["description"] = response_channel["items"][0]["snippet"]['description']
    vertasium["statistics"] = response_channel["items"][0]['statistics']
    
    #this will be used to get information for each vide
    #the video id will be used to scrap specific video stats such as likes and views
    acc = 0
    #in this for loop, the acc will be the key for the ith video title, time it released
    #video id, the description of the video, and another dictionary with statistics of the video
    for i in response_videos['items']:
        acc = acc+ 1
        vertasium[acc] = [i['snippet']['title'],i['contentDetails']['videoPublishedAt'], \
            i['contentDetails']['videoId'],i['snippet']['description']]

        request_video_id = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=vertasium[acc][2])
        response_video_id = request_video_id.execute()
        vertasium[acc].append(response_video_id["items"][0]["statistics"])


    # Defines the data to insert
    data = [("Vertaisum", int(vertasium['statistics']['viewCount']), 500, "2023-05-13 12:00:00", 10000)]
    # Insert the data into the table
    sql = "INSERT INTO Information (channel, views, likes, time, subscribers) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, data)

    mydb.commit()


    print(vertasium)

    mydb.close()
main()