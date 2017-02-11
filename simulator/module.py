# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>
#
# Modified by Davide Pedranz <davide.pedranz@gmail.com>


import sys
import sim


class Module:
    """
    Defines a generic simulation module, implementing some basic functionality
    that all modules should inherit from
    """

    # static class variable automatically incremented every time a new module is
    # instantiated
    __modules_count = 0

    def __init__(self):
        """
        Constructor. Gets simulation instance for scheduling events and
        automatically assigns an ID to the module
        """
        self.sim = sim.Sim.Instance()
        # auto assign module id
        self.module_id = Module.__modules_count
        Module.__modules_count += 1
        # get data logger from simulator
        self.logger = self.sim.get_logger()

    def initialize(self):
        """
        Initialization method called by the simulation for each newly
        instantiated module
        """
        return

    def handle_event(self, event):
        """
        This function should be overridden by inheriting modules to handle
        events for this module. If not overridden, this method will throw an
        error and stop the simulation
        """
        print("Module error: class %s does not override handle_event() method",
              self.get_type())
        sys.exit(1)

    def get_id(self):
        """
        Returns module id
        """
        return self.module_id

    def get_type(self):
        """
        Returns module type
        """
        return self.__class__.__name__
