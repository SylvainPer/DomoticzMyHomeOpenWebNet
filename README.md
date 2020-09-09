# DomoticzMyHomeOpenWebNet
Domoticz plugin for MyHome Zigbee devices

This plugin allows to control your wireless MyHome lights in Domoticz.
It uses an OpenWebNet frames on a modified zigbee protocol.

The plugin starts by joining and scanning the network.
All the devices must join the same network as the USB key (controller).
The Micromodules are added to domoticz automatically after the network scan.
A general push button allows to switch off all the devices.
The remote orders are not sent on the network, the learning create a direct link.
Each device is check every 5 minutes to update its state (see options).

## USB key
* Bticino 3578: https://catalogo.bticino.it/BTI-3578-IT
* Legrand 088328

## Tested devices
* Legrand 088306: MicroModule


https://www.legrand.fr/sites/default/files/doc-pap-bd.pdf
