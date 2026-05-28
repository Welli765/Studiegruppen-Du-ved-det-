from ultralytics import YOLO
from time import sleep
import paramiko
from paramiko import SSHClient

# Load a pretrained YOLO26n model
model = YOLO("flame/runs/detect/flame-1/weights/best.pt")

# Single stream with batch-size 1 inference
source_rtsp = "rtsp://172.20.10.11:8554/cam"  # RTSP, RTMP, TCP, or IP streaming address

# Run batched inference on a list of images
results = model(source_rtsp, stream=True, show=True, conf=0.55)  # return a generator of Results objects

# Process results generator
for result in results:
    if len(result.boxes.conf) > 0: #Tjekker om confidence valuen stiger. Så snart detecter en flamme bliver den triggered.
        client = SSHClient()
        client.load_system_host_keys()
        client.connect("raspberrypi.local", port=22, username="pi", password="12345678")
        stdin, stdout, stderr = client.exec_command('python3 trigger_on.py')
        print("Sendt")
        client.close()
        break
