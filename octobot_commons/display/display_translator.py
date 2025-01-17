#  Drakkar-Software OctoBot-Commons
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import contextlib
import octobot_commons.logging as logging


class DisplayTranslator:
    """
    Interface for simplifying displayed elements translation
    """

    def __init__(self):
        self.logger = logging.get_logger(self.__class__.__name__)

    def to_json(self, name="root") -> dict:
        """
        Return the json representation of this display
        :param name: name of the root element
        :return: the json compatible dict representation of this display
        """
        raise NotImplementedError("to_json is not implemented")

    @contextlib.contextmanager
    def part(self, name):
        """
        Adds a part to this display
        :param name: name of the part
        """
        raise NotImplementedError("part is not implemented")
