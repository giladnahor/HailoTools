import hailo
import time
# Importing VideoFrame before importing GST is must
from gsthailo import VideoFrame
from gi.repository import Gst

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def run(video_frame: VideoFrame):
    # scale the bbox to fit original aspect ratio
    # the original aspect ratio is 16:9
    # the inferred image aspect ratio is 1:1 with borders on the top and bottom
    #|----------------------|
    #|    (black border     |
    #|                      |
    #|------top_border------|
    #|                      |
    #|     scaled image     |
    #|                      |
    #|----bottom_border-----|
    #|                      |
    #|    (black border     |
    #|----------------------|    
    bottom_border = (1-9/16)/2
    top_border = 1 - bottom_border
    detections = video_frame.roi.get_objects_typed(hailo.HAILO_DETECTION)
    for detection in detections:
        bbox = detection.get_bbox()
        ymin = map(bbox.ymin(), bottom_border, top_border, 0, 1)
        ymax = map(bbox.ymax(), bottom_border, top_border, 0, 1)
        height = ymax - ymin
        new_bbox = hailo.HailoBBox(bbox.xmin(), ymin, bbox.width(), height)
        detection.set_bbox(new_bbox)
    return Gst.FlowReturn.OK
