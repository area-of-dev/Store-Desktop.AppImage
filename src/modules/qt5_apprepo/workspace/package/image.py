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

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsBlurEffect


class ImageWidget(QtWidgets.QLabel):

    def __init__(self, entity=None, width=400):
        super(ImageWidget, self).__init__()

        pixmap = QtGui.QPixmap('img/spinner.webp')
        self.setPixmap(pixmap.scaledToWidth(width))

    def onImageLoaded(self, data, width=400):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)

        pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
        if not pixmap: return None

        self.setPixmap(pixmap)

        # # creating a blur effect
        # blur_effect = QGraphicsBlurEffect()
        # blur_effect.setBlurRadius(1)
        # self.setGraphicsEffect(blur_effect)

    def close(self):
        super().deleteLater()
        return super().close()
