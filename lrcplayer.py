from Tkinter import *
from lyricshandler import parse_lrc
from banshee_info import Banshee_Info
from lyrics import MiniLyrics
import logging
import urllib
import thread
import time
import os

logging.basicConfig(filename="log.txt", filemode="w", level=logging.DEBUG)

class GUI(object):
    def __init__(self, master):
        self.master = master
        self.lyrics_tags = False
        self.previous_lyrics = ""
        self.master.title("Lyrics Player")
        self.master.geometry("500x300")
        self.init_gui()
        thread.start_new_thread(self.thread_handler, ())

    def init_gui(self):
        self.lyrics_previous_label = Label(self.master, text="previous here", bg="yellow", fg="black", font=('Arial', 14, 'bold'))
        self.lyrics_previous_label.pack(fill=BOTH, expand=1)
        self.lyrics_label = Label(self.master, text="lyrics here",bg="yellow", fg="black", font=('Arial' ,14, 'bold'))
        self.lyrics_label.pack(fill=BOTH, expand=1)
        self.song_title_label = Label(self.master, text="song title", font=('Ubuntu-Mono',12))
        self.song_title_label.pack(anchor=W)
        self.song_singer_label = Label(self.master, text="singer here")
        self.song_singer_label.pack(anchor=W)
        self.elapsed_time_label = Label(self.master, text="[00:00:00]")
        self.elapsed_time_label.pack(anchor=W)

    def reset_gui(self):
        self.lyrics_previous_label["text"] = ""
        self.song_title_label["text"] = ""
        self.song_singer_label["text"] = ""
        self.elapsed_time_label["text"] = ""

    def thread_handler(self):
        while True:
            self.banshee_controller()
            time.sleep(0.001)

    def banshee_controller(self):
        self.status = "playing"
        b_obj = Banshee_Info()
        try:
            self.status = str(b_obj.get_state())
        except AttributeError, e:
            self.status = "not running"      # banshee not running
        if self.status == "not running":
            self.lyrics_label["text"] = "Banshee not running"
        if self.status == "paused":
            self.lyrics_label["text"] = "Banshee Paused"
        if self.status == "idle":
            self.lyrics_label["text"] = "Banshee Idle"
        if self.status == "playing":
            song_path = urllib.unquote(str(b_obj.get_uri()))[7:]
            song_artist = b_obj.get_author()
            song_title = b_obj.get_title()
            pos_in_sec = int(b_obj.banshee.GetPosition())/1000
            custom_position = b_obj.get_custom_position()
            self.song_title_label["text"] = song_title
            self.song_singer_label["text"] = song_artist
            self.elapsed_time_label["text"] = "[%s]" %custom_position
            self.display_lyrics(song_path, song_artist, song_title, pos_in_sec, custom_position)

    def display_lyrics(self, song_path, song_artist, song_title, pos_in_sec, custom_position):
        def load_lyrics(lrc_path):
            with open(lrc_path) as fh:
                lrc_data = fh.read()
                lyrics, tags = parse_lrc(lrc_data)
                return (lyrics, tags)

        if self.lyrics_tags == False:
            if os.path.exists(song_path+".lrc"):
                lyrics, tags = load_lyrics(song_path+".lrc")
                if tags != None:
                    tags_dict = {x[0]:x[1] for x in tags}
                    try:
                        self.lyrics_label["text"] = tags_dict[pos_in_sec]
                        self.lyrics_previous_label["text"] = self.previous_lyrics
                        self.previous_lyrics = self.lyrics_label["text"]
                    except KeyError:
                        pass
                else:
                    self.lyrics_label["text"] = "Lyrics Not available"
            else:
                try:
                    urllib.urlopen("http://www.google.com")
                except IOError:
                    self.lyrics_label["text"] = "internet not working can't download lyrics"
                    self.lyrics_previous_label["text"] = ""
                else:    
                    lyrics_dict = MiniLyrics(song_artist, song_title)
                    urllib.urlretrieve(lyrics_dict[0]["url"], song_path+".lrc")
        else:
            pass


root = Tk()
gui_obj = GUI(root)
root.mainloop()