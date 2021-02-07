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
import configparser


class DesktopFileReader(configparser.RawConfigParser):
    def __init__(self):
        super(DesktopFileReader, self).__init__()
        self.optionxform = str

    def replace(self, origin=None, new=None):
        properties = origin.split(' ')
        if len(properties) <= 1:
            return new

        properties[0] = new
        return ' '.join(properties)


class EqualsSpaceRemover(object):
    def __init__(self, origin):
        self.origin = origin

    def write(self, what):
        self.origin.write(what.replace(" = ", "=", 1))
