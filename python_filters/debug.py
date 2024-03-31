import hailo
import numpy as np
import time
# Importing VideoFrame before importing GST is must
from gsthailo import VideoFrame
from gi.repository import Gst

def add_mask(video_frame: VideoFrame):
    
    mask_bbox = hailo.HailoBBox(xmin=0.05, ymin=0.45, width=0.9, height=0.52)
    mask_tile = hailo.HailoTileROI(mask_bbox, 1, 0.0, 0.0, 0, hailo.SINGLE_SCALE)
    video_frame.roi.add_object(mask_tile)
    
    return Gst.FlowReturn.OK

def run(video_frame: VideoFrame):
    import ipdb; ipdb.set_trace()
    # shape = [640, 640]
    # success, map_info = gst_buff.map(Gst.MapFlags.READ)
    # frame = np.ndarray(
    #     shape=shape,
    #     dtype=np.uint8,
    #     buffer=map_info.data)
    
    dets = hailo.get_hailo_detections(video_frame.roi)
    for det in dets:
        label = det.get_label()
        bbox = det.get_bbox()
        confidence = det.get_confidence()
        print(f"Label: {label}, Bbox: {bbox}, Confidence: {confidence}")
    # gst_buff.unmap(map_info)
    return Gst.FlowReturn.OK

def delay(video_frame: VideoFrame):
    # import ipdb; ipdb.set_trace()
    time.sleep(0.2)
    return Gst.FlowReturn.OK
