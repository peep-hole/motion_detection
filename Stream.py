from imutils.video import VideoStream
import argparse
from imutils.video import FPS
import imutils
import cv2

# argument parser - to load stream according to your option
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--stream", type=str, help="Link to the video stream with some motion to detect.")
parser.add_argument("-p", "--path", type=str, help="Path to the video on your device to detect some motion")
args = vars(parser.parse_args())

# Firstly we try to receive a stream from web
if args["stream"] is not None:
    print("Capturing video stream from: ", args["stream"])
    stream = cv2.VideoCapture(args["stream"])
    fps = FPS().start()

# Here we see that if booth options are chosen, the stream has higher priority than a file
elif args["path"] is not None:
    print("Reading video from path: ", args["path"])
    stream = cv2.VideoCapture(args["path"])
    fps = FPS().start()

# Only if no options were added, we fire the camera in your device
else:
    print("Capturing video stream from your web cam")
    stream = VideoStream(src=0).start()
    fps = FPS().start()

# loop over frames from the video file stream
# It will probably be modified a lot when merged with other parts of this project
while True:
    # grab the frame from the threaded video file stream (according to args)
    if args["stream"]: (grabbed, frame) = stream.read()
    elif args["path"]: (grabbed, frame) = stream.read()
    else: (grabbed, frame) = True, stream.read()

    # if the frame was not grabbed, then we have reached the end of the stream
    if not grabbed:
        break

    # resize the frame and convert it to grayscale
    frame = imutils.resize(frame, width=600)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # I do not know what this line (48) do, but it works without :)
    # frame = np.dstack([frame, frame, frame])

    # If <ESC> pressed, exit program
    key = cv2.waitKey(1)
    if key == 27:
        break

    # show the frame and update the FPS counter
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
if args["path"]: stream.release()
cv2.destroyAllWindows()
