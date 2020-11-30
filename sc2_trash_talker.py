import keyboard,time,sys,pyperclip,subprocess,playsound,os
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config['SECRET_KEY']='verysecret'

class MessageForm(FlaskForm):
    username = StringField('Message to send:', validators=[DataRequired()])
    submit = SubmitField('Send Message')
    chicken = SubmitField('Chicken')
    ohyeah = SubmitField('Oh Yeah!')
    gg = SubmitField('GG!')
    gameover = SubmitField('Game Over')
    fail = SubmitField('Fail')

def copy2clip(txt):
    if os.name == 'nt':
        pyperclip.copy(txt.strip())
    else:
        cmd='echo '+shlex.quote(txt.strip())+'|xsel --clipboard'
        return subprocess.check_call(cmd, shell=True)

def play_sound(form):
    if form.chicken.data:
        playsound.playsound("sounds/chicken.wav")
    if form.ohyeah.data:
        playsound.playsound("sounds/ohyeah.wav")
    if form.gg.data:
        playsound.playsound("sounds/gg.wav")
    if form.gameover.data:
        playsound.playsound("sounds/gameover.wav")
    if form.fail.data:
        playsound.playsound("sounds/fail.wav")

def send_message(form):
    if form.submit.data:
        copy2clip(form.username.data)
        start_time = time.time_ns()
        keyboard.press_and_release('enter')
        keyboard.press_and_release('shift+ins')
        #keyboard.press_and_release('ctrl+v')       
        keyboard.press_and_release('enter')
        end_time = time.time_ns()
        print("Time {} us".format(int((end_time-start_time)/1000)))
        return True
    return False
              
@app.route('/', methods=['GET', 'POST'])
def trash_talker():
    form = MessageForm()
    play_sound(form)
    if send_message(form):
        return redirect('/')
    else:
        return render_template('keys.html', title='Starcraft 2 Trash Talker', form=form)

if __name__ == '__main__':
    keyboard.press_and_release('esc')
    app.run(host="0.0.0.0", port="80")
