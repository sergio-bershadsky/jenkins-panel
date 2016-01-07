FROM python:2.7

# Prepare sys
RUN apt-get update && apt-get install -y \
    python-dev python-setuptools python-pip \
    git-core \
    gettext \
    && pip install -U mysql-python

# Prepare python
COPY ./requirements.pip /srv/requirements.pip
RUN pip install -r /srv/requirements.pip

# Prepare env
ENV APP_NAME="/jenkins_panel"
ENV APP_ROOT="/opt${APP_NAME}"
ENV APP_REPOSITORY="${APP_ROOT}/repository"
ENV PYTHONPATH="${APP_REPOSITORY}/src"

# Prepare repository
COPY . ${APP_REPOSITORY}

# Prepare app
ENV DJANGO_SETTINGS_MODULE=jenkins_panel.settings

# Prepare initial
COPY ./deploy/entrypoint.sh /bin/entrypoint.sh
RUN chmod 700 /bin/entrypoint.sh

# Prepare ports
EXPOSE 80
EXPOSE 443

WORKDIR ${PYTHONPATH}

ENTRYPOINT ["/bin/entrypoint.sh"]