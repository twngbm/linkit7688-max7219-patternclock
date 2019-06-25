# linkit7688-max7219-patternclock

  ## Introduction

  This is a pattern clock project for **MEDIATEK Linkit 7688 duo** and four **MAX7219 8*8 LED Matrix**.

It can read a specificy format of .json named as **Schedule.json** and turn into pattern show on specificy MAX7219.

  Current support five events: **Medicine, Exercise, Wakeup, Hand, Eat.**

  For example:

  You can set up events **Medicine** and **Eat** at 18:00, The two patterns will show up at first MAX7219 from 17:00 to 18:00 in turn.

  A event which contain **Exercise** and **Hand** at 18:15 will draw the patterns to the second MAX7219 from 17:15 to 18:15 in turn.

This project is a practice of Linkit7688 duo and max7219, any suggests and criticisms are welcome.

## Source Tree

**Schedule.json** : json file for **main.py** to read and analysis, it can be properly generated from **gui.py** or **dist/gui.exe**.

   **gui.py** : A python script which use to generate **Schedule.json** with a GUI.

**main.py** : Main python script which work is to analysis **Schedule.json** and send single to **sketch/sketch_main.ino**.

**main_emu.py** : Simulator of **main.py** ,since **main.py** use serial and most computer don't have. Copy of **main.py** and change every serial IO to print.

  **reset.sh** : Shell script for Linkit7688, use to handle update of **Schedule.json** from USB.

**sketch_main/sketch_main.ino** : Arduino script for Linkit7688, use to receive single from **main.py** and draw pattern to specificy MAX7219.

**dist/gui.exe** : Binary form of **gui.py**, generate from **gui.py**.

## Requirement

HardWare:

  **MEDIATEK Linkit 7688 duo**, four **MAX7219 8*8 LED Matrix**

