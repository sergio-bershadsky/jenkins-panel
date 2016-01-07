import jenkins

from . import settings


client = jenkins.Jenkins(settings.SERVER)