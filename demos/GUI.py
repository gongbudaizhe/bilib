#! /usr/bin/env python
# -*- coding: utf-8 -*-
# hello.py
#
# Copyright © 2014 bily <bily.HUST@gmail.com>
#
# distribution is not allowed without author's approval

#import sys
#sys.path.append("") # your library directory

"""

"""

import wx
from multiprocessing import Process,Value,Lock,Event
import pyaudio
import wave
import time
import subprocess
import os
from array import array
from struct import pack
from sys import byteorder

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "DECODE DEMO", size = (500, 500))

        self.panel = wx.Panel(self, -1)
        #bmp = wx.Image("normal.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        #self.button = wx.BitmapButton(panel, -1, bmp, pos=(50,50), size=(50,50))
        self.toggle_button = wx.ToggleButton(self.panel, -1, "Record", 
                                            pos=(170,170),
                                            size=(150,150))
        self.button = wx.Button(self.panel, -1, "Play", pos=(320,300),size=(60,60))

        self.label = wx.StaticText(self.panel, label="", pos=(50,400))

        #self.label.SetForegroundColour('white')
        #self.label.SetBackgroundColour('black')

        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnClick, self.toggle_button)
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.button)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        #self.text = wx.StaticText(self.panel, label="", pos=(10, 400), style = wx.ALIGN_CENTRE)
        #self.label = wx.StaticText()         
        self.event = Event()
        self.event.clear()
        self.record_process = None
        self.Show() 
#        self._pyaudio = pyaudio.PyAudio()
        #self.stream = self._pyaudio.open(format=FORMAT, channels=1, 
                                    #rate=RATE, input=True,output=True,
                                    #frames_per_buffer=CHUNK_SIZE)
        #self.stream.stop_stream()
        #self.sample_width = self._pyaudio.get_sample_size(FORMAT)
    def update(self, event):
        if os.path.exists(".decode_done"):
            #with open("decode/temp/nnet/decode_test/scoring/decode.txt") as f_in:
            with open("decode/result/decode.txt") as f_in:

                line = f_in.readlines()[0].strip()
                result = "".join(line.split(" ")[1:])
                self.label.SetLabel(result)
                self.timer.Stop()

    def OnClose(self, event):
 #       self.stream.close()
 #       self._pyaudio.terminate()
        self.Destroy()
        print "closing..."

    def OnClick(self, event):
        if self.toggle_button.GetValue():
            self.toggle_button.SetLabel("Stop")

            self.event.clear()
            self.record_process = Process(target=self.record)
            self.record_process.start()
        else:
            self.toggle_button.SetLabel("Record")
            self.timer.Start(2000)
            try:
                os.remove(".decode_done") 
            except:
                pass
            self.event.set()
            self.record_process.join()

    def record(self):
#        while True:
            #if self.event.is_set():
                #print "stop..."
                #break
            #print "running..."
#        return
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=1,
                        rate=RATE,
                        input=True)

        stream.start_stream()
        data = array('h')
        print "recording..."
        while 1:
            if not self.event.is_set():
                # keep getting data
                snd_data = array("h", stream.read(CHUNK_SIZE))
                if byteorder == "big":
                    snd_data.byteswap()
                data.extend(snd_data)
            else:
                # stop and store
                print "stop recording..."
                stream.stop_stream()
                stream.close()
                p.terminate()

                data = pack('<' + ('h'*len(data)), *data)

                wf = wave.open('record.wav', 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(FORMAT))

                wf.setframerate(RATE)
                wf.writeframes(data)
                wf.close()
                print "recording done"
                print "decoding..."
                self.decode()
                break

    def decode(self):
        subprocess.call(['./decode.sh','&>> output'])
        touch(".decode_done")
            #self.text.SetLabel("hello china")
            #self.text.SetLabel("".join(line.split(" ")[1:]))

    def play(self):
        wf = wave.open("record.wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK_SIZE)
        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK_SIZE)

        stream.stop_stream()
        stream.close()

        p.terminate()
        #for i in range(10000):
            #print "playing..."
        #self.stream.start_stream()
        #wf = wave.open('record.wav', 'rb')
        #data = wf.readframes(CHUNK_SIZE)
        #while data != "":
            #print "playing..."
            #self.stream.write(data)
            #data = wf.readframes(CHUNK_SIZE)
        #self.stream.stop_stream()
        #print "playing done"

    def OnPlay(self,event):
        Process(target=self.play).start()
  

