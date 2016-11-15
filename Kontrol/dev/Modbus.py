# !/usr/bin/env python
#
#   Copyright 2016 Yuregir Tekeli
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

"""



Driver for the MPC-10 process controller, for communication via the Modbus RTU protocol.

"""

import minimalmodbus

__author__ = "Yuregir TEKELI"
__email__ = "yuregir@teke.li"
__license__ = "Apache License, Version 2.0"


class MPC10Controller(minimalmodbus.Instrument):
    """Instrument class for MPC-10 process controller.

    Communicates via Modbus RTU protocol (via RS232 or RS485), using the *MinimalModbus* Python module.

    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247

    Implemented with these function codes (in decimal):

    ==================  ====================
    Description         Modbus function code
    ==================  ====================
    Read registers      3
    Write registers     16
    ==================  ====================

    """

    def __init__(self, portname, slaveaddress):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)

    def get_engine_rpm(self):
        return self.read_register(3, 1)

    def get_voltage(self):
        return self.read_register(4, 1)

    def get_controller_state(self):
        return self.read_register(7, 1)

    def get_mode(self):
        return self.read_register(12, 1)

    def get_ambient_temp(self):
        return self.read_register(14, 1)

    def get_active_shutdown_status_1(self):
        return self.read_register(8, 1)

    def get_active_shutdown_status_2(self):
        return self.read_register(9, 1)

    def get_active_shutdown_status_3(self):
        return self.read_register(10, 1)

    def get_serial_number(self):
        return self.read_register(208, 1)

    def get_start_temperature(self):
        return self.read_register(220, 1)

    def get_stop_temperature(self):
        return self.read_register(221, 1)

    def set_start_temperature(self, value):
        self.write_register(220, value, 1)

    def set_stop_temperature(self, value):
        self.write_register(220, value, 1)

    def get_fuel_level(self):
        """Disable the setpoint (SP) change rate for loop1. """

        return self.read_register(239, 1)

    def get_eeprom_save(self):
        return self.read_register(240, 1)

    def get_active_warning_status_1(self):
        """Return the output value (OP) for loop1 (in %)."""
        return self.read_register(242, 1)

    def get_active_warning_status_2(self):
        """Return True if Loop1 is inhibited."""
        return self.read_register(243, 1)

    def get_active_warning_status_3(self):
        """Return the output value (OP) for loop2 (in %)."""
        return self.read_register(244, 1)

    def get_threshold_alarm1(self):
        """Return the threshold value for Alarm1."""
        return self.read_register(10241, 1)

    def is_set_alarmsummary(self):
        """Return True if some alarm is triggered."""
        return self.read_register(10213, 1) > 0


########################
## Testing the module ##
########################

if __name__ == '__main__':
    minimalmodbus._print_out('TESTING MURPHY MPC-10 MODBUS MODULE')

    a = MPC10Controller('/dev/ttyUSB0', 1)
    a.debug = False

    minimalmodbus._print_out('Engine RPM:          {0}'.format(a.get_engine_rpm()))
    minimalmodbus._print_out('System Voltage:      {0}'.format(a.get_voltage()))
    minimalmodbus._print_out('Controller State:    {0}'.format(a.get_controller_state()))
    minimalmodbus._print_out('Controller Mode:     {0}'.format(a.get_mode()))
    minimalmodbus._print_out('Ambient temp:        {0}'.format(a.get_ambient_temp()))
    minimalmodbus._print_out('Shutdown Status 1:   {0}'.format(a.get_active_shutdown_status_1()))
    minimalmodbus._print_out('Shutdown Status 2:   {0}'.format(a.get_active_shutdown_status_2()))
    minimalmodbus._print_out('Shutdown Status 3:   {0}'.format(a.get_active_shutdown_status_3()))
    minimalmodbus._print_out('MPC10 Serial:        {0}'.format(a.get_serial_number()))
    minimalmodbus._print_out('Start Temperature:   {0}'.format(a.get_start_temperature()))
    minimalmodbus._print_out('Stop Temperature:    {0}'.format(a.get_stop_temperature()))
    minimalmodbus._print_out('Fuel Level:          {0}'.format(a.get_fuel_level()))
    minimalmodbus._print_out('EEPROM Save:         {0}'.format(a.get_eeprom_save()))
    minimalmodbus._print_out('Active Warning 1:    {0}'.format(a.get_active_warning_status_1()))
    minimalmodbus._print_out('Active Warning 2:    {0}'.format(a.get_active_warning_status_2()))
    minimalmodbus._print_out('Active Warning 3:    {0}'.format(a.get_active_warning_status_3()))

    # a.set_sprate_loop1(30)
    # a.enable_sprate_loop1()

    minimalmodbus._print_out('DONE!')

pass
