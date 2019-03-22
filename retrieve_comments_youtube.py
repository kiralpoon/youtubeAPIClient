#! /usr/bin/python
import httplib2
import os, sys
import json
import time
from osc_message_client import sendVRC

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

YOUTUBEURL = "https://www.youtube.com/watch?v=<youtubelive id>" #youtubelive URL
CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
# argparser = argparse.ArgumentParser()

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))


VALID_BROADCAST_STATUSES = ("all", 'active', 'completed', 'upcoming',)


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READONLY_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  flow.user_agent = "APIKey"

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  acquireLiveChatId(credentials)  


  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

# Retrieve a list of broadcasts with the specified status.
def list_broadcasts(youtube, broadcast_status): 
  print("Broadcasts with status '%s':" % broadcast_status) 

  list_broadcasts_request = youtube.liveBroadcasts().list(
    broadcastStatus=broadcast_status,
    part="id,snippet",
    maxResults=50
  )
  while list_broadcasts_request:
    list_broadcasts_response = list_broadcasts_request.execute()
    for broadcast in list_broadcasts_response.get("items", []):
      print("%s (%s)" % (broadcast["snippet"]["title"], broadcast["id"]))

    list_broadcasts_request = youtube.liveBroadcasts().list_next(
      list_broadcasts_request, list_broadcasts_response)

def acquireLiveChatId(credentials): 
  print("Getting live chat id")
  urlP = YOUTUBEURL[-11:]
  http = credentials.authorize(httplib2.Http())
  url = "https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id="
  url += urlP

  res, data = http.request (url)
  data = json.loads (data.decode ())
  print(data)
  try:
    chat_id = data ["items"] [0] ["liveStreamingDetails"] ["activeLiveChatId"]
  except:
    print("Reading live error")
    return
  print ("ChatID: " + chat_id)
  print("Obtained ChatID")
  url = "https://www.googleapis.com/youtube/v3/liveChat/messages?part=snippet,authorDetails"
  url += "&liveChatId=" + chat_id
  commentGet(data,url,http)

def commentGet(data,url,http):
    commentDifference = ""
    commentDBlue = False
    commentDifference_middle = ""
    prev_items_data_length = 0
 
    print("retrieving comment")
    while True:
        res, data = http.request(url)
        data = json.loads(data.decode())
 
        if data.get("items"):   #in case item not exists
            curr_items_data_length = len(data["items"])
            # print("data" + str(data))
            print("datum length: " + str(len(data["items"])))
            # print("first item: " + str(data["items"][0]))
            # if prev_items_data_length == curr_items_data_length:
            #   pass
            # else:
            #   for 
            for datum in data["items"]:
                snippet = datum.get("snippet")
                if snippet.get("textMessageDetails"):
                    textMessageDetails = snippet.get("textMessageDetails")
                    if textMessageDetails.get("messageText"):

                        comment = datum["snippet"]["textMessageDetails"]["messageText"]
                        name = datum["authorDetails"]["displayName"]

                        if commentDBlue == True:
                            print(name + ": " + comment)

                            if(comment=="cube on"):
                              sendVRC('/cube/activate', '1')
                            elif(comment=="cube off"):
                              sendVRC('/cube/activate', '0')
                            elif(comment=="tower" or comment=="Tower"):
                              sendVRC('/gift/tower', '1')
                              time.sleep(1)
                              sendVRC('/gift/tower', '0')
                            elif(comment=="bear" or comment=="Bear"):
                              sendVRC('/gift/bear', '1')
                              time.sleep(1)
                              sendVRC('/gift/bear', '0')
                            elif(comment=="flower" or comment == "Flower"):
                              sendVRC('/gift/flower', '1')
                              time.sleep(1)
                              sendVRC('/gift/flower', '0')

                        if commentDifference == name + ":" + comment:
                            commentDBlue = True
                        commentDifference_middle = name + ":" + comment
        prev_items_data = data["items"]
        prev_items_data_length = len(data["items"])
        prev_items_data_index = prev_items_data_length -1
        commentDifference = commentDifference_middle
        time.sleep(2)
        commentDBlue = False

if __name__ == "__main__":
  argparser.add_argument("--broadcast-status", help="Broadcast status",
    choices=VALID_BROADCAST_STATUSES, default=VALID_BROADCAST_STATUSES[0])
  args = argparser.parse_args()
  youtube = get_authenticated_service(args)
  try:
    pass
    #acquireLiveChatId(youtube, args.broadcast_status)
    #list_broadcasts(youtube, args.broadcast_status)
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))