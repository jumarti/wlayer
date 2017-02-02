import os
import json
import time
import pprint
from subprocess import PIPE, Popen

from . import logger
from . import getBasePath
from . import definitions
from . import current_windows


def _getServiceName(window):
	
	if window.endswith(".rtsp"):
		return "play@" + window.replace(".rtsp", ".service")
	
	service = definitions.get(window, {}).get('service')
	
	if service is None:
		raise Exception("service name not found")
	
	return service


def _getServiceStatus(window, process_lookup=None):
	status_txt, error = _serviceAction(window, 'status')
	if len(error) > 0:
		raise Exception(error)
	pid = None
	isup = False
	for line in status_txt.split("\n"):
		line = line.strip()
		active = "Active: "
		if line.startswith(active) == True:
			status = line.split(active)[1]
			if status.startswith("active ") == True:
				isup = True
				if process_lookup is None:
					break
		
		if process_lookup is not None:
			if line.find(process_lookup) != -1:
				pid = int(line.split("\x80")[1].split(" ")[0])
				break

	return isup, pid


def _getWindowIds(window):
	process_lookup, title_lookup = _getProcessLookUp(window)

	if process_lookup is not None:
		isup, pid = _getServiceStatus(window, process_lookup)
		if isup == False:
			return []

		args = ["xdotool", "search", "--pid", "{0}".format(pid)]
	else:
		args = ["xdotool", "search", "--name", "{0}".format(title_lookup)]

	proc = Popen(args, stdout=PIPE, stderr=PIPE)
	search, err = proc.communicate()
	if len(err) > 0:
		raise Exception(err)

	window_ids = []
	for id in search.split("\n"):
		try:
			wid = int(id)
		except: 
			continue
		
		if process_lookup is not None:
			args = ["xdotool", "getwindowname", "{0}".format(wid)]
			proc = Popen(args, stdout=PIPE, stderr=PIPE)
			out, err = proc.communicate()
			if len(err) > 0:
				raise Exception(err)

			if out.lower().find(title_lookup.lower()) != -1:
				window_ids.append(wid)
				break
		else:
			window_ids.append(wid)

	return window_ids

def _getProcessLookUp(window):
	
	key = window
	if window.endswith(".rtsp"):
		path = getBasePath()
		rtsp = open(path.rstrip("/") + "/{0}".format(window)).read()
		#rtsp = rtsp.strip().replace("?", "\\?")
		process_look_up = rtsp
		key = "*.rtsp"
	else:
		process_look_up = definitions.get(window, {}).get('process_lookup')


	title_lookup = definitions.get(key, {}).get('title_lookup')

	if title_lookup is None:
		raise Exception("title lookup not found")


	return process_look_up, title_lookup


def _serviceAction(window, action):

	service = _getServiceName(window)
	args = ["sudo", "systemctl", action, service]
	if action == "status":
		args += ["-n", "0", "-l"]

	proc = Popen(args, stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()

	return out, err


def _execXdo(window, instructions):
	
	wids = _getWindowIds(window)
	if len(wids) == 0:
		raise Exception("no window")


	out = ""
	for wid in wids:
		for instruction in instructions:

			ins = instruction.strip().split()
			command = ins[0]
			if command == "key":
				#args = ["xdotool", command, "--window", "{0}".format(wid)]
				args = ["xdotool", "windowactivate", "--sync"]
				args += ["{0} ".format(wid), ins[0]]
				args += [ " ".join(ins[1:])]
				pprint.pprint(args)
				
			elif command == "windowmove" or \
				command == "windowsize":
				# args = [ "xdotool", command, "--sync", "{0}".format(wid)]
				args = [ "xdotool", command, "{0}".format(wid)]
				args += ins[1:]
				#pprint.pprint(args)

			elif command == "windowactivate":
				args = [ "xdotool", command, "{0}".format(wid)]


			else:
				raise Exception("unknown xdo cmd {0}".format(command))
			proc = Popen(
				args, 
				stdout=PIPE, stderr=PIPE
				)
			tmp_out, err = proc.communicate()

			if len(err) > 0:
				raise Exception(err)

			out += tmp_out
		

	return out

def execControl(window, action=None, xdos=None, service=None):

	if action is not None:
		key = window
		if window.endswith(".rtsp"):
			key = "*.rtsp"
		xdos = definitions[key].get(
			"controls",{}).get(
			action,{}).get("xdo")

		service = definitions[key].get(
			"controls",{}).get(
			action,{}).get("service")

	if xdos is None and service is None:
		raise Exception("No actions set")

	if xdos is not None:
		if isinstance(xdos, basestring) == True:
			xdos = [xdos]
		if isinstance(xdos, list) == False:
			raise Exception("no xdos found for {0}".format(action))

		return _execXdo(window, xdos)

	if service is not None:
		if isinstance(service, basestring) == False:
			raise Exception("unknown action format") 
		return _serviceAction(window, service)

def _getLayout(layout):
	path = getBasePath()	
	layoutPath =path.rstrip("/") + "/{0}.layout.json".format(layout) 
	return json.loads(open(layoutPath).read())


def openLayout(layout, only_windows=None):
	global current_windows
	
	if isinstance(layout, basestring):
		layout = _getLayout(layout)

	pendings = []
	errors = []
	windows = layout.keys()

	orphans = list(set(current_windows).difference(set(windows)))
	for orphan in orphans:
		execControl(orphan, "close")

	current_windows = windows

	for window in windows:
		if only_windows is not None:
			if isinstance(only_windows, basestring):
				only_windows = [only_windows]
			if window not in only_windows:
				continue
		try:
			out, err = _serviceAction(window, 'start')
			if len(err) > 0:
				raise Exception(err)

			pendings.append(window)
		except Exception as err:
			errors.append((window, err))

	timeout = time.time()
	while len(pendings) > 0:
		finished = []
		for window in pendings:
			wids = _getWindowIds(window)
			if len(wids) == 0:
				key = window
				if window.endswith(".rtsp"):
					key = "*.rtsp"
				
				exec_proc = definitions[key].get('exec')
				if exec_proc is not None:
					logger.debug("uses exec {0}".format(exec_proc))
					isup, pid = _getServiceStatus(window)
					if isup == False:
						continue

					proc = Popen(exec_proc.split(), stdout=PIPE, stderr=PIPE )
					out, err = proc.communicate()
					if len(err) > 0:
						errors.append((window, err))
						finished.append(window)
					else:
						tries = 0
						while tries < 10:
							time.sleep(1)
							wids = _getWindowIds(window)
							if len(wids) > 0:
								break
							tries +=1
								

				continue
			if len(wids) > 1:
				# got multiple windows ids, restart the whole thing
				logger.warning("got multiple windows ids, restarting service {0}".format(window))
				try:
					out, err = _serviceAction(window, 'restart')
					if len(err) > 0:
						raise Exception(err)
				except Exception as err:
					finished.append(window)
					errors.append((window, err))

				continue

			#all ok		
			finished.append(window)
			try:
				_execXdo(window, layout[window])
			except Exception as err:
				errors.append((window, err))

		for done in finished:
			del(pendings[pendings.index(done)] )

		if len(pendings) == 0:
			break
		time.sleep(0.5)
		if time.time() - timeout > 10*len(pendings):
			raise Exception("timeout")


	return windows, errors


