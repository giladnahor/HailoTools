# requirements: python3, gstreamer1.0, gst-rtsp-server-1.0
# sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad
# pip install PyGObject
# sudo apt-get install libgstrtspserver-1.0-dev

# Usage: python3 rtsp_video_file_server.py <video-file-path> [<video-file-path> ...]
# The video files will be streamed at rtsp://127.0.0.1:8554/stream1, rtsp://127.0.0.1:8554/stream2, etc. 
# You can use any RTSP client, like VLC, to view the streams
# Gstreamer example:
# gst-launch-1.0 -v rtspsrc location=rtsp://127.0.0.1:8554/stream1 latency=0 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

class VideoFileRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, video_path):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.video_path = video_path

    def do_create_element(self, url):
        src_pipeline = f"filesrc location={self.video_path} ! decodebin ! videoconvert ! videoscale ! x264enc ! rtph264pay name=pay0 pt=96"
        return Gst.parse_launch(src_pipeline)

def main(args):
    if len(args) < 2:
        sys.stderr.write(f"Usage: {args[0]} <video-file-path> [<video-file-path> ...]\n")
        sys.exit(1)

    video_paths = args[1:]

    GObject.threads_init()
    Gst.init(None)

    server = GstRtspServer.RTSPServer()
    server.set_service("8554")

    mount_points = server.get_mount_points()

    for index, video_path in enumerate(video_paths, start=1):
        factory = VideoFileRtspMediaFactory(video_path)
        factory.set_shared(True)
        mount_points.add_factory(f"/stream{index}", factory)
        print(f"RTSP server is streaming {video_path} at rtsp://127.0.0.1:8554/stream{index}")

    server.attach(None)

    loop = GObject.MainLoop()
    loop.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
