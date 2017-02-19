#!/usr/bin/python
# This file contains the functions regarding the plugin manager.

import git, shutil, os, imp, sys
from . import security, api
import re

indexes = {}

def loadPlugins():
    plugin = {}
    plugin_dir = os.getcwd() + '/plugins/'
    for i in os.listdir(plugin_dir):
        if not i == '__init__.py' and i.endswith('.py'):
            name =  i.replace('.py', '')
            try:
               plugin[name] = imp.load_source(name, plugin_dir + i)
               plugin[name].init()
            except ImportError as msg:
               moduleName = str(msg).split(' ')[len(str(msg).split(' ')) -1]
               sys.exit("Error occured during loading imports for the plugin {}: {}. Install it with 'easy_install {}' or 'pip install {}'".format(name, msg, moduleName , moduleName))
    return plugin

def getPluginDict():
    global indexes
    return indexes

def setPluginDict(d):
    global indexes
    indexes = d

def getPluginVersion(loc):
    f = open(loc, 'r').read().split('@')
    v = None
    for l in f:
        t = l.split('=')
        if t[0].lower() == 'version':
            _tmp_v = t[1].split('.')
            c = 1
            _version = _tmp_v[0] + '.'
            while(c < len(_tmp_v)):
                _version += _tmp_v[c]
                c += 1
    return float(_version)

def indexPlugins(params={}):
    tmpFolder = 'plugins/index'
    indexFolderPath = 'plugins/index/'
    docsFolderPath = 'static/docs/'
    installedPlugins = []
    staticFolder = ['css/', 'images/', 'fonts/', 'js/']
    indexes = getPluginDict()
    pluginParts = ['templates/', 'plugins/']

    if 'action' in params:
        if not params['action'] == 'getPlugins':
            try:
                if not int(params['folid']) in indexes:
                    return "No valid plugin id specified."
            except:
                    return "Please specify integers only."

    if 'action' in params:
        if params['action'] == 'getPlugins':
            folders = [x for x in os.listdir(indexFolderPath) if os.path.isdir(os.path.join(indexFolderPath, x))]
            for i in folders:
                i = security.sanitizePathBasename(i)
                if i != '.git':
                    fol = {}
                    fol['id'] = len(indexes)
                    fol['folder'] = i
                    fol['status'] = 'install'
                    for filename in os.listdir('templates/'):
                        installedPlugins.append(filename)

                    for filename in os.listdir(indexFolderPath + i + '/templates'):
                        if filename in installedPlugins:
                            installed_version = getPluginVersion(docsFolderPath + i + '_readme.md')
                            indexed_version = getPluginVersion(indexFolderPath + i + '/' + docsFolderPath + 'readme.md')
                            if indexed_version > installed_version:
                                fol['update'] = 'yes'
                            else:
                                fol['update'] = 'no'
                            fol['status'] = 'remove'
                    readme = re.split('@', open(indexFolderPath + i + '/' + docsFolderPath + 'readme.md', 'r').read())#.split('@')

                    sumList = {}
                    for s in readme:
                        if re.search('\w+=', str(s)):
                            _check = re.search('\w+=', str(s)).group().replace('=', '')
                            _text = re.sub('\w+=', '', s)
                            if _check == 'summary' or _check == 'description':
                                _text = re.sub('\n', '<br>', _text)
                            fol[_check] = _text

                    if not i in (f['folder'] for f in indexes.values()):
                        indexes[len(indexes)] = fol
                    else:
                        for tmp in indexes.values():
                            if i == tmp['folder']:
                                for k in fol:
                                    if k != 'id':
                                        indexes[tmp['id']][k] = fol[k]
            setPluginDict(indexes)
            return indexes
        elif params['action'] == 'installPlugin':
            if 'folid' in params:
                if indexes[int(params['folid'])]['status'] == 'install':
                    src_path = indexFolderPath + indexes[int(params['folid'])]['folder'] + '/'
                    for part in pluginParts:
                        for filename in os.listdir(src_path + part):
                            shutil.copy(src_path + part + filename, part + filename)
                    for f in staticFolder:
                        if os.path.exists(src_path + 'static/' + f):
                            for filename in os.listdir(src_path + '/static/' + f):
                                shutil.copy(src_path + 'static/' + f + filename, 'static/' + f + filename)
                    for filename in os.listdir(src_path + '/' + docsFolderPath):
                        shutil.copy(src_path + '/' + docsFolderPath + filename, docsFolderPath + indexes[int(params['folid'])]['folder'] + '_' + filename)
                    indexes[int(params['folid'])]['status'] = 'remove'
                    global modules
                    modules = loadPlugins()
                    api.setModules(modules)
                    return indexes[int(params['folid'])]['folder'] + ' installed.'
                else:
                    return "This plugin is already installed."
        elif params['action'] == 'removePlugin':
            if 'folid' in params:
                if indexes[int(params['folid'])]['status'] == 'remove':
                    src_path = indexFolderPath + indexes[int(params['folid'])]['folder'] + '/'
                    for part in pluginParts:
                        for filename in os.listdir(src_path + part):
                            os.remove(part + filename)
                    for f in staticFolder:
                        if os.path.exists(src_path + 'static/' + f):
                            for filename in os.listdir(src_path + 'static/' + f):
                                os.remove('static/' + f + filename)
                    for filename in os.listdir(src_path + '/' + docsFolderPath):
                        shutil.copy(src_path + '/' + docsFolderPath + filename, docsFolderPath + indexes[int(params['folid'])]['folder'] + '_' + filename)
                    indexes[int(params['folid'])]['status'] = 'install'
                    return indexes[int(params['folid'])]['folder'] + ' removed.'
                else:
                    return "This plugin was already removed."
        setPluginDict(indexes)
    else:
        if not os.path.exists(tmpFolder):
            os.makedirs(tmpFolder)
        if not os.path.exists(indexFolderPath):
            os.makedirs(indexFolderPath)

        if not os.path.isfile(indexFolderPath + 'README.md'):
                shutil.rmtree(indexFolderPath)
                try:
                    git.Repo.clone_from("https://github.com/wez3/domoboard-plugins.git", indexFolderPath)
                except:
                    print('indexed')
        else:
            git.cmd.Git(indexFolderPath).pull("https://github.com/wez3/domoboard-plugins.git")
        folders = [x for x in os.listdir(indexFolderPath) if os.path.isdir(os.path.join(indexFolderPath, x))]
        return indexPlugins({'action': 'getPlugins'})
