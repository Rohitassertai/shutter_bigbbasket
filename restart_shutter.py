import os
import time
import psutil
import datetime

start = datetime.time(0, 0, 0)
end = datetime.time(23, 45, 0)

while True:
    try:
        ds = []
        for proc in psutil.process_iter():
            procc = proc.cmdline()
            # sudo python3 deepstream-intrusion.py uri uri folder_name
            if len(procc) >= 2 and "python3" in procc and "shutter_deploy.py" in procc:
                ds.append(proc.pid)
        # CHECK THE TIME CONDITION HERE
        current = datetime.datetime.now().time()
        if start <= current and current <= end:  # RUN TIME
            print("inside time")
            if len(ds) == 0:  # RUN IF IT IS NOT RUNNING
                print("Running shutter code")
                os.system("sh run_shutter.sh")
                # os.system("/home/assert-arya/scripts/run_intrusion.sh &")
        else:  # CLOSE TIME
            if len(ds) > 0:
                print("Closing shutter code")
                for pid in ds:
                    os.system("sudo kill -15 " + str(pid))
        time.sleep(5)  # CHECK IN EACH 5 SECONDS
    except KeyboardInterrupt:
        break
             
