import subprocess
import time 
#Watchdog API - https://pythonhosted.org/watchdog/
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import get_config

CONFIG = get_config()
PATH_DIR = CONFIG["filePath"]["local"]["test_dir"]

class ExampleHandler(FileSystemEventHandler):
    def on_created(self, event): # when file is created
        # do something, eg. call your function to process the image
        if event.src_path[-5:] == '.html' or event.src_path[-4:] == '.htm':
            print("Got event for file %s" % event.src_path) 
            run_color = subprocess.run(["python3", "color_check.py"], capture_output=True, text=True)
            print(run_color.stdout)

observer = Observer()
event_handler = ExampleHandler() # create event handler
# set observer to use created handler in directory
observer.schedule(event_handler, path=f'{PATH_DIR}')
observer.start()

# sleep until keyboard interrupt, then stop + rejoin the observer
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()