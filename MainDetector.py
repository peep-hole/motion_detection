from imutils.video import VideoStream
from PIL import ImageTk, Image
import numpy as np
import datetime
import argparse
import os
import imutils
import time
import cv2
import MenuHandler
ALERT_TIME = 30
last_captured = 0
base_frame_masked = None
base_frame = None
counter = 0

def apply_mask(frame):  # narazie zwraca ta sama klatke
    return frame


# stream = cv object stream, debug mode = czy pokazywac te dodatkowe okna jak szara skala blurr itp,
# full debug = pokazuje dodatkowo zamaskowane frame'y, background_refresh_rate = jak czesto odswiezac tło

def detect(stream, type_stream, min_area=500, debug_mode=False, full_debug=False, background_refresh_rate=100):
    root = MenuHandler.setUpMenu()
    lmain = MenuHandler.getLabel()



    #frame = None
    # ta wartość będzie wskazywała jak długo po ustaniu ruchu wyswietlac komunikat
    # (w momencie ruchu ustawia to na ALERT_TIME i dekrementuje w kazdej iteraci)
    # dodatkowo zapobiega miganiu komunikatu w momencie aktualizacji tła
    

    # licznik klatek, na jego podstawie bedziemy odswiezac tło

    running = True
    def render():
        global last_captured
        global base_frame_masked
        global base_frame
        global counter
        # odczytanie frama + konwersja jesli jest to wideo (nie sprawdzałem jeszcze jak działa to dla streamów)
        frame = stream.read()
        frame = frame if type_stream == "camera" else frame[1]

        # jesli nie udalo sie odczytac frama to program konczy sie
        if frame is None:
            running=False
        maskCoords = MenuHandler.getMaskCoords()
        # najpierw mały resize, a nastepnie stosujemy maske
        frame = imutils.resize(frame, width=500)
        masked_frame = apply_mask(frame)

        # wykonuje jednoczesnie konwersje na skale szarosci a potem rozmycie dla frame'a z maska i bez aby wykryc ruch
        # tam gdzie jest maska, a wyswietlac pelne wiedo
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        masked_gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
        masked_blurred = cv2.GaussianBlur(masked_gray, (21, 21), 0)
        # tutaj ustawiamy tło jesli jesli jeszcze go nie mamy lub jesli wystarczająco długo było nieaktualizowane
        if base_frame_masked is None or counter == background_refresh_rate:

            base_frame = blurred
            base_frame_masked = masked_blurred
            counter = 0 # resetujemy licznik odswierzenia

        # ponizej obliczamy roznice klatek aby nastepnie wyswietlic threshold
        masked_frame_diff = cv2.absdiff(base_frame_masked, masked_blurred)
        frame_diff = cv2.absdiff(base_frame, blurred)

        masked_thresh = cv2.threshold(masked_frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        if(maskCoords != None and maskCoords.__len__()>1):
            x = min(maskCoords[0],maskCoords[2])
            y=  min(maskCoords[1],maskCoords[3])
            rows,cols=masked_thresh.shape
            M = np.float32([[1,0,x],[0,1,y]])
            masked_thresh=masked_thresh[min(maskCoords[1],maskCoords[3]):max(maskCoords[3],maskCoords[1]),min(maskCoords[0],maskCoords[2]):max(maskCoords[0],maskCoords[2])]
            masked_thresh=cv2.warpAffine(masked_thresh,M,(cols,rows))
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]

        # to co ponizej poszerza nasz threshold, tzn. gdybysmy pokazali durszlak(aka sitko) z bliska to wypełni to jego
        # dziurki i rozleje delikatnie dookoła, w końću kształt obiektu jest bez znaczenia
        thresh = cv2.dilate(thresh, None, iterations=2)
        masked_thresh = cv2.dilate(masked_thresh, None, iterations=2)

        # tutaj konturujemy nasz threshold i zapisujemy te kontury (moze wykrywac wiele obiektów)
        contours = cv2.findContours(masked_thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # iterujemy po konturach, sprawdzamy czy wielkosc pola jest wieksza niz minimalna do wykrycia, a nastepnie
        # nakładamy ten kontur na oryginalny obrazek i ustawiamy licznik klatek wyswietlania alertu
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:

                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                last_captured = ALERT_TIME
        
        if(maskCoords!=None):
            cv2.rectangle(frame,(maskCoords[0],maskCoords[1]),(maskCoords[2],maskCoords[3]),(255,255,255),2)
        # jesli wykryto ruch to odlicza czas, w ktorym pokazuje alert
        if last_captured > 0:
            cv2.putText(frame, "Motion Detected!", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            last_captured -= 1

        # w tym miejscu nanoszona do wyswietlenia jest data i godzina
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # wyswietlanie
        image_mode = MenuHandler.getStatus()
        frame_types=[frame,gray,blurred,thresh,frame_diff,masked_gray,masked_blurred,masked_thresh,masked_frame_diff]

        cv2image = cv2.cvtColor(frame_types[image_mode], cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        #root.mainloop()
        #cv2.imshow("Motion Detection", frame)
        
        if debug_mode:
            cv2.imshow("Gray", gray)
            cv2.imshow("Blurred", blurred)
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Frame Difference", frame_diff)

        if full_debug:
            cv2.imshow("Gray With Mask", masked_gray)
            cv2.imshow("Blurred With Mask", masked_blurred)
            cv2.imshow("Thresh With Mask", masked_thresh)
            cv2.imshow("Frame Difference With Mask", masked_frame_diff)

        # jesli wcisnie sie esc to program konczy sie
        key = cv2.waitKey(1)
        if key == 27:
            running=False

        # inkrementacja ilosci klatek przed ostatnim odswierzeniem
        counter += 1
        root.after(10,render)

        
    # zamkniecie zrodla i okien
    root.after(1,render)
    root.mainloop()

# tutaj mozna odpalic na wlasnej kamerze i sprawdzic dzialanie
# trial = VideoStream(src=0).start()
# time.sleep(2.0)
# detect(trial, "camera", debug_mode=True, full_debug=True)

# #tutaj rownierz test tylko na wideo (trzeba dodac odpowiedni film do katalogu)
# trial2 = cv2.VideoCapture("CyborgAGHiscoming.mp4")
# detect(trial2, "video", debug_mode=True, full_debug=True)

def main():
    parser = argparse.ArgumentParser(
        description="This program tracks the motion on chosen piece of video (live webcam , online stream , video file)",
        usage="usage: some_sort_of_console_interface_i_guess.py [-h] [-v VIDEO_PATH] [-a MIN_AREA] [-s STREAM_URL] [-d] [-c]")
    parser.add_argument("-v", "--video", type=str, help="tracks motion on video file")
    parser.add_argument("-a", "--min_area", type=int, default=500,
                               help="minimum area size in pixels which can be considered as motion (default is 500)")
    parser.add_argument("-s", "--stream", type=str, help="track motion on online stream")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="opens motion tracker in debug mode which shows different stages of tracking motion")
    parser.add_argument("-c", "--camera", action='store_true', help="track motion on your webcam")
    arguments = vars(parser.parse_args())

    if arguments.get("video") is not None:
        if arguments.get("steam") is not None or arguments.get("camera") is True:
            raise argparse.ArgumentError("More than one sorce was given")
        if os.path.isfile(arguments.get("video")) is False:
            raise argparse.ArgumentError("Sorce file was not found")
            # Z pliku
        print("video with debug magic happens")
        stream = cv2.VideoCapture(arguments.get("video"))
        detect(stream, "video", arguments.get("min_area"), arguments.get("debug"))

    if arguments.get("camera") is True:
        if arguments.get("steam") is not None or arguments.get("video") is not None:
            raise argparse.ArgumentError("More than one sorce was given")
        stream = VideoStream(src=0).start()
        detect(stream, "camera", arguments.get("min_area"), arguments.get("debug"))

    if arguments.get("stream") is not None:
        if arguments.get("video") is not None or arguments.get("camera") is True:
            raise argparse.ArgumentError("More than one sorce was given")
        # wypadałoby moze cos co sprawdza czy url jest poprawny

        stream = cv2.VideoCapture(arguments.get("stream"))
        detect(stream, "stream", arguments.get("min_area"), arguments.get("debug"))


if __name__ == "__main__":
    main()
