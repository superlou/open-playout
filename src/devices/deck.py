import gi
import sys
from device import Device
from observable_variable import ObservableVariable
#from control_panels.dsk_control_panel import DskControlPanel

try:
    gi.require_version('Gst', '1.0')
except ValueError:
    print 'Could not find required Gstreamer library'
    sys.exit(1)

from gi.repository import Gst


class Deck(Device):
    suggested_name = "deck"
    suggested_readable_name = "Deck"

    def __init__(self, name):
        Device.__init__(self, name)
        #self.ControlPanelClass = DeckControlPanel

        self.file_uri = ObservableVariable()
        self.file_uri.changed.connect(self.file_uri_changed)

        self.default_video = self.add_element('videotestsrc')
        self.default_video.set_property('pattern', 2)
        self.video_selector = self.add_element('input-selector')
        self.default_video.link(self.video_selector)

        self.default_audio = self.add_element('audiotestsrc')
        self.default_audio.set_property('wave', 4)
        self.audio_selector = self.add_element('input-selector')
        caps = Gst.caps_from_string(self.DEFAULT_AUDIO_CAPS)
        self.default_audio.link_filtered(self.audio_selector, caps)

        self.add_output_video_port_on(self.video_selector, 'src', 'video_out')
        self.add_output_audio_port_on(self.audio_selector, 'src', 'audio_out')

    def file_uri_changed(self, file_uri):
        self.rack_video(file_uri)

    def rack_video(self, file_uri):
        print "Racking:", file_uri

        self.decodebin = self.add_element('uridecodebin')
        self.decodebin.connect("pad-added", self.on_new_decoded_pad)
        self.decodebin.connect("no-more-pads", self.on_no_more_pads)
        self.decodebin.connect("drained", self.on_drained)

        self.decodebin.set_property('uri', file_uri)

        self.video_convert = self.add_element('videoconvert')
        self.video_scale = self.add_element('videoscale')
        self.video_rate = self.add_element('videorate')
        self.link_series(self.video_convert, self.video_scale, self.video_rate,
                         self.video_selector)

        self.audio_convert = self.add_element('audioconvert')
        self.audio_rate = self.add_element('audiorate')
        self.link_series(self.audio_convert, self.audio_rate,
                         self.audio_selector)

    def unrack_video(self):
        elements = [self.decodebin, self.video_convert, self.video_scale,
                    self.video_rate, self.audio_convert, self.audio_rate]

        for element in elements:
            element.set_state(Gst.State.NULL)

    def on_new_decoded_pad(self, decodebin, pad):
        caps_string = pad.get_current_caps().to_string()

        print "New pad:", caps_string

        if "video/x-raw" in caps_string:
            pad.link(self.video_convert.get_static_pad("sink"))

        if "audio/x-raw" in caps_string:
            # Need to set conversion elements to NULL and back, otherwise
            # caps aren't always fixed
            self.audio_convert.set_state(Gst.State.NULL)
            self.audio_rate.set_state(Gst.State.NULL)

            pad.link(self.audio_convert.get_static_pad("sink"))

            self.audio_convert.set_state(Gst.State.PLAYING)
            self.audio_rate.set_state(Gst.State.PLAYING)

    def on_no_more_pads(self, decodebin):
        print "Uridecodebin done adding pads"
        self.select_file_video()

    def on_drained(self, decodebin):
        print "Decodebin drained!"
        self.select_default_video()
        self.unrack_video()

    def select_default_video(self):
        pad = self.video_selector.get_static_pad('sink_0')
        self.video_selector.set_property('active-pad', pad)

        pad = self.audio_selector.get_static_pad('sink_0')
        self.audio_selector.set_property('active-pad', pad)

    def select_file_video(self):
        pad = self.video_selector.get_static_pad('sink_1')
        self.video_selector.set_property('active-pad', pad)

        pad = self.audio_selector.get_static_pad('sink_1')
        self.audio_selector.set_property('active-pad', pad)