class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
#import wx

#class ShapedButton(wx.PyControl):
    #def __init__(self, parent, normal, pressed=None, disabled=None):
        #super(ShapedButton, self).__init__(parent, -1, style=wx.BORDER_NONE)
        #self.normal = normal
        #self.pressed = pressed
        #self.disabled = disabled
        #self.region = wx.RegionFromBitmapColour(normal, wx.Color(0, 0, 0, 0))
        #self._clicked = False
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        #self.Bind(wx.EVT_SIZE, self.on_size)
        #self.Bind(wx.EVT_PAINT, self.on_paint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        #self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
        #self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        #self.Bind(wx.EVT_MOTION, self.on_motion)
        #self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
    #def DoGetBestSize(self):
        #return self.normal.GetSize()
    #def Enable(self, *args, **kwargs):
        #super(ShapedButton, self).Enable(*args, **kwargs)
        #self.Refresh()
    #def Disable(self, *args, **kwargs):
        #super(ShapedButton, self).Disable(*args, **kwargs)
        #self.Refresh()
    #def post_event(self):
        #event = wx.CommandEvent()
        #event.SetEventObject(self)
        #event.SetEventType(wx.EVT_BUTTON.typeId)
        #wx.PostEvent(self, event)
    #def on_size(self, event):
        #event.Skip()
        #self.Refresh()
    #def on_paint(self, event):
        #dc = wx.AutoBufferedPaintDC(self)
        #dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        #dc.Clear()
        #bitmap = self.normal
        #if self.clicked:
            #bitmap = self.pressed or bitmap
        #if not self.IsEnabled():
            #bitmap = self.disabled or bitmap
        #dc.DrawBitmap(bitmap, 0, 0)
    #def set_clicked(self, clicked):
        #if clicked != self._clicked:
            #self._clicked = clicked
            #self.Refresh()
    #def get_clicked(self):
        #return self._clicked
    #clicked = property(get_clicked, set_clicked)
    #def on_left_down(self, event):
        #x, y = event.GetPosition()
        #if self.region.Contains(x, y):
            #self.clicked = True
    #def on_left_dclick(self, event):
        #self.on_left_down(event)
    #def on_left_up(self, event):
        #if self.clicked:
            #x, y = event.GetPosition()
            #if self.region.Contains(x, y):
                #self.post_event()
        #self.clicked = False
    #def on_motion(self, event):
        #if self.clicked:
            #x, y = event.GetPosition()
            #if not self.region.Contains(x, y):
                #self.clicked = False
    #def on_leave_window(self, event):
        #self.clicked = False

#def main():
    #def on_button(event):
        #print 'Button was clicked.'
    #app = wx.PySimpleApp()
    #frame = wx.Frame(None, -1, 'Shaped Button Demo')
    #panel = wx.Panel(frame, -1)
    #button = ShapedButton(panel, 
        #wx.Bitmap('normal.png'), 
        #wx.Bitmap('pressed.png')
        #)
    #button.Bind(wx.EVT_BUTTON, on_button)
    #sizer = wx.BoxSizer(wx.VERTICAL)
    #sizer.AddStretchSpacer(1)
    #sizer.Add(button, 0, wx.ALIGN_CENTER)
    #sizer.AddStretchSpacer(1)
    #panel.SetSizer(sizer)
    #frame.Show()
    #app.MainLoop()

#if __name__ == '__main__':
#    main()


#import wx
#import wx.lib.agw.shapedbutton as SB

#class MyFrame(wx.Frame):
    #def __init__(self, parent):
        #wx.Frame.__init__(self, parent, -1, "ShapedButton Demo")
        #self.SetBackgroundColour(wx.WHITE)
        #panel = wx.Panel(self)
    
        ## Create 2 bitmaps for the button
        #upbmp = wx.Bitmap("normal.png", wx.BITMAP_TYPE_PNG)
        #disbmp = wx.Bitmap("pressed.png", wx.BITMAP_TYPE_PNG)

        #play = SB.SBitmapToggleButton(panel, -1, upbmp, (300, 300))
        #play.SetBackgroundColour(wx.WHITE)
        #play.SetUseFocusIndicator(False)
        #play.SetBitmapDisabled(disbmp)

## our normal wxApp-derived class, as usual

#app = wx.App(0)

#frame = MyFrame(None)
#app.SetTopWindow(frame)
#frame.Show()

#app.MainLoop()
