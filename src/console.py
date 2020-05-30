# -*- coding: utf-8 -*-
# Copyright 2015 Alex Woroschilow (alex.woroschilow@gmail.com)
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
import sys
import logging
import optparse
import inject

from importlib import util

abspath = sys.argv[0] \
    if len(sys.argv) else \
    os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))


class Application(object):

    def __init__(self, options, args):
        spec = util.find_spec('lib.kernel')
        module = spec.loader.load_module()
        if module is None: return None

        self.kernel = module.Kernel(options, args)

    @inject.params(console='console', logger='logger')
    def exec_(self, options, args, console=None, logger=None):

        actionsmap = {
            'status': console.status,
            'cleanup': console.cleanup,
            'upload': console.upload,
            # Commands to synchronize application with the system
            # there are few keywords for the same commands for the usability reason
            'synchronize': console.synchronize,
            'sync': console.synchronize,
            # Look for the application in the repository
            # there are few keywords for the same commands for the usability reason
            'search': console.search,
            'lookup': console.search,
            'find': console.search,
            # Uninstall the applications from the system
            # there are few keywords for the same commands for the usability reason
            'uninstall': console.uninstall,
            'remove': console.uninstall,
            'delete': console.uninstall,
            'rm': console.uninstall,
            # Commands to install application from the apprepo
            # there are few keywords for the same commands for the usability reason
            'install': console.install,
            'download': console.install,
            'get': console.install,
            'in': console.install,
            # Commands to update current installed applications to the latest versions
            # there are few keywords for the same commands for the usability reason
            'update': console.update,
            'upgrade': console.update,
            'up': console.update,
            # 'upload': console.upload_version,
            # 'upload-version': console.upload_version,
            # 'upload-package': console.upload_version,
            # 'push-version': console.upload_version,
            # 'push-package': console.upload_version,
        }

        command = args[0] if len(args) else 'status'
        logger.info('command: {}'.format(command))
        if not len(command) or command not in actionsmap.keys():
            return logger.error('unknown command: {}'.format(command))

        action = actionsmap[command] or None
        if action is None or not callable(action):
            return logger.error('unknown command: {}'.format(command))

        try:
            for output in action(options, args[1:]):
                print(output)
        except Exception as ex:
            print('Failed: {}'.format(ex))
            raise ex


if __name__ == "__main__":
    parser = optparse.OptionParser("""apprepo [options] [argument] <string>
    status\t- display a list of the available AppImage files
    cleanup\t- look for the .desktop files without binaries or icons without the desktop files and remove them
    upload\t- upload a new version of the AppImage to the apprepo server
    synchronize\t- go through all available AppImage files and integrate them into the system if necessary
    update \t(upgrade|up) \t<string>\t- check for the latest version and install it 
    search \t(find|lookup) \t<string>\t- look for an AppImage files at the apprepo server by the string
    uninstall \t(remove|rm|delete) \t<string>\t- remove the AppImage from the system by the name
    install \t(in|download|get) \t<string>\t- install an AppImage from the apprepo by the name
    """)

    logfile = os.path.expanduser('~/.config/AOD-Store/default.log')

    parser.add_option("--logfile", default=logfile, dest="logfile", help="Logfile location")
    parser.add_option("--loglevel", default=logging.DEBUG, dest="loglevel", help="Logging level")
    parser.add_option("--version-token", dest="version_token", help="Upload token", default=None)
    parser.add_option("--version-description", dest="version_description", help="description", default=None)
    parser.add_option("--version-name", dest="version_name", help="Upload name", default=None)
    parser.add_option("--force", dest="force", help="Force execution", action='store_true')
    parser.add_option("--global", dest="systemwide", help="Install the application for all users", action='store_true')
    parser.add_option("--cleanup", dest="cleanup", help="Remove unknown packages", action='store_true')

    configfile = os.path.expanduser('~/.config/AOD-Store/default.conf')
    parser.add_option("--config", default=configfile, dest="config", help="Config file location")

    (options, args) = parser.parse_args()

    log_format = '[%(relativeCreated)d][%(name)s] %(levelname)s - %(message)s'
    logging.basicConfig(level=options.loglevel, format=log_format)

    application = Application(options, args)
    sys.exit(application.exec_(options, args))
