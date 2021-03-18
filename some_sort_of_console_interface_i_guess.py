import argparse
import os
import sys

parser  = argparse.ArgumentParser(description="This program tracks the motion on chosen piece of video (live webcam , online stream , video file)", 
                                  usage="usage: some_sort_of_console_interface_i_guess.py [-h] [-v VIDEO_PATH] [-a MIN_AREA] [-s STREAM_URL] [-d] [-c]")
parser.add_argument("-v", "--video", type=str , help="tracks motion on video file")
area = parser.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size in pixels which can be considered as motion (default is 500)")
parser.add_argument("-s", "--stream", type=str , help="track motion on online stream")
parser.add_argument("-d" , "--debug" , action='store_true' , help="opens motion tracker in debug mode which shows different stages of tracking motion")
parser.add_argument("-c" , "--camera" , action='store_true' , help="track motion on your webcam")
arguments=vars(parser.parse_args())

if arguments.get("video") is not None:
   if arguments.get("steam") is not None or arguments.get("camera") is True:
       raise argparse.ArgumentError("More than one sorce was given")
   if os.path.isfile(arguments.get("video")) is False:
       raise argparse.ArgumentError("Sorce file was not found")
   if arguments.get("debug") is True:
       print("video with debug magic happens")
   else:
       print("video magic happens")
if arguments.get("camera") is True:
   if arguments.get("steam") is not None or arguments.get("video") is not None:
       raise argparse.ArgumentError("More than one sorce was given")
   if arguments.get("debug") is True:
       print("camera with debug magic happens")
   else:
       print("camera magic happens")
if arguments.get("stream") is not None:
   if arguments.get("video") is not None or arguments.get("camera") is True:
       raise argparse.ArgumentError("More than one sorce was given")
   ##wypadałoby moze cos co sprawdza czy url jest poprawny
   if arguments.get("debug") is True:
       print("stream with debug magic happens")
   else:
       print("stream magic happens")

   

