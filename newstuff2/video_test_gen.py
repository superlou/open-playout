import gi
import sys
from device import Device

try:
    gi.require_version('Gst', '1.0')
except ValueError:
    print 'Could not find required Gstreamer library'
    sys.exit(1)

from gi.repository import Gst


class VideoTestGen(Device):
    def __init__(self, name, pattern=0):
        Device.__init__(self, name)

        self.src = Gst.ElementFactory.make('videotestsrc', None)
        self.bin.add(self.src)
        self.src.set_property('pattern', pattern)

        self.convert = Gst.ElementFactory.make('videoconvert', None)
        self.bin.add(self.convert)

        self.text_overlay = Gst.ElementFactory.make('textoverlay', None)
        self.bin.add(self.text_overlay)
        self.text_overlay.set_property("text", self.name)
        self.text_overlay.set_property("shaded-background", True)

        self.caps_filter = Gst.ElementFactory.make('capsfilter', None)
        self.bin.add(self.caps_filter)

        caps = Gst.caps_from_string("video/x-raw,format=I420,width=320,height=240")
        self.caps_filter.set_property('caps', caps)

        self.src.link(self.text_overlay)
        self.text_overlay.link(self.convert)
        self.convert.link(self.caps_filter)

        self.add_output_port_on(self.caps_filter, "src")
