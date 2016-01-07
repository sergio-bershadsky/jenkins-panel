# -*- coding: utf-8 -*-
from flask.ext.collect import Collect
from flask.ext.script import Manager

from jenkins_panel.app import app


manager = Manager(app)


collect = Collect()
collect.init_app(app)
collect.init_script(manager)


if __name__ == "__main__":
    manager.run()