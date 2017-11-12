* * *

# wifid

리눅스에서 와이파이 다이렉트 연결 설정하기

## WiFi Direct on Linux

So I tried to connect two devices using Wifi-Direct.

One was a PC with Linux, and the other was an Android smartphone.

I wanted Linux as a GO and Android as a client.

In order to set up Wifi-Direct connection, I made a Python script to start wpa_supplicant and wpa_cli with p2p options.

And this is what worked for me in Linux.

## wifid.py

It provides 3 functions:

- setup_conf_files()
- start_as_go_fedora()
- start_as_go_ubuntu()

which are to enable P2P device connectivity and become an autonomous GO, as the name suggests.

## ref
http://processors.wiki.ti.com/index.php/WiFi_Direct_Configuration_Scripts
http://processors.wiki.ti.com/index.php/OMAP_Wireless_Connectivity_NLCP_WiFi_Direct_Configuration_Scripts

* * *