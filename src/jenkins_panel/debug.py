# -*- coding: utf-8 -*-
from wdb.ext import WdbMiddleware
from flask import Flask


class Wdb(object):

    app = None

    def init_app(self, app):
        self.app = app
        if app.config.get('WDB_ENABLED', app.debug):
            start_disabled = app.config.get('WDB_START_DISABLED', False)
            app.wsgi_app = WdbMiddleware(app.wsgi_app, start_disabled)
            # Patch app.run to disable Werkzeug debugger
            app.run = self._run

    def _run(self, *args, **kwargs):
        kwargs["use_debugger"] = False
        return Flask.run(self.app, *args, **kwargs)