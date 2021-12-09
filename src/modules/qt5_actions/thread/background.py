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
import random
import time

import hexdi
from PyQt5 import QtCore
import hexdi

from modules.qt5_actions.storage.interface import ActionsStorage


class BackgroundThread(QtCore.QThread):

    def __init__(self):
        super(BackgroundThread, self).__init__()

    @hexdi.inject('actions')
    def run(self, actions):
        while True:
            for action in actions.actions():
                action.progress = random.randrange(1, 100, 1)
                time.sleep(0.1)
            time.sleep(1)

    @hexdi.inject('actions')
    def start(self, actions: ActionsStorage) -> None:
        super().start()

    def terminate(self) -> None:
        super().terminate()
