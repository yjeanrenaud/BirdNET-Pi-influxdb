# BirdNET-Pi-influxdb
Integrate your BirdNET-Pi data into influxDB

## why and what
I run a small OrangePi Zero 2 with [BirdNET-Pi](https://github.com/mcguirepr89/BirdNET-Pi) to collect the birds' voices from my balcony. This works quite neat (I'll publish a how-to later).
Now I wanted to collect the data about the birds the local tensor flow network on that small machine finds not only on the machine itsself but also at my InfluxDB server.
Fortuntely, BirdNET-Pi supports [apprise](https://github.com/caronc/apprise/), which can do quite a few cool tricks! Unfortunatelly, neither FORM nor JSON or XML work as custom notification scemes somehow under BirdNET-Pi. I did not wanted to dig into this, so I needed a way that transmits the measured data in a usable form.
 MQTT does, so I used that. Again, unfortunatelly it is not quite possible to get BirdNET-Pi to send out properly formated JSON messages, so I wrote a little middleware.
## prerequsites and dependencies
- you need [BirdNET-Pi](https://github.com/mcguirepr89/BirdNET-Pi) up and running.
- you need a running [InfluxDB Server](https://github.com/influxdata/influxdb ). I run mine in a docker. InfluxDB is quite hefty, so you won't be running it on a RaspberryPi eventually.
- create a new bucket, e.g. called `birdnet`
- I use the [telegraf agent](https://github.com/influxdata/telegraf) to send various data to the InfluxDB server, e.g. from IoT devices. Hence, you need an API token of your InfluxDB socket
- you need a MQTT Broker. e.g. [Mosquitto](https://github.com/eclipse-mosquitto/mosquitto). It works pretty straight forward and could run out of the box. I added credentials only for birdnet
- python3: `sudo apt-get update;sudo apt-get install python3`
- python paho-mqtt: `pip install paho-mqtt` or `apt-get install python3-paho-mqtt`
- python json: `pip install json` or `apt-get install python3-json`
## setup
- with your mosquitto MQTT broker credentials, your InfluxDB Token, set up your `telegraf.conf` as outlined [here](https://github.com/yjeanrenaud/BirdNET-Pi-influxdb/blob/main/telegraf.conf).
- set up your credentials in [mqtt_json.py](https://github.com/yjeanrenaud/BirdNET-Pi-influxdb/blob/main/mqtt_json.py) and store it in a safe place, e.g. your home dir.
- run `mqtt_json.py` continiously, e. g. via *cronjob* and *screen*: `@reboot /usr/bin/screen -dmS mqtt_json /usr/bin/env python3 /full/path/to/mqtt-json.py`
- set up your [BirdNet-Pi](https://github.com/mcguirepr89/BirdNET-Pi):
  - Under *Tools*/*Settings*, you enter an **Apprise Notifications Configuration:** e.g. `mqtt://username:password@MQTT-BROKER-IP:1883/birdnet/bird`.
  - you need to enter a **Notification Title:**, e.g. `New BirdNET-Pi Detection` (BirdNET-Pi insists on a notification title, as apprise asks for it, but it does not really matter for now. It is helpful if you use other apprise hannels like signal or threema besides mqtt for BirdNET-Pi. You may leave it to default)
  - Enter your **Notification Body:**, e.g. `$flickrimage A $comname ($sciname) was just detected with a confidence of $confidence. VALUES: comname=$comname,sciname=$sciname,confidence=$confidence,date=$date,time=$time,week=$week`. The important part is `comname=$comname,sciname=$sciname,confidence=$confidence,date=$date,time=$time,week=$week` beacuse all the rest gets ignored by the parser middleware we deployed. I left the default message so it is nicer to read in a messenger like Threema.
## todo
- secure the code
