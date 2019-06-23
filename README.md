# linkit7688-max7219-patternclock

  ## Introduction

  This is a pattern clock project for **MEDIATEK Linkit 7688 duo** and four MAX7219.

  It can read a specificy format of .json named as Schedule.json and turn into pattern show on specificy MAX7219.

  Current support five events: **Medicine, Exercise, Wakeup, Hand, Eat.**

  For example:

  You can set up events **Medicine** and **Eat** at 18:00, The two patterns will show up at first MAX7219 from 17:00 to 18:00 in turn.

  A event which contain **Exercise** and **Hand** at 18:15 will draw the patterns to the second MAX7219 from 17:15 to 18:15 in turn.

  This project is just a practice of Linkit7688 duo and max7219, any suggestions are welcome.

## Source Tree

   **Schedule.json** : json file for **main.py** to read and analysis, it can be properly generated from **gui.py** or **dist/gui.exe**

   **gui.py** : A python script which use to generate **Schedule.json** with a GUI.

  **main.py** : Main python script which work is to analysis **Schedule.json** and send single to **sketch/sketch_main.ino**

  **main_emu.py** : Simulator of **main.py** ,since **main.py** use serial and most computer don't have. Copy of **main.py** and change every serial IO to print

  **reset.sh** : Shell script for Linkit7688, use to handle update of **Schedule.json** from USB.

  **sketch_main/sketch_main.ino** : Arduino script for Linkit7688, use to receive single from **main.py** and draw pattern to specificy MAX7219

  **dist/gui.exe** : Binary form of **gui.py**, generate from **gui.py**

## Requirement

HardWare:

  **MEDIATEK Linkit 7688 duo**, four **MAX7219**

SoftWare:

  Python 2.7 : **main.py**

  Python 3.6 or up: **gui.py**, **main_emu.py**

  [PyQt5](https://pypi.org/project/PyQt5/) and [pyinstaller](https://www.pyinstaller.org/)(recommend) : **gui.py**

  Both can be installed by pip

  Arduino IDE: **sketch_main/sketch_main.ino**



**MEDIATEK Linkit 7688 duo require a network connection everytime it bootup to adjust OS time by ntpd.**

## Setup and Usage

### Linkit 7688 duo Install

  1. [Set up Linkit 7688 duo](https://docs.labs.mediatek.com/resource/linkit-smart-7688/en/get-started/get-started-with-the-linkit-smart-7688-duo-development-board)

  2. Load **sketch_main/sketch_main.ino** into Linkit 7688 duo with Arduino IDE

  3. Copy **main.py** , **Schedule.json** , **reset.sh** into Linkit 7688 duo board flash /root/ , by using scp or win-scp.

  4. Login to Openwrt Web Panel, go to System tab and Startup subtab, then add the following command:

```
sleep 60
ntpd -q -p ptbtime1.ptb.de
sleep 10
cd /root/ && python /root/main.py & ./root/reset.sh
```

  5. Set up the hardwire for MAX7219, pins are defined in **sketch_main/sketch_main.ino**

  6. Reboot and everything should be ready.

### Bootup Flow

  1. Plug USB power cable into Linkit 7688 duo.

  2. Board Bootup will take about 30 seconds, with orange light on.

  3. After bootup, board will try to connect to known wifi automatically. This will take up about 20 seconds, with orange light flash every two second,depend on the situtation of the wifi network.

  4. During the wifi trying to connect, a 60 seconds sleep are shoted, to ensure the wifi have been connected.
After 60 secoond, a network time sync command will be shoted, and adjust the os timing.

  5. Once the network time sync command are shoted, a 10 seconds  sleep are called, to make sure that timing adjust are done before the 
python shell script are called.

  6. After that, **main.py** will be executed, and MAX7219 should start working.

### Usage

  1. Plug the power into board and wait for bootup

  2. Pattern will start showing depend on **Schedule.json** file. About 100 seconds after you plug in the power cable.

### How to modify the Schedule.json

  1. Run **gui.py** or **gui.exe** .

  2. Open a exist **Schedule.json**  to edit or just start adding event.

  3. After finishing editing, click "Save" to save file, if an empty table is saved, an empty item will be automatically generate at time 
1:00 with empty event.
```
{"0":{"hour":1,"minute":0,"events":"11000200000"}}
```

  4. Copy Schedule.json into a usb device with format FAT32.**File name** ***MUST be Schedule.json*** and ***MUST at the root folder***

  5. Plug the usb device into Linkit 7688, after about 7~10 seconds, plug out the usb decice.(You can see the pattern stop changing, then you can plug out the USB device)

  6. After plug out the USB device, Linkit 7688 will go into a reboot.

  7. From plug out to new schedule pattern to take effect will take about 100 seconds.

### Generate gui.exe

  After modifying the gui.py and if you want to create a executable file without the dependence of the python enviromen,you can use pyinstaller to pack the python script to a stand alone executable file.

  1. [Install pyinstaller](https://www.pyinstaller.org/)

  2. type the flowing command, -F means single file and -w means windows application

```
pyinstaller -F -w --icon=icon.ico gui.py
```

  3. After the buildup finished, the exe file will be place at /dist/gui.exe
