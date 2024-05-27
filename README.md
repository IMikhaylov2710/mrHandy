This is a script for hand recognition using webcam

Installation:

1) git clone
2) cd into folder
3) run pip install requirements.txt

Running script:

1) run python face.py
2) you could run face.py --help if you want to use arguments
3) to exit cam press "q"

How to use?
By default this script has two modes: recognition and master mode. To switch between mods you should show open palm to the camera for 20 frames (by default). After switching mode the script will notify you. After you enter master mode the programm will automatically monitor the following parts of the palm: tip of each finger and coordinate for every knuckle.

By default this script recogizes two hands

Whats new?
1) added gesture recognition
2) added lagging (several frames with no gesture recognized will be omitted for better recognition performance, number of frames could be changed with arguments, see --help for convenience)
2) started beta of gesture logic 
3) added argparse for better interaction with the script
