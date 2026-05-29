from ultralytics import YOLO
from time import sleep
import paramiko
from paramiko import SSHClient


model = YOLO("flame/runs/detect/flame-1/weights/best.pt")


source_rtsp = "rtsp://172.20.10.11:8554/cam"  


results = model(source_rtsp, stream=True, show=True, conf=0.55) 


for result in results:
    if len(result.boxes.conf) > 0: 
        client = SSHClient()
        client.load_system_host_keys()
        client.connect("raspberrypi.local", port=22, username="pi", password="12345678")
        stdin, stdout, stderr = client.exec_command('python3 trigger_on.py')
        print("Sendt")
        client.close()
        break
