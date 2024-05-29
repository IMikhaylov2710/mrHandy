This is a script for hand recognition using webcam

Installation:

1) git clone
2) cd into folder
3) run pip install requirements.txt

Running script:

0) this script will ask for access to monitor, mouse control and camera, feel free to give it, it is absolutely safe
1) run python face.py
2) you could run face.py --help if you want to use arguments
3) to exit cam press "q" (make sure you use english keyboard)

How to use?
By default this script has two modes: recognition and master mode. In recognition mode the programm will wait until it sees a gesture to switch to master mode (by default it is open palm) for 20 frames. To switch back to recognition mode you should point your index finger up for 20 frames.

By default switching between modes has a sound notification (could be turned off using --muffle flag)

After you enter master mode the programm will automatically monitor the following parts of the palm:
1) tip of each finger
2) coordinate for every knuckle
3) centroid of your knuckles

In master mode your mouse cursor follows the centroid of your knuckles in absolute coordinates (beta). Currently this program only supports one monitor (two monitors support will be added later).

Whats new?
1) Added mouse control for macOS
2) Added the emulation for mouse left click and mouse release

For compliance or collaboration feel free to contact me at i.mikhailov@omnigene.tech
