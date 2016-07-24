#!/usr/bin/env python
import os
import sys
import argparse
import gi
from gi.repository import GObject
import shlex
from threading import Thread

import editor
from station import Station
from devices.monitor import Monitor
from devices.camera import Camera
from devices.switcher import Switcher
from devices.video_test_gen import VideoTestGen

os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')


class Main:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--graph',
                            help="Generate graph of pipeline",
                            action='store_true')
        parser.add_argument('-c', '--config',
                            help="Load configuration file")
        parser.add_argument('-d', '--gst-debug', type=int,
                            help="GST debug level")
        self.args = parser.parse_args()

        GObject.threads_init()
        #Gdk.threads_init()

    def run(self):
        app = editor.GuiApp()
        app.start(self.args)

    def terminal(self):
        print "Open-Playout Server"

        self.test_cmd('add videotestgen c1')
        self.test_cmd('add videotestgen v1')
        self.test_cmd('add monitor m1')
        self.test_cmd('add switcher s1 2')

        self.test_cmd('link c1.out s1.in1')
        self.test_cmd('link v1.out s1.in2')
        self.test_cmd('link s1.prog_out m1.in')

        cmd = ""
        while cmd != "exit":
            cmd = raw_input('>>> ')
            self.parse(cmd)

    def parse(self, cmd):
        tokens = shlex.split(cmd)
        first_token = tokens.pop(0)

        # If first argument is a device, assume an action is coming
        device = self.station.find_device_by_name(first_token)
        if device:
            action = tokens.pop(0)
            device.do_action(action, tokens)

        # Generic actions
        if first_token == "add":
            device_type = tokens.pop(0)
            device_name = tokens.pop(0)

            if device_type == 'videotestgen':
                videotestgen = VideoTestGen(device_name)
                self.station.add_device(videotestgen)

            if device_type == 'camera':
                camera = Camera(device_name)
                self.station.add_device(camera)

            if device_type == 'switcher':
                inputs = int(tokens.pop(0))
                switcher = Switcher(device_name, inputs)
                self.station.add_device(switcher)

            if device_type == 'monitor':
                monitor = Monitor(device_name, (320, 240), (0, 0))
                self.station.add_device(monitor)

        if first_token == "remove":
            device_name = tokens.pop(0)
            device = self.station.find_device_by_name(device_name)
            self.station.remove_device(device)

        if first_token == "graph":
            self.station.graph_pipeline()

        if first_token == "link":
            port_1, port_2 = tokens.pop(0), tokens.pop(0)
            name = port_1 + "-" + port_2
            self.station.link(name, port_1, port_2)

        if first_token == "unlink":
            port_1 = tokens.pop(0)
            port_2 = tokens.pop(0)
            self.station.unlink(port_1, port_2)

        if first_token == "exit":
            self.editor.exit()

    def test_cmd(self, cmd):
        print ">>>", cmd
        self.parse(cmd)

if __name__ == "__main__":
    main = Main()
    main.run()
