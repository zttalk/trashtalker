#!/usr/bin/env python3

import re
import os
import threading
import time

import flask
import flask_wtf
import gevent.pywsgi
import keyboard
import playsound
import pyperclip
#import subprocess
import wtforms
import socket
import random

SOUNDS_DIR = 'sounds'
SOUND_FIELD_PREFIX = 'sound_'
TITLE = 'Starcraft 2 Trash Talker'
FG_WINDOW_TITLE = 'StarCraft II'

DEBUG_TEST_SEND = False

def copy2clip(txt):
	if os.name == 'nt':
		pyperclip.copy(txt.strip())
	else:
		raise Exception('help, i\'m not new technology')
		#cmd='echo '+shlex.quote(txt.strip())+'|xsel --clipboard'
		#return subprocess.check_call(cmd, shell=True)

def get_fg_window():
	if os.name == 'nt':
		from win32gui import GetWindowText, GetForegroundWindow
		return GetWindowText(GetForegroundWindow())
	else:
		raise Exception('help, i\'m not new technology')

class MessageForm(flask_wtf.FlaskForm):
	message = wtforms.StringField('Message to send:')
	message_submit = wtforms.SubmitField('Send Message')
	# (Note that this class is updated with sound fields just below.)

sounds = {}
for direntry in os.listdir(SOUNDS_DIR):
	m = re.fullmatch(r'(.*)\.(?:wav|mp3)', direntry, re.IGNORECASE)
	if m and direntry != "Bruno.wav":
		label = m.group(1)
		sounds[label] = direntry
		setattr(MessageForm, SOUND_FIELD_PREFIX + re.sub(r'[^A-Za-z0-9_]+', '', m.group(1)).lower(), wtforms.SubmitField(label))

def play_sound(form):
	for field in form:
		if field.name.startswith(SOUND_FIELD_PREFIX) and field.data and field.label.text in sounds:
			print('Playing sound "{}"'.format(field.label.text))
			try:
				if random.randrange(0, 10, 1) == 5:
					playsound.playsound(os.path.join(SOUNDS_DIR, "Bruno.wav"), block=os.name != 'nt')
				else:
					playsound.playsound(os.path.join(SOUNDS_DIR, sounds[field.label.text]), block=os.name != 'nt')
			except Exception as e:
				print('Failed: {}'.format(e))
			return True
	return False

keyboard_mutex = threading.Lock()

def send_message(form):
	if not form.message_submit.data:
		return False
	
	message = form.message.data.strip()
	if not message:
		return True

	keyboard_mutex.acquire()
	try:
		if DEBUG_TEST_SEND:
			time.sleep(1)
		print('Chat line: "{}"'.format(message))
		if get_fg_window() != FG_WINDOW_TITLE and not DEBUG_TEST_SEND:
			print('wrong window')
		else:
			copy2clip(message)
			start_time = time.time_ns()
			keyboard.press_and_release('enter')
			keyboard.press_and_release('shift+ins')
			#keyboard.press_and_release('ctrl+v')
			keyboard.press_and_release('enter')
			end_time = time.time_ns()
			print('Time {} µs'.format(int((end_time - start_time) / 1000)))
	finally:
		keyboard_mutex.release()
	return True

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'veryunimaginablysecret'

@app.route('/', methods=['GET'])
def show_ui():
	form = MessageForm()
	return flask.render_template('keys.html', title=TITLE, form=form)

@app.route('/', methods=['POST'])
def go():
	form = MessageForm()
	send_message(form)
	play_sound(form)
	return flask.redirect('/')

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port='80')
	http_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 80), app)	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	print("Local IP: ", s.getsockname()[0])
	s.close()
	http_server.serve_forever()
