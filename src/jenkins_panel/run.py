# -*- coding: utf-8 -*-
from jenkins_panel.app import app


if __name__ == '__main__':
    app.run\
        ( host='0.0.0.0'
        , port=80
        )