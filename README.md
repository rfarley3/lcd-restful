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
Coded for Python3, but tested for compatibility with Python2 before releases.

### Virtualenv
This is an optional section, that allows you to isolate this install from your 
system. Update, install virtualenv, and its hooks:

```
sudo apt-get update
sudo pip install --upgrade pip
sudo pip install virtualenvwrapper
echo "export WORKON_HOME=$HOME/.pyvirtualenvs" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
. ~/.bashrc
```

If you are on a Raspberry Pi, then RPi.GPIO is on already on your system, but 
the virtualenv will need to build an isolated copy, to compile you'll need the 
Python headers. If you are not on a RPi, then you can skip this step.

```
sudo apt-get install python-dev  # v2
sudo apt-get install python3-dev  # v3
```

Create and load the virtualenv. If you are using Py3, add a `-p \`which 
python3\`` argument to set the Python binary this virtualenv will point to.

```
mkvirtualenv lcd
workon lcd
```

Now that the virtualenv is activated, any pip installed packages will be 
isolated within it and not affect your system. Installing additional packages or 
hacking the virtualenv will not impact your system Python install. Additionally, 
uninstalling this code and all its dependencies will be as easy as `rmvirtualenv 
lcd`.

### Dependencies
There are two big notes about the dependencies:
* If you are not on a RPi, then the RPi.GPIO install will fail, but since 
you're probably testing you with the fake HW, then you don't care.
* The version of RPLCD on PyPi (0.4.0) is missing features this code depends on, 
you'll need at least commit 3c3a486.

```
pip install RPi.GPIO
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
want to use it, then dig through the git history to find a patch and driver to 
allow you to use this code with the Adafruit library.

## Usage
* Test
	* `./lcd-test.py`
* Run
	* The setup.py tells pip to install an entry point into your virtualenv path
	* `lcd_server`

