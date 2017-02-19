#!/usr/bin/python
# This file contains the functions used for web based configuration of domoboard

import git
from . import api
from flask import request

def writeToConfig(idx, page, component, description, extra):
    originalCfg = api.getOriginalConfig()
    section = dict(originalCfg[page][component])
    section[description] = idx
    originalCfg[page][component] = section
    originalCfg.write()

def getVersion():
    f = open('VERSION.md', 'r')
    version = f.read().rstrip()
    f.close()
    return version

def performUpgrade():
    git.cmd.Git('.').pull()
    return "Upgrade completed."

def getCurrentBranch():
    try:
        repo = git.Repo('.')
        branch = repo.active_branch
        return branch.name
    except:
        return "None"
