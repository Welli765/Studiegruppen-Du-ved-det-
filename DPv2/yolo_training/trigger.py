from ultralytics import YOLO

# Load a pretrained YOLO26n model
model = YOLO("runs/detect/flame-3/weights/best.pt")

# Single stream with batch-size 1 inference
source_rtsp = "rtsp://192.168.50.62:8554/cam"  # RTSP, RTMP, TCP, or IP streaming address

# Run inference on the source
results = model(source_rtsp, stream=True)  # generator of Results objects

#print(results)


# Start tracking objects in a video
# You can also use live video streams or webcam input
#model.track(source=source_rtsp)

for r in results:
    print(r.boxes)