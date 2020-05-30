# -*- coding: utf-8 -*-
# Copyright 2020 Alex Woroschilow (alex.woroschilow@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
import pty
import glob
import stat
import shutil
import pathlib
import subprocess
import configparser
from multiprocessing.pool import ThreadPool


class EqualsSpaceRemover(object):
    def __init__(self, origin):
        self.origin = origin

    def write(self, what):
        self.origin.write(what.replace(" = ", "=", 1))


class AppImageDesktopFinder(object):
    def __init__(self, appimage, mountpoint):
        self.mountpoint = mountpoint
        self.appimage = appimage

    def _desktop_origin(self):
        pattern = '{}/*.desktop'.format(self.mountpoint)
        for path in glob.glob(pattern):
            return path

    def property(self, origin=None):
        properties = origin.split(' ')
        properties[0] = self.appimage
        return ' '.join(properties)

    def files(self, destination=None):
        desktop_origin = self._desktop_origin()

        desktop_wanted = pathlib.Path(self.appimage)
        desktop_wanted = "{}/{}.desktop".format(destination, desktop_wanted.stem)
        return (desktop_origin, desktop_wanted)


class AppImageIconFinder(object):
    def __init__(self, appimage, mountpoint):
        self.mountpoint = mountpoint
        self.appimage = appimage

    def _icon_origin(self):
        pattern = '{}/*.svg'.format(self.mountpoint)
        for path_temp_icon in glob.glob(pattern):
            return path_temp_icon

        pattern = '{}/*.png'.format(self.mountpoint)
        for path_temp_icon in glob.glob(pattern):
            return path_temp_icon

        pattern = '{}/*.jpg'.format(self.mountpoint)
        for path_temp_icon in glob.glob(pattern):
            return path_temp_icon

        pattern = '{}/*.ico'.format(self.mountpoint)
        for path_temp_icon in glob.glob(pattern):
            return path_temp_icon

        return None

    def _icon_wanted(self):
        appimage = pathlib.Path(self.appimage)
        appimage = appimage.stem

        icon_origin = self._icon_origin()
        icon_origin = pathlib.PurePosixPath(icon_origin)
        return ''.join([appimage, icon_origin.suffix])

    def property(self, origin=None):
        origin = pathlib.Path(self.appimage)
        return origin.stem

    def files(self, destination=None):
        icon_origin = self._icon_origin()
        icon_wanted = self._icon_wanted()
        icon_wanted = "{}/{}".format(destination, icon_wanted)
        return (icon_origin, icon_wanted)


class ServiceAppImage(object):
    pool = ThreadPool(processes=1)

    def __init__(self, locations_local=[], locations_global=[]):
        self.locations_global = locations_global
        self.locations_local = locations_local

    @property
    def locations(self):
        return self.locations_global + \
               self.locations_local

    def _permissions(self, systemwide=False):
        if systemwide is None or not systemwide:
            return stat.S_IRWXU
        return stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IRWXO | stat.S_IROTH

    def _destination(self, package, systemwide=False):
        if systemwide is None or not systemwide:
            return os.path.expanduser('~/Applications/{}'.format(package))
        return '/Applications/{}'.format(package)

    def _integrate(self, appimage, prefix='/usr/share'):
        if not os.path.exists(appimage) or os.path.isdir(appimage):
            raise Exception('File does not exist')

        os.chmod(appimage, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        out_r, out_w = pty.openpty()
        process = subprocess.Popen([appimage, '--appimage-mount'], stdout=out_w, stderr=subprocess.PIPE)
        path_mounted = str(os.read(out_r, 2048), 'utf-8', errors='ignore')
        path_mounted = path_mounted.strip("\n\r")

        path_desktop = '{}/applications'.format(prefix)
        os.makedirs(path_desktop, exist_ok=True)

        path_icon = '{}/icons'.format(prefix)
        os.makedirs(path_icon, exist_ok=True)

        desktopfinder = AppImageDesktopFinder(appimage, path_mounted)
        desktop_origin, desktop_wanted = desktopfinder.files(path_desktop)

        iconfinder = AppImageIconFinder(appimage, path_mounted)
        icon_origin, icon_wanted = iconfinder.files(path_icon)

        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(desktop_origin)

        if not config.has_option('Desktop Entry', 'Version'):
            config.set('Desktop Entry', 'Version', 1.0)

        property_icon = config.get('Desktop Entry', 'Icon')
        config.set('Desktop Entry', 'Icon', iconfinder.property(property_icon))

        for section in config.sections():
            if config.has_option(section, 'Exec'):
                property_exec = config.get(section, 'Exec')
                config.set(section, 'Exec', desktopfinder.property(property_exec))

            if config.has_option(section, 'TryExec'):
                property_exec = config.get(section, 'TryExec')
                config.set(section, 'TryExec', desktopfinder.property(property_exec))

        with open(desktop_wanted, 'w') as desktop_wanted_stream:
            config.write(EqualsSpaceRemover(desktop_wanted_stream))

        with open(icon_origin, 'rb') as icon_origin_stream:
            with open(icon_wanted, 'wb') as icon_wanted_stream:
                icon_wanted_stream.write(icon_origin_stream.read())
                icon_wanted_stream.close()
            icon_origin_stream.close()

        process.terminate()

        return (desktop_wanted, icon_wanted)

    def integrate(self, appimage, systemwide=False):

        prefix = '/usr/share' if systemwide else \
            os.path.expanduser('~/.local/share')

        async_result = self.pool.apply_async(self._integrate, (appimage, prefix))
        return list(async_result.get())

    def list(self):
        for location in self.locations:
            location = os.path.expanduser(location)
            if location is None or not len(location):
                continue

            for appimage in glob.glob('{}/*.AppImage'.format(location)):
                yield appimage

    def install(self, tempfile, package, force=False, systemwide=False):
        destination = self._destination(package, systemwide)
        if os.path.exists(destination) and not force:
            raise Exception('{} already exists, use --force to override t'
                            'he existing package'.format(destination))

        if os.path.exists(destination):
            os.remove(destination)

        folder = os.path.dirname(destination)
        if len(folder) and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=False)

        shutil.move(tempfile, destination)
        permissions = self._permissions(systemwide)
        os.chmod(destination, permissions)

        if os.path.exists(tempfile):
            os.unlink(tempfile)

        return [destination] + self.integrate(destination, systemwide)
