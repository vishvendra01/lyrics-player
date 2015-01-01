#-*- coding: utf-8 -*-
import sys, dbus

class Banshee_Info:
    def __init__(self):
        self.dbus_handler = dbus.SessionBus()
        if self.running():
            self.banshee = self.dbus_handler.get_object("org.bansheeproject.Banshee", "/org/bansheeproject/Banshee/PlayerEngine")

    def __get_track_info(self):
        return self.banshee.GetCurrentTrack()

    def __get_position(self):
        return self.banshee.GetPosition()

    def __get_length(self):
        return self.banshee.GetLength()

    def get_custom_position(self):
        conversion_value = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09"]
        pos_in_secs =  self.__get_position()/100
        secs = pos_in_secs / 10
        minute = secs / 60
        secs = secs % 60
        pulses = pos_in_secs % 10
        if secs < 10:
            secs = conversion_value[secs]
        if minute < 10:
            minute = conversion_value[minute]
        if pulses < 10:
            pulses = conversion_value[pulses]
        return "%s:%s" %(minute, secs)

    def get_title(self):
        return self.__get_track_info().get('name')

    def get_author(self):
        return self.__get_track_info().get('artist')

    def get_album(self):
        return self.__get_track_info().get('album')

    def progress(self):
        return int(round( 100 * ( float( self.__get_position() ) / float( self.__get_length() ))))

    def get_uri(self):
        return self.banshee.GetCurrentUri()

    def get_volume(self):
        return self.banshee.GetVolume()

    def get_length(self):
        m, s = divmod(self.__get_length() / 1000, 60)
        return str(m) + 'm ' + str(s) + 's'

    def running(self):
        if self.dbus_handler.name_has_owner('org.bansheeproject.Banshee'):
            return True

    def get_state(self):
        return self.banshee.GetCurrentState()