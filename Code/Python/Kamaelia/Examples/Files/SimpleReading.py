#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2010 British Broadcasting Corporation and Kamaelia Contributors(1)
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://www.kamaelia.org/AUTHORS - please extend this file,
#     not this notice.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Checked: 2024/03/24

from Kamaelia.Util.Console import ConsoleReader, ConsoleEchoer
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.File.Reading import SimpleReader
from Kamaelia.Util.RateFilter import MessageRateLimit

Pipeline(
    SimpleReader("/etc/fstab"),
    ConsoleEchoer(),
).run()


Pipeline(
    SimpleReader("/etc/fstab"),
    MessageRateLimit(2,1,hardlimit=0),
    ConsoleEchoer(),
).run()

Pipeline(
    SimpleReader("/etc/fstab"),
    MessageRateLimit(0.5,1,hardlimit=1),
    ConsoleEchoer(),
).run()

