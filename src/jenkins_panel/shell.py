# -*- coding: utf-8 -*-
import IPython

from jenkins_panel.app import app

app.testing = True

welcome_message = "Welcome!"

with app.app_context():
    IPython.embed(header=welcome_message)