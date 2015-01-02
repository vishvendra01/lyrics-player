#!/usr/bin/env python
from Tkinter import *
from lyricshandler import parse_lrc
from banshee_info import Banshee_Info
from lyrics import MiniLyrics
import logging
import urllib
import thread
import time
import dbus
import os

logging.basicConfig(filename="log.txt", filemode="w", level=logging.DEBUG)

class GUI(object):
    def __init__(self, master):
        # root
        self.master = master
        # control variables
        self.control_var = False         # set False is song changed
        self.lyrics_avail = True         # set true if lyrics is avail
        # general needed vars
        self.lyrics = ""
        self.lyrics_tags = ""
        self.current_song = ""
        self.tags_dict = ""
        self.ordered_tags_dict = ""
        # method calling
        self.master.title("Lyrics Player")
        self.master.geometry("500x300")
        self.init_gui()
        thread.start_new_thread(self.thread_handler, ())

    def init_gui(self):
        # lyrics_frame displays lyrics
        self.lyrics_frame = Frame(self.master)
        self.lyrics_text = Text(self.lyrics_frame, bg="yellow", height=2, width=45, state="disabled", yscrollcommand=self.scrollbar.set)
        self.scrollbar = Scrollbar(self.lyrics_frame)
        self.lyrics_frame.pack(expand=1, fill=BOTH)
        self.lyrics_text.pack(expand=1, fill=BOTH)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        # other attributes
        self.song_title_label = Label(self.master, text="song title", font=('Ubuntu-Mono',12))
        self.song_singer_label = Label(self.master, text="singer here")
        self.elapsed_time_label = Label(self.master, text="[00:00]")
        self.song_singer_label.pack(anchor=W)
        self.song_title_label.pack(anchor=W)
        self.elapsed_time_label.pack(anchor=W)
        

    def reset_gui(self):
        self.lyrics_text.delete("1.0", END)
        self.song_title_label["text"] = ""
        self.song_singer_label["text"] = ""
        self.elapsed_time_label["text"] = ""

    def display_msg(self, msg):
        # logging.debug(self.lyrics_text.get("1.0", END))
        if self.lyrics_text.get("1.0", END) in ["banshee not running\n", "banshee paused\n", "banshee idle\n"]:
            self.control_var = False
        else:
            self.lyrics_text["state"] = "normal"
            self.lyrics_text.delete("1.0", END)
            self.lyrics_text.insert("1.0",msg)
            self.lyrics_text.tag_add("firstline", "1.0", "2.0")
            self.lyrics_text.tag_configure("firstline", foreground="blue", font=("Ubuntu-Mono", 15, "bold"))
            self.lyrics_text["state"] = "disabled"

    def thread_handler(self):
        now = time.time()
        while True:
            self.banshee_controller()
            time.sleep(0.03)
            

    def banshee_controller(self):
        """ checks for status for banshee every second """
        # status checks
        self.status = "playing"
        b_obj = Banshee_Info()
        try:
            self.status = str(b_obj.get_state())
        except AttributeError, e:
            self.status = "not running"      # banshee not running
        except dbus.exceptions.DBusException, e:
            self.status = "not running"
        if self.status == "not running":
            self.display_msg("banshee not running")
        if self.status == "paused":
            self.display_msg("banshee paused")
        if self.status == "idle":
            self.display_msg("banshee idle")
        if self.status == "playing":
            # if banshee is playing songs
            song_path = urllib.unquote(str(b_obj.get_uri()))[7:]
            song_artist = b_obj.get_author()
            song_title = b_obj.get_title()
            pos_in_sec = float((b_obj.banshee.GetPosition()/100)/10.0)
            custom_position = b_obj.get_custom_position()
            self.song_title_label["text"] = song_title
            self.song_singer_label["text"] = song_artist
            self.elapsed_time_label["text"] = "[%s]" %custom_position
            # set control_var 
            if self.current_song != song_title:
                self.control_var = False
            # display_lyrics on screen
            self.display_lyrics(song_path, song_artist, song_title, pos_in_sec, custom_position)

    def load_lyrics(self, lrc_path):
        with open(lrc_path) as fh:
            lrc_data = fh.read()
            lyrics, tags = parse_lrc(lrc_data)
            return (lyrics, tags)

    def display_lyrics(self, song_path, song_artist, song_title, pos_in_sec, custom_position):
        if self.control_var == False:
            if os.path.exists(song_path+".lrc"):
                self.lyrics, self.lyrics_tags = self.load_lyrics(song_path+".lrc")
                if self.lyrics_tags != None:
                    # set lyrics_avail true it shows lyrics is available
                    self.lyrics_avail = True
                else:
                    self.display_msg("Lyrics Not available")
                    self.lyrics_avail = False
            else:
                try:
                    self.display_msg("downloading lyrics...")
                    urllib.urlopen("http://www.google.com")
                except IOError:
                    self.display_msg("internet not working can't download lyrics")
                    self.lyrics_avail = False
                else:
                    try:
                        self.display_msg("downloading lyrics...")   
                        lyrics_dict = MiniLyrics(song_artist, song_title)
                        urllib.urlretrieve(lyrics_dict[0]["url"], song_path+".lrc")
                    except KeyError:
                        self.display_msg("can't download lyrics")
                        self.lyrics_avail = False
                    else:
                        self.lyrics, self.lyrics_tags = self.load_lyrics(song_path+".lrc")
                        if self.lyrics_tags != None:
                            self.lyrics_avail = True
                        else:
                            self.display_msg("lyrics not available")
                            self.lyrics_avail = False
            # set current_song to song_title
            # set control_var to true
            # due to this, this block run only one time
            self.current_song = song_title
            self.control_var = True
            if self.lyrics_avail == True:
                self.lyrics_text["state"] = "normal"
                self.lyrics_text.delete("1.0", END)
                self.lyrics_text.insert("1.0", self.lyrics)
                self.lyrics_text["state"] = "disabled"
                self.tags_dict = {x[0]:x[1] for x in self.lyrics_tags}
                self.ordered_tags_dict = {}
                count = 1
                for x in sorted(self.tags_dict):
                    self.ordered_tags_dict[x] = [self.tags_dict[x], count]
                    count += 1
        elif self.lyrics_avail == True:
            if self.tags_dict.has_key(pos_in_sec):
                lyrics_line = self.ordered_tags_dict[pos_in_sec][1]
                # manipulating lyrics display gui
                self.lyrics_text["state"] = "normal"
                self.lyrics_text.tag_add("sync", "%d.0" %lyrics_line, "%d.0" %(lyrics_line+1))
                self.lyrics_text.tag_config("sync", foreground="red")
                self.lyrics_text.see("%d.0" %(lyrics_line+8))
                self.lyrics_text["state"] = "disabled"
                # debug logs
                # logging.debug('start')
                # logging.debug('len lyrics: %s' %(len(self.lyrics.split('\n'))))
                # logging.debug('len: %s' %len(self.tags_dict))
                # logging.debug('current_line: %s' %lyrics_line)
                # logging.debug('lyrics: %s' %self.tags_dict[pos_in_sec])
                # logging.debug('ordered lyrics: %s' %self.ordered_tags_dict[pos_in_sec][0])
                # logging.debug('exit')
                # pickle.dump(self.ordered_tags_dict, open("self.tags_dict.p", "wb"))



root = Tk()
gui_obj = GUI(root)
root.wm_attributes("-topmost", 1)
root.mainloop()
