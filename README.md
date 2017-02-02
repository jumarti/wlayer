# wlayer
Control Linux desktop windows layouts via REST


A python programm, expected to run as a systemd unit (or any daemonaizer) which exposes a REST API to manipulate windows positions and sizes according to preset layouts defined on json files.

## What for ?
Personal tool: I use a fanless linux box connected to the TV  using Chrome to watch Netflix, YouTube etc. I also have several RTSP compatible cameras connected on the same network and I need to be able to switch to a DVR-like camera grid view and back to Chrome, or even include chrome on a box of the grid. A web app accesible within a phone should expose buttons to trigger these layouts.

## How does it work
- Python Tornado to expose REST entry points. Flask would have been another option. Just wanted to try Tornado. I use ./wserver for this. This is done on `server.py, this the python main script to deamonize.

- `xdotool` is used to manipulate windows. This is done on core functions defined on `layouts.py` file. `Popen` is used for sys calls.

- Layouts are json files which define xdtotool calls for an specific window. Another json file determines how a program is called, and also some KEYs actions to expose on via core functions. 

Example:
Definitions `base.defs.json`
```json
{
	"netflix" : {
		"service" : "chrome",
		"process_lookup" : null,
		"title_lookup" : "netflix",
		"exec" : "/usr/bin/google-chrome --app=file:///home/juanc/netflix.html",
		"controls" : {
			"play" : {
				"xdo" : ["key space"]
				},
			"stop" : {
				"xdo" : ["key space"]
				},
			"full" : {
				"xdo" : ["key F11"]
				},
			"not_full" : {
				"xdo" : ["key F11"]
				},
			"close" : {
				"xdo" : ["key Alt+F4"]
				}		
		}

	},
	"*.rtsp" : {
		"title_lookup" : "VLC media player",
		"controls" : {
			"play" : {
				"xdo" : ["key space"]
				},
			"stop" : {
				"xdo" : ["key s"]
				},
			"full" : {
				"xdo" : ["key f"]
				},
			"not_full" : {
				"xdo" : ["key f"]
				},
			"close" : {
				"service" : "stop"
			}
		}
	}
```

A layout `test.layout.json`
```json
{
	"nuc.leo.rtsp" : [
		"windowmove 2000 0",
		"windowsize 300 170"
 
	],
	"nuc.high.rtsp" : [
		"windowmove 2000 200",
		"windowsize 300 170"
 
	],
	"nuc.bridge.rtsp" : [
		"windowmove 2000 400",
		"windowsize 300 170"
 
	],		

	"nuc.low.rtsp" : [
		"windowmove 2000 600",
		"windowsize 300 170"
 
	],	

	"luc.road.rtsp" : [
		"windowmove 2000 800",
		"windowsize 300 200"
		
	],
	"netflix" : [
		"windowmove 0 0",
		"windowsize 1373 1000"

	]	

}
```


## Status
Had to interrupt this work. Later I found this mini keyboards-mouse-dongle gadgets which give you a full desktop wireless  controll, leaving the phone-controlling less apealing. However, the idea of exposing xdotool via REST API may be usefull to ninja-control a Linux Desktop. 

- Core functions OK: Able to manipulate windows according to layouts and params,

- Missing API connection to core functions

- Missing phone web app


