# Dark-Modeify-Me
Auto dark mode tool for emails created by email developers using pyscript.

# Setup and How to Run
Requires python3 to run and requires a server along with a python script running in the background

1. After downloading/cloning the tool go into the directory 
2. Run the monitor_folder python file by typing ```python3 scripts/python/monitor_folder.py``` 
3. This will start monitoring the tests folder under ```dark-modeify-html/file-assets/tests``` and checking for htm/html files 
4. When htm/html files have been added to said folder then script will run and output in the following folders in order  <br>
   a. Under ```dark-modeify-html/file-assets/images``` a snapshot of both dark and light mode of said coded email will appear  <br>
   b. Under ```dark-modeify-html/scripts/python/stouts``` there will be a coords JSON file with coordinates and file naming will be the following 
   (name of html)_coords.json <br>
   c. Under the same folder a colors JSON file with key color values will also be created with colors of said coordinate points with the following 
   naming scheme - (name of html)_colors.json <br>
5. Run a local python server by typing ```python -3 -m http.sever```
6. Copy and visit the url created from the server and run the tool!