SoftWare:

  Python 2.7 : **main.py**

  Python 3.6 or up: **gui.py**, **main_emu.py**

  [PyQt5](https://pypi.org/project/PyQt5/) and [pyinstaller](https://www.pyinstaller.org/)(recommend) : **gui.py**

Both can be installed by pip.

  Arduino IDE: **sketch_main/sketch_main.ino**



**MEDIATEK Linkit 7688 duo require a network connection everytime it bootup to adjust OS time by ntpd.**

## Setup and Usage

### Linkit 7688 duo Install

1. [Set up Linkit 7688 duo.](https://docs.labs.mediatek.com/resource/linkit-smart-7688/en/get-started/get-started-with-the-linkit-smart-7688-duo-development-board)

2. Load **sketch_main/sketch_main.ino** into Linkit 7688 duo with Arduino IDE.

3. Copy **main.py** , **Schedule.json** , **reset.sh** into Linkit 7688 duo board flash **/root/** , by using scp or win-scp.

4. Change **reset.sh** and **main.py** to executable.

```
chmod +x reset.sh
chmod +x main.py
```

5. Login to Openwrt Web Panel, go to System tab and Startup subtab, at the buttom of the page, Local Startup section, add the following command:

```
sleep 60
ntpd -q -p ptbtime1.ptb.de
sleep 10
cd /root/ && python /root/main.py & ./root/reset.sh
```
before exit 0, than Submit.

5. Link up the hardwire for MAX7219, pins are defined in **sketch_main/sketch_main.ino**

  6. Reboot and everything should be ready.

### Usage

1. Plug the power into board and wait for bootup. At **every** bootup, you should **wait at least 2 minutes** to make system ready, for usb plugin plugout event. See the below section **Bootup Flow** for more bootup detail.

2. Pattern will start showing depend on current exist **Schedule.json** file on the board. About 2 minutes after you plug in the power cable.

### How to modify the Schedule.json

  1. Run **gui.py** or **gui.exe** .

  2. Open a exist **Schedule.json**  to edit or just start adding event.

  3. After finishing editing, click "Save" to save file, if an empty table is saved, an empty item will be automatically generate at time 
1:00 with empty event.
```
{"0":{"hour":1,"minute":0,"events":"11000200000"}}
```

4. Copy **Schedule.json** into a usb device with format **FAT32**. **File name** ***MUST be Schedule.json*** and ***MUST at the root folder***.

5. **Make Sure that Linkit 7688 bootup is ready(By seeing the pattern start changing or just wait at least two minutes.)** Plug the USB device into Linkit 7688, after about 7~10 seconds, plug out the usb decice.(You can see the pattern stop changing, then you can plug out the USB device.) The file have been automatically copy from USB to board at **/root/**

6. After plug out the USB device, new schedule should take effect within a second.

### Error Handling

#### 1. Strange, Broken Pattern

Reason: Unstable MAX7219 wire connection.
Fix: Replug the MAX7219 wire, if the problem still exist, do a reboot.

#### 2. Event wake up on wrong time; Event don;t wake up at the time set.

##### Situtation 1: Serial output with right pattern, but MAX7219 doesn't work

Reason: Unstable MAX7219 wire connection.

Fix: Replug the MAX7219 wire, if the problem still exist, do a reboot.

##### Situtation 2: Serial output wrong pattern.

Reason might be:

1. Old **Schedule.json** still on the board.

2. System time is wrong.

Fix: 

1. You ***MUST*** wait at least ***2 minutes*** for system to boot up from **Cold boot**, means you boot the board up from plugin USB power cable, then system can properly handle USB plugin event. And make sure you'v wait until the file have been copy from USB to board by seeing pattern stop changing or wait for at least ***10 seconds***.

2. This Board ***MUST*** work with WiFi connection to Internet, for board need to re-sync timeing with Internet since it didn't come with a battery. Above section **Linkit 7688 duo Install** Step 5 give **ntpd** server (time sync server) a 60 seconds windows to wait for WiFi connection ,and another 10 seconds windows for ntpd to take effect. Above command failed if no Wifi connection or WiFi connection establish after 60 seconds windows. Than **main.py** will get a wrong timing from system, and generate a wrong timing dictionary, futher cause the wrong pattern. Make Sure Linkit 7688 had setup and linked to a stable WiFi signal. And Make Sure to reconnect to new WiFi if the old one is unreachable.

##### Situtation 3: I'v make sure that every step is correct, but file still can't automatically copy from USB to board.

Reason might be:

1. **reset.sh** didn't come up while board bootup.

2. You plug the USB on the wrong port.

Fix:

1. To check if **reset.sh** come up while board bootup, you will need to **ssh** into board and check current running process with command **ps** or **top**. After the boot up finished (2 minutes) , you should be able to see a process with command **sleep 1** ,then **reset.sh** work fine. If you don't see one, this might be the **reset.sh** isn't **executable**. Make sure you had done Step 4 at **Linkit 7688 duo Install**.

2. Linkit 7688 have two micro USB port, one for power supply and MCU control, and another for USB connection for Linux Kernel. In this case, you'll just neet to swap two cable to another port.

### Bootup Flow

1. Plug USB power cable into Linkit 7688 duo **PWR/MCU** port.

2. Board Bootup will take about 30 seconds, with orange light on.

3. After bootup, board will try to connect to a known WiFi automatically. This will take up about 20 seconds, with orange light flash every two seconds,
depend on the situtation of the WiFi network.

4. During the Wifi trying to connect, a 60 seconds sleep command is shoted, to ensure the WiFi had been connected.
After 60 secoonds, a network time sync command will be shoted, and adjust the os timing.

5. Once the network time sync command was shoted, a 10 seconds sleep are called, to make sure that timing adjust had done before the 
python shell script is called.

5. After that, **main.py** will be executed, and MAX7219 should start working.


### Generate gui.exe (Recommend)

After modifying the **gui.py** and if you want to create a executable file without the dependence of the python enviromen,you can use pyinstaller to pack the python script to a stand alone executable file.

1. [Install pyinstaller.](https://www.pyinstaller.org/)

2. type the following command at powershell, -F means single file and -w means windows application.

```
pyinstaller -F -w --icon=icon.ico gui.py
```

3. After the building is finished, the exe file will be place at **/dist/gui.exe**.
