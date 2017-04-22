# LCD RESTful
A RESTful service to control output on a Hitachi Character Panel LCD such as a 
HD44780. Example tutorial for wiring and driving the LCD can be found 
[here](https://learn.adafruit.com/character-lcd-with-raspberry-pi-or-beaglebone-black/usage).
To facilitate testing, if not on a RPi (or if --fake passed as CLA), this driver 
will fall back to terminal output.

## Why
Serve out the LCD to middleware or any service, even non-localhost, that can do 
REST. Have a middleware service poll for updates (some dead drop location like 
email or dropbox) and then post the results to the server in order for them to 
show on the LCD exactly how you want them to.

## Wiring
The [old](find-link) Adafruit wiring used different pins. [Here is a 
	picture](https://www.engineersgarage.com/sites/default/files/Lcd_0.jpg) of the 
	LCD pinout. Also poorly drawn here:
```
	GND Vcc Vee RS RW EN DB0 1  2  3  4  5  6  7  Vled GNDled
  1   2   3   4  5  6  7   8  9  10 11 12 13 14 15   16
```

## Install
Coded for Python3, but tested for compatibility with Python2 before releases. If 
you don't want to use Py3, then leave off the `-p` flag and arg below.
Start by creating a virtualenv:
```
mkvirtualenv -p `which python3` lcd
workon lcd
```
Install dependencies. Note: if you are not on a RPi, then the RPi.GPIO install 
will fail, but since you're probably testing you don't care. Also, as of writing 
this, the version of RPLCD on PyPi (0.4.0) is very out of date. It is 
incompatible with this code, and you'll need at least commit 3c3a486. To do this 
you'll want to pip install from a clone of its repo before you pip the 
requirements. This code was tested with
```
git clone https://github.com/dbrgn/RPLCD.git
pip install RPLCD/.
pip install -r <this repo dir>/requirements.txt
pip install <this repo dir>/.
```

### Why not the Adafruit driver?
Because it's bulky and has a few things that made dev difficult. 1) It couldn't 
detect my RPi 0W as an RPi; 2) I had to patch its code to do dependency 
injection (the GPIO instantiation is in the LCD init's param list); 3) injecting 
the code to convert UTF to Hitachi was clunky. For reference, I'm talking about 
[this repo](https://github.com/adafruit/Adafruit_Python_CharLCD.git). If you 
want to use that library, then dig through the git history to find a patch and 
driver to allow you to use the Adafruit library.

## Usage
* Test
	* `./lcd-test.py`
* Run
	* The setup.py tells pip to install an entry point into your virtualenv path
	* `lcd_server`

