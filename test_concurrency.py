import subprocess
import time

# Launch two client processes almost simultaneously
p1 = subprocess.Popen(["python", "client.py"])
time.sleep(0.5)  # tiny stagger so logs are readable, but both overlap
p2 = subprocess.Popen(["python", "client.py"])

p1.wait()
p2.wait()