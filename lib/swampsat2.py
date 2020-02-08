# MIT License
#
# Copyright (c) 2020 Ralen Toledo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Usage: swampsat2 [-l LOGFILE] [-d DELIMITER] [-f FILE]
          swampsat2 [-l LOGFILE] [-d DELIMITER] [-s HEXSTRING]

Parse SwampSat II beacons from either a file or command-line string

Options:
  -f FILE, --file=FILE                 input file containing hex strings from a SwampSat II beacon
  -s HEXSTRING, --hexstring=HEXSTRING  hex string from a SwampSat II beacon
  -l LOGFILE, --logfile=LOGFILE        file where parsed data will be saved [default: [$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json]
  -d DELIMITER, --delimiter=DELIMITER  delimiter for input HEX string (whitespace is automatically removed)
  -h --help                            prints this help message
  --version                            prints current version

"""

from docopt import docopt


class ParseDownlink:

    def __init__(self, hexstr='', dlim=''):
        from _collections import OrderedDict

        self._errmsg = ''
        self.compileddata = OrderedDict()
        self._parse(hexstr, dlim)

    @classmethod
    def parse(cls, hexstr='', dlim=''):
        obj = cls(hexstr, dlim)
        return obj.compileddata

    @classmethod
    def parserecord(cls, hexstr='', logpath='[$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json', dlim=''):
        obj = cls(hexstr, dlim)
        if obj._errmsg == '':
            obj.record(logpath)
        return obj.compileddata

    def display(self):
        import json
        print(json.dumps(self.compileddata, indent=4))

    def get(self):
        return self.compileddata

    def record(self, logpath='[$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json'):
        import json
        import datetime
        import os

        # Replace the $HOME placeholder with the OS/user corrected home folder
        logpath = logpath.replace(os.path.normcase('[$HOME]'), os.path.expanduser('~'))

        # Add a timestamp to the file if the "[$TIMESTAMP]" placeholder exists
        logpath = logpath.replace(os.path.normcase('[$TIMESTAMP]'), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

        # Create path directory tree if it doesn't already exist
        try:
            os.makedirs(os.path.split(logpath)[0], exist_ok=True)
        except OSError:
            pass

        # Create file
        with open(logpath, 'at', encoding='utf-8') as lfile:
            json.dump(self.compileddata, lfile, indent=4)
            lfile.write('\n')

    def _parse(self, hexstr, dlim=''):
        from collections import OrderedDict
        import datetime

        # Expected packet lengths
        packetlens = {'adac': 137, 'cdh': 112, 'eps': 116, 'battery': 15, 'vutrx': 28, 'ants': 4, 'stx': 22}

        # Clean input
        hexstr_cleaned, errmsg = ParseDownlink._cleaninput(hexstr, dlim)
        length = len(hexstr_cleaned)
        if length == 0:

            self._errmsg = errmsg

        # Check if the downlink is contains the acknowledgement
        elif ''.join(['47', '61', '74', '6f', '72', '20', '4e', '61',
                      '74', '69', '6f', '6e', '20', '49', '73', '20',
                      '45', '76', '65', '72', '79', '77', '68', '65',
                      '72', '65', '21', '20', '46', '72', '6f', '6d',
                      '20', '53', '77', '61', '6d', '70', '53', '61',
                      '74', '20', '49', '49']) in ''.join(hexstr_cleaned):

            self.compileddata = OrderedDict()
            self.compileddata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.compileddata['msgtype'] = 0
            self.compileddata['messagenum'] = 1
            self.compileddata['messagetotal'] = 1
            self.compileddata['message'] = 'Gator Nation Is Everywhere! From SwampSat II'
            self.compileddata['lastcommand'] = hexstr_cleaned[-2]
            self.compileddata['awknowledgement'] = hexstr_cleaned[-1]

        # Flight mode 1 first beacon
        elif length == 112:

            # Separate data packets
            cdhlist = hexstr_cleaned[:packetlens['cdh']]

            cdhdata = self._cdh(cdhlist)

            self.compileddata = OrderedDict()
            self.compileddata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.compileddata['msgtype'] = 1
            self.compileddata['messagenum'] = 1
            self.compileddata['messagetotal'] = 2
            self.compileddata.update(cdhdata)

        # Flight mode 2 first beacon
        elif length == 249:

            # Separate data packets
            cdhlist = hexstr_cleaned[:packetlens['cdh']]
            adaclist = hexstr_cleaned[packetlens['cdh']:]

            cdhdata = self._cdh(cdhlist)
            adacdata = self._adac(adaclist)

            self.compileddata = OrderedDict()
            self.compileddata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.compileddata['msgtype'] = 2
            self.compileddata['messagenum'] = 1
            self.compileddata['messagetotal'] = 2
            self.compileddata.update(cdhdata)
            self.compileddata.update(adacdata)

        # Flight mode 1 second beacon
        elif length == 163:

            # Separate data packets
            epslist = hexstr_cleaned[:packetlens['eps']]

            batterylist = hexstr_cleaned[
                          packetlens['eps']:
                          packetlens['eps'] +
                          packetlens['battery']
                          ]

            vutrxlist = hexstr_cleaned[
                        packetlens['eps'] +
                        packetlens['battery']:
                        packetlens['eps'] +
                        packetlens['battery'] +
                        packetlens['vutrx']
                        ]

            antslist = hexstr_cleaned[packetlens['eps'] + packetlens['battery'] + packetlens['vutrx']:]

            epsdata = self._eps(epslist)
            batterydata = self._battery(batterylist)
            vutrxdata = self._vutrx(vutrxlist)
            antsdata = self._ants(antslist)

            self.compileddata = OrderedDict()
            self.compileddata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.compileddata['msgtype'] = 3
            self.compileddata['messagenum'] = 2
            self.compileddata['messagetotal'] = 2
            self.compileddata.update(epsdata)
            self.compileddata.update(batterydata)
            self.compileddata.update(vutrxdata)
            self.compileddata.update(antsdata)

        # Flight mode 2 second beacon
        elif length == 185:

            # Separate data packets
            epslist = hexstr_cleaned[:packetlens['eps']]

            batterylist = hexstr_cleaned[
                          packetlens['eps']:
                          packetlens['eps'] +
                          packetlens['battery']
                          ]

            vutrxlist = hexstr_cleaned[
                        packetlens['eps'] +
                        packetlens['battery']:
                        packetlens['eps'] +
                        packetlens['battery'] +
                        packetlens['vutrx']
                        ]

            antslist = hexstr_cleaned[
                       packetlens['eps'] +
                       packetlens['battery'] +
                       packetlens['vutrx']:
                       packetlens['eps'] +
                       packetlens['battery'] +
                       packetlens['vutrx'] +
                       packetlens['ants']
                       ]

            stxlist = hexstr_cleaned[
                      packetlens['eps'] +
                      packetlens['battery'] +
                      packetlens['vutrx'] +
                      packetlens['ants']:
                      ]

            epsdata = self._eps(epslist)
            batterydata = self._battery(batterylist)
            vutrxdata = self._vutrx(vutrxlist)
            antsdata = self._ants(antslist)
            stxdata = self._stx(stxlist)

            self.compileddata = OrderedDict()
            self.compileddata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.compileddata['msgtype'] = 4
            self.compileddata['messagenum'] = 2
            self.compileddata['messagetotal'] = 2
            self.compileddata.update(epsdata)
            self.compileddata.update(batterydata)
            self.compileddata.update(vutrxdata)
            self.compileddata.update(antsdata)
            self.compileddata.update(stxdata)

        else:

            self._errmsg = '\t\t\tLength of hex string must be equal to one of the following lengths: 112, 249, 163, 185'

        if self._errmsg != '':

            print(self._errmsg)
            self.compileddata = OrderedDict()

        return self.compileddata

    @staticmethod
    def _cleaninput(hstr, dlim):

        # Clean input
        hstr_cleaned = hstr.lower().strip().replace(' ', '').replace(dlim, '').replace('\t', '').replace('\r',
                                                                                                         '').replace(
            '\n', '')

        # Check length
        if len(hstr_cleaned) == 0:
            return [], '\t\t\tString is empty'

        # Check if the string contains anything except for hex values and the delimiter
        if ParseDownlink._validatehex(hstr_cleaned, dlim):
            return [], '\t\t\tInvalid character found in string'

        # Split hex string into list of bytes
        return [hstr_cleaned[i:i + 2] for i in range(0, len(hstr_cleaned), 2)], ''

    @staticmethod
    def _validatehex(hstr, dl=''):

        validhex = '0123456789abcdef' + dl.lower()
        return any(c not in validhex for c in hstr)  # Returns true if the str is not valid

    @staticmethod
    def _parsebinary(data, dtype, numbytes=1):

        # Bytes are read assuming little endian
        dtype = dtype.lower()
        if dtype == 'uint8':
            hexnum = ''.join([data[i] for i in reversed(range(1))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(1))]  # Remove used elements
            return int(hexnum, 16)  # Convert hex to numeric
        elif dtype == 'uint16':
            hexnum = ''.join([data[i] for i in reversed(range(2))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(2))]  # Remove used elements
            return int(hexnum, 16)  # Convert hex to numeric
        elif dtype == 'uint32':
            hexnum = ''.join([data[i] for i in reversed(range(4))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(4))]  # Remove used elements
            return int(hexnum, 16)  # Convert hex to numeric
        elif dtype == 'uint':  # Allows for a specified number of bytes (defaults to 1 byte bool)
            hexnum = ''.join(
                [data[i] for i in reversed(range(numbytes))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(numbytes))]  # Remove used elements
            return int(hexnum, 16)  # Convert hex to numeric
        elif dtype == 'int8':
            hexnum = ''.join([data[i] for i in reversed(range(1))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(1))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to integer
            if num >= 2 ** 7:  # Check for the sign
                num -= 2 ** 8  # Account for the sign
            return num
        elif dtype == 'int16':
            hexnum = ''.join([data[i] for i in reversed(range(2))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(2))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to integer
            if num >= 2 ** 15:  # Check for the sign
                num -= 2 ** 16  # Account for the sign
            return num
        elif dtype == 'int32':
            hexnum = ''.join([data[i] for i in reversed(range(4))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(4))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to integer
            if num >= 2 ** 31:  # Check for the sign
                num -= 2 ** 32  # Account for the sign
            return num
        elif dtype == 'int':  # Allows for a specified number of bytes (defaults to 1 byte bool)
            hexnum = ''.join(
                [data[i] for i in reversed(range(numbytes))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(numbytes))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to integer
            if num >= 2 ** (numbytes * 8 - 1):  # Check for the sign
                num -= 2 ** (numbytes * 8)  # Account for the sign
            return num
        elif dtype == 'bool8':
            hexnum = ''.join([data[i] for i in reversed(range(1))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(1))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to numeric
            nleadingzeros = numbytes * 8 + 2 - len(
                bin(num))  # Count the number of leading zeros necessary to complete the list of bits
            return [int(char) for char in
                    list('0' * nleadingzeros + bin(num)[2:])[::-1]]  # Place bit flag values in a list
        elif dtype == 'bool16':
            hexnum = ''.join([data[i] for i in reversed(range(2))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(2))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to numeric
            nleadingzeros = numbytes * 8 + 2 - len(
                bin(num))  # Count the number of leading zeros necessary to complete the list of bits
            return [int(char) for char in
                    list('0' * nleadingzeros + bin(num)[2:])[::-1]]  # Place bit flag values in a list
        elif dtype == 'bool32':
            hexnum = ''.join([data[i] for i in reversed(range(4))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(4))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to numeric
            nleadingzeros = numbytes * 8 + 2 - len(
                bin(num))  # Count the number of leading zeros necessary to complete the list of bits
            return [int(char) for char in
                    list('0' * nleadingzeros + bin(num)[2:])[::-1]]  # Place bit flag values in a list
        elif dtype == 'bool':  # Allows for a specified number of bytes (defaults to 1 byte bool)
            hexnum = ''.join(
                [data[i] for i in reversed(range(numbytes))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(numbytes))]  # Remove used elements
            num = int(hexnum, 16)  # Convert hex to numeric
            nleadingzeros = numbytes * 8 + 2 - len(
                bin(num))  # Count the number of leading zeros necessary to complete the list of bits
            return [int(char) for char in
                    list('0' * nleadingzeros + bin(num)[2:])[::-1]]  # Place bit flag values in a list
        elif dtype == 'single':
            hexnum = ''.join([data[i] for i in reversed(range(4))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(4))]  # Remove used elements
            return ParseDownlink.hextofloat(hexnum)  # Convert hex to numeric
        elif dtype == 'double':
            hexnum = ''.join([data[i] for i in reversed(range(8))])  # Read and concatenate hex bytes in reverse order
            [data.pop(i) for i in reversed(range(8))]  # Remove used elements
            return ParseDownlink.hextodouble(hexnum)  # Convert hex to numeric

    @staticmethod
    def _cdh(hexarray):
        from collections import OrderedDict

        ordict = OrderedDict()
        ordict['cdh_deployment_isis'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_deployment_solarpanel'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_deployment_magnetometer'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_deployment_payload'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_deployment_magnetometer_deployattempts'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        hexarray.pop(0)  # 1 byte padding
        ordict['cdh_bootcounter'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['cdh_programduration'] = ParseDownlink._parsebinary(hexarray, 'uint32')
        ordict['cdh_deployment_satellite'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_currentmode'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_temperature_obc'] = \
            ParseDownlink._parsebinary(hexarray, 'uint32') / 100000000  # Division converts uint32 to single/float32
        ordict['cdh_temperature_motor'] = \
            ParseDownlink._parsebinary(hexarray, 'uint32') / 100000000  # Division converts uint32 to single/float32
        ordict['cdh_temperature_vlf'] = \
            ParseDownlink._parsebinary(hexarray, 'uint32') / 100000000  # Division converts uint32 to single/float32
        [hexarray.pop(0) for _ in range(2)]  # 2 byte padding
        ordict['cdh_usage_cpu'] = ParseDownlink._parsebinary(hexarray, 'single') * 100
        ordict['cdh_usage_memory'] = ParseDownlink._parsebinary(hexarray, 'single') / 1024 / 1024
        ordict['cdh_usage_camera'] = ParseDownlink._parsebinary(hexarray, 'uint32')
        ordict['cdh_usage_science'] = ParseDownlink._parsebinary(hexarray, 'uint32')
        ordict['cdh_batterythreshold_safe'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_batterythreshold_low'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_batterythreshold_critical'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_beacon_state'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_downlink_status'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_downlink_frequency'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['cdh_beacon_frequency_tx'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['cdh_beacon_frequency_rx'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['cdh_beacon_lastuplinktime'] = ParseDownlink._parsebinary(hexarray, 'uint32')
        ordict['cdh_downlink_scienceradio'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_downlink_imageradio'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_beacon_speed'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['cdh_downlink_vutrxpower'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_downlink_stxpower'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_scienceready'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_memsmultiplier'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_detumblestate'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_angularestimator'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_controlmode'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        hexarray.pop(0)  # 1 byte padding
        ordict['cdh_detumble_angularthreshold_high_x'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_angularthreshold_high_y'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_angularthreshold_high_z'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_angularthreshold_low_x'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_angularthreshold_low_y'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_angularthreshold_low_z'] = ParseDownlink._parsebinary(hexarray, 'single')
        ordict['cdh_detumble_flag_tle'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_flag_ymomentum'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['cdh_detumble_flag_ywheel'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        hexarray.pop(0)  # 1 byte padding
        ordict['cdh_detumble_flag_previouscontrolonset'] = ParseDownlink._parsebinary(hexarray, 'uint32')

        return ordict

    @staticmethod
    def _adac(hexarray):
        from collections import OrderedDict

        ordict = OrderedDict()

        # 1 Byte of bit flags
        bitflags_bootstatus = ParseDownlink._parsebinary(hexarray, 'bool', 1)
        ordict['adac_bootstatus_newselection'] = bitflags_bootstatus[0]
        ordict['adac_bootstatus_bootsuccess'] = bitflags_bootstatus[1]
        ordict['adac_bootstatus_failedbootattempt_1'] = bitflags_bootstatus[2]
        ordict['adac_bootstatus_failedbootattempt_2'] = bitflags_bootstatus[3]
        ordict['adac_bootstatus_failedbootattempt_3'] = bitflags_bootstatus[4]

        ordict['adac_bootcounter'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_secondssinceboot'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_latchup_sram_1'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_latchup_sram_2'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_error_edac_single'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_error_edac_double'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['adac_error_edac_multiple'] = ParseDownlink._parsebinary(hexarray, 'uint16')

        # 6 Bytes of bit flags
        bitflags_currentstate = ParseDownlink._parsebinary(hexarray, 'bool', 6)
        ordict['adac_currentstate_mode_attitudeestimation'] = bitflags_currentstate[0]
        ordict['adac_currentstate_mode_control'] = bitflags_currentstate[1]
        ordict['adac_currentstate_mode_adcsrun'] = bitflags_currentstate[2]
        ordict['adac_currentstate_enable_cubecontrol_signal'] = bitflags_currentstate[3]
        ordict['adac_currentstate_enable_cubecontrol_motor'] = bitflags_currentstate[4]
        ordict['adac_currentstate_enable_cubesense'] = bitflags_currentstate[5]
        ordict['adac_currentstate_enable_cubewheel_1'] = bitflags_currentstate[6]
        ordict['adac_currentstate_enable_cubewheel_2'] = bitflags_currentstate[7]
        ordict['adac_currentstate_enable_cubewheel_3'] = bitflags_currentstate[8]
        ordict['adac_currentstate_enable_cubestar'] = bitflags_currentstate[9]
        ordict['adac_currentstate_enable_gpsreceiver'] = bitflags_currentstate[10]
        ordict['adac_currentstate_enable_gpslnapower'] = bitflags_currentstate[11]
        ordict['adac_currentstate_enable_motordriver'] = bitflags_currentstate[12]
        ordict['adac_currentstate_sunabovehorizon'] = bitflags_currentstate[13]
        ordict['adac_currentstate_error_cubesense_communication'] = bitflags_currentstate[14]
        ordict['adac_currentstate_error_cubecontrol_signalcommunications'] = bitflags_currentstate[15]
        ordict['adac_currentstate_error_cubecontrol_motorcommunication'] = bitflags_currentstate[16]
        ordict['adac_currentstate_error_cubewheel_communication_1'] = bitflags_currentstate[17]
        ordict['adac_currentstate_error_cubewheel_communication_2'] = bitflags_currentstate[18]
        ordict['adac_currentstate_error_cubewheel_communication_3'] = bitflags_currentstate[19]
        ordict['adac_currentstate_error_cubestar_communication'] = bitflags_currentstate[20]
        ordict['adac_currentstate_error_magnetometer_range'] = bitflags_currentstate[21]
        ordict['adac_currentstate_error_sunsensor_overcurrent'] = bitflags_currentstate[22]
        ordict['adac_currentstate_error_sunsensor_busy'] = bitflags_currentstate[23]
        ordict['adac_currentstate_error_sunsensor_detection'] = bitflags_currentstate[24]
        ordict['adac_currentstate_error_sunsensor_range'] = bitflags_currentstate[25]
        ordict['adac_currentstate_error_nadirsensor_overcurrent'] = bitflags_currentstate[26]
        ordict['adac_currentstate_error_nadirsensor_busy'] = bitflags_currentstate[27]
        ordict['adac_currentstate_error_nadirsensor_detection'] = bitflags_currentstate[28]
        ordict['adac_currentstate_error_nadirsensor_range'] = bitflags_currentstate[29]
        ordict['adac_currentstate_error_ratesensor_range'] = bitflags_currentstate[30]
        ordict['adac_currentstate_error_wheelspeed_range'] = bitflags_currentstate[31]
        ordict['adac_currentstate_error_coarsesunsensor'] = bitflags_currentstate[32]
        ordict['adac_currentstate_error_startracker_match'] = bitflags_currentstate[33]
        ordict['adac_currentstate_error_startracker_overcurrent'] = bitflags_currentstate[34]
        ordict['adac_currentstate_invalid_orbitparameters'] = bitflags_currentstate[35]
        ordict['adac_currentstate_invalid_configuration'] = bitflags_currentstate[36]
        ordict['adac_currentstate_invalid_controlmodechange'] = bitflags_currentstate[37]
        ordict['adac_currentstate_invalid_estimatorchange'] = bitflags_currentstate[38]
        ordict['adac_currentstate_error_magneticfield_modelmeasurementdisagree'] = bitflags_currentstate[39]
        ordict['adac_currentstate_error_noderecovery'] = bitflags_currentstate[40]

        ordict['adac_estimated_roll'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_pitch'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_yaw'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_angularrate_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_angularrate_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_angularrate_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_position_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_position_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_position_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_velocity_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_velocity_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_velocity_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.25
        ordict['adac_estimated_magneticfield_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_magneticfield_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_magneticfield_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_estimated_sunvector_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.0001
        ordict['adac_estimated_sunvector_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.0001
        ordict['adac_estimated_sunvector_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.0001
        ordict['adac_measured_angularrate_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_measured_angularrate_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_measured_angularrate_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.01
        ordict['adac_measured_wheel_x'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_measured_wheel_y'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_measured_wheel_z'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_magnetorquer_commands_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 10
        ordict['adac_magnetorquer_commands_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 10
        ordict['adac_magnetorquer_commands_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 10
        ordict['adac_ywheel_command'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_raw_sunsensor_xpos'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_sunsensor_ypos'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_sunsensor_zpos'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_sunsensor_xneg'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_sunsensor_yneg'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_sunsensor_zneg'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_raw_magnetometer_x'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_raw_magnetometer_y'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_raw_magnetometer_z'] = ParseDownlink._parsebinary(hexarray, 'int16')
        ordict['adac_current_3v3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.48828125
        ordict['adac_current_5v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.48828125
        ordict['adac_current_vbat'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.48828125
        ordict['adac_current_ywheel'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.01
        ordict['adac_temperature_mcu'] = ParseDownlink._parsebinary(hexarray, 'int16') * 1
        ordict['adac_temperature_magnetometer'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.1
        ordict['adac_temperature_ratesensor_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 1
        ordict['adac_temperature_ratesensor_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 1
        ordict['adac_temperature_ratesensor_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 1
        ordict['adac_gpsstatus_solutionstatus'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gpsstatus_trackedsatellites'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gpsstatus_usedsatellites'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gpsstatus_xyzlofcounter'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gpsstatus_rangelogcounter'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gpsstatus_responsemessage'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['adac_gps_time'] = \
            ParseDownlink._parsebinary(hexarray, 'uint32') / 1000 + 315964800 + \
            (ParseDownlink._parsebinary(hexarray, 'uint16') + 2048) * 7 * 24 * 60 * 60
        ordict['adac_gps_position_x'] = ParseDownlink._parsebinary(hexarray, 'int32') * 0.001
        ordict['adac_gps_velocity_x'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.001
        ordict['adac_gps_position_y'] = ParseDownlink._parsebinary(hexarray, 'int32') * 0.001
        ordict['adac_gps_velocity_y'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.001
        ordict['adac_gps_position_z'] = ParseDownlink._parsebinary(hexarray, 'int32') * 0.001
        ordict['adac_gps_velocity_z'] = ParseDownlink._parsebinary(hexarray, 'int16') * 0.001

        return ordict

    @staticmethod
    def _eps(hexarray):
        from collections import OrderedDict

        ordict = OrderedDict()
        ordict['eps_output_current_bcr'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 14.662757
        ordict['eps_output_voltage_bcr'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.008993157
        ordict['eps_output_current_12v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.00207
        ordict['eps_output_voltage_12v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.01349
        ordict['eps_output_current_bat'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005237
        ordict['eps_output_voltage_bat'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.008978
        ordict['eps_output_current_5v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005237
        ordict['eps_output_voltage_5v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005865
        ordict['eps_output_current_3v3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005237
        ordict['eps_output_voltage_3v3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.004311
        ordict['eps_temperature_motherboard'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.372434 - 273.15
        ordict['eps_temperature_daughterboard'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.372434 - 273.15
        ordict['eps_currentdraw_3v3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001327547
        ordict['eps_currentdraw_5v'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001327547
        ordict['eps_switchbus_voltage_motor'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.01349
        ordict['eps_switchbus_current_motor'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_hstx'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.008993
        ordict['eps_switchbus_current_hstx'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.006239
        ordict['eps_switchbus_voltage_camera'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005865
        ordict['eps_switchbus_current_camera'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_adac5'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005865
        ordict['eps_switchbus_current_adac5'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_vlf'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.005865
        ordict['eps_switchbus_current_vlf'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_ants'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.004311
        ordict['eps_switchbus_current_ants'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_adac3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.004311
        ordict['eps_switchbus_current_adac3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_switchbus_voltage_gps'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.004311
        ordict['eps_switchbus_current_gps'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.001328
        ordict['eps_bcr1_temperature_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr1_temperature_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr1_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0322581
        ordict['eps_bcr1_current'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr2_temperature_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr2_temperature_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr2_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0322581
        ordict['eps_bcr2_current_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr2_current_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr3_temperature_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr3_temperature_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.4963 - 273.15
        ordict['eps_bcr3_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0099706
        ordict['eps_bcr3_current_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr3_current_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr4_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0322581
        ordict['eps_bcr4_current_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr4_current_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr6_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0322581
        ordict['eps_bcr6_current_a'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775
        ordict['eps_bcr6_current_b'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.0009775

        # 2 Byte of bit flags
        bitflags_pdmstate = ParseDownlink._parsebinary(hexarray, 'bool', 2)
        ordict['eps_pdmstate_vlf_12v'] = bitflags_pdmstate[1]
        ordict['eps_pdmstate_stx_bat'] = bitflags_pdmstate[3]
        ordict['eps_pdmstate_camera'] = bitflags_pdmstate[5]
        ordict['eps_pdmstate_adac_5v'] = bitflags_pdmstate[6]
        ordict['eps_pdmstate_vlf_5v'] = bitflags_pdmstate[7]
        ordict['eps_pdmstate_ants'] = bitflags_pdmstate[8]
        ordict['eps_pdmstate_adac_3v3'] = bitflags_pdmstate[9]
        ordict['eps_pdmstate_gps_3v3'] = bitflags_pdmstate[10]

        ordict['eps_reset_brownout_motherboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_brownout_daughterboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_software_motherboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_software_daughterboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_manual_motherboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_manual_daughterboard'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['eps_reset_watchdog'] = ParseDownlink._parsebinary(hexarray, 'uint16')

        return ordict

    @staticmethod
    def _battery(hexarray):
        from collections import OrderedDict

        ordict = OrderedDict()
        ordict['battery_voltage'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.008993
        ordict['battery_current'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 14.662757 / 1000
        ordict['battery_temperature_motherboard'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.372434 - 273.15
        ordict['battery_temperature_daughterboard_1'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.3976 - 238.57
        ordict['battery_temperature_daughterboard_2'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.3976 - 238.57
        ordict['battery_temperature_daughterboard_3'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.3976 - 238.57
        ordict['battery_temperature_daughterboard_4'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 0.3976 - 238.57

        # 1 Byte of bit flags
        bitflags_heaterstatus = ParseDownlink._parsebinary(hexarray, 'bool', 1)
        ordict['battery_heaterstatus_1'] = bitflags_heaterstatus[0]
        ordict['battery_heaterstatus_2'] = bitflags_heaterstatus[1]
        ordict['battery_heaterstatus_3'] = bitflags_heaterstatus[2]
        ordict['battery_heaterstatus_4'] = bitflags_heaterstatus[3]

        return ordict

    @staticmethod
    def _vutrx(hexarray):
        from collections import OrderedDict

        def getkbits8(num, k, p):
            binary = bin(num)[2:]  # convert number into binary first
            leadingzeros = 8 - len(binary)  # Count the necessary leading zeros to fill byte
            binary = '0' * leadingzeros + binary  # Fill byte with leading zeros
            end = 8 - p - 1
            start = end - k + 1
            k_bit_sub_str = binary[start: end + 1]  # extract k  bit sub-string
            return int(k_bit_sub_str, 2)  # convert extracted sub-string into decimal again

        ordict = OrderedDict()
        ordict['vutrx_rx_failedpackage'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['vutrx_rx_crcfailedpackage'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['vutrx_rx_packagecounter'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        frequentlock = ParseDownlink._parsebinary(hexarray, 'uint8')  # Get whole register
        ordict['vutrx_rx_frequentlock'] = getkbits8(frequentlock, 1, 0)  # Split register by bit position
        ordict['vutrx_tx_frequentlock'] = getkbits8(frequentlock, 1, 1)
        ordict['vutrx_rssi'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 3 / 4096
        ordict['vutrx_smps_temperature'] = ParseDownlink._parsebinary(hexarray, 'int8')
        ordict['vutrx_poweramplifier_temperature'] = ParseDownlink._parsebinary(hexarray, 'int8')
        ordict['vutrx_poweramplifier_power'] = ParseDownlink._parsebinary(hexarray, 'uint8')
        ordict['vutrx_frequencyoffset_tx'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['vutrx_frequencyoffset_rx'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        dtmf = ParseDownlink._parsebinary(hexarray, 'uint8')  # Get whole register
        ordict['vutrx_dtmf_tone'] = getkbits8(dtmf, 4, 0)  # Split register by bit position
        ordict['vutrx_dtmf_counter'] = getkbits8(dtmf, 4, 4)
        ordict['vutrx_current_3v3'] = ParseDownlink._parsebinary(hexarray, 'int16') * 3e-6
        ordict['vutrx_current_5v'] = ParseDownlink._parsebinary(hexarray, 'int16') * 62e-6
        ordict['vutrx_voltage_3v3'] = ParseDownlink._parsebinary(hexarray, 'int16') * 4e-3
        ordict['vutrx_voltage_5v'] = ParseDownlink._parsebinary(hexarray, 'int16') * 4e-3
        ordict['vutrx_poweramplifier_forwardpower'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 3 / 4096
        ordict['vutrx_poweramplifier_reversepower'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 3 / 4096

        return ordict

    @staticmethod
    def _stx(hexarray):
        from collections import OrderedDict

        def getkbits8(num, k, p):
            binary = bin(num)[2:]  # convert number into binary first
            leadingzeros = 8 - len(binary)  # Count the necessary leading zeros to fill byte
            binary = '0' * leadingzeros + binary  # Fill byte with leading zeros
            end = 8 - p - 1
            start = end - k + 1
            k_bit_sub_str = binary[start: end + 1]  # extract k  bit sub-string
            return int(k_bit_sub_str, 2)  # convert extracted sub-string into decimal again

        ordict = OrderedDict()
        ordict['stx_voltage_battery'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 4e-3
        ordict['stx_current_battery'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 40e-6
        ordict['stx_voltage_poweramplifier'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 4e-3
        ordict['stx_current_poweramplifier'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 40e-6
        ordict['stx_temperature_top'] = getkbits8(ParseDownlink._parsebinary(hexarray, 'int16'), 12, 4) * 0.0625
        ordict['stx_temperature_bottom'] = getkbits8(ParseDownlink._parsebinary(hexarray, 'int16'), 12, 4) * 0.0625
        ordict['stx_temperature_poweramplifier'] = \
            ((ParseDownlink._parsebinary(hexarray, 'uint8') * 3 / 4096) - 0.5) * 100
        ordict['stx_synth_offset'] = ParseDownlink._parsebinary(hexarray, 'uint8') * 0.5 + 2400
        ordict['stx_buffer_overrun'] = ParseDownlink._parsebinary(hexarray, 'uint16')
        ordict['stx_buffer_underrun'] = ParseDownlink._parsebinary(hexarray, 'uint16')

        # 1 Byte of bit flags
        bitflags_pastatus = ParseDownlink._parsebinary(hexarray, 'bool', 1)
        ordict['stx_poweramplifier_status_frequencylock'] = bitflags_pastatus[0]
        ordict['stx_poweramplifier_status_powergood'] = bitflags_pastatus[1]

        ordict['stx_rf_poweroutput'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 3 * 28 / 4096 / 18

        return ordict

    @staticmethod
    def _ants(hexarray):
        from collections import OrderedDict

        ordict = OrderedDict()
        ordict['ants_temperature'] = ParseDownlink._parsebinary(hexarray, 'uint16') * 3.3 / 1023

        # 2 Bytes of bit flags
        bitflags_antsstatus = ParseDownlink._parsebinary(hexarray, 'bool', 2)
        ordict['ants_status_armed'] = bitflags_antsstatus[0]
        ordict['ants_status_deploymentactive_4'] = bitflags_antsstatus[1]
        ordict['ants_status_stopcriteria_4'] = bitflags_antsstatus[2]
        ordict['ants_status_deploymentflag_4'] = bitflags_antsstatus[3]
        ordict['ants_status_independentburn'] = bitflags_antsstatus[4]
        ordict['ants_status_deploymentactive_3'] = bitflags_antsstatus[5]
        ordict['ants_status_stopcriteria_3'] = bitflags_antsstatus[6]
        ordict['ants_status_deploymentflag_3'] = bitflags_antsstatus[7]
        ordict['ants_status_ignoreswitches'] = bitflags_antsstatus[8]
        ordict['ants_status_deploymentactive_2'] = bitflags_antsstatus[9]
        ordict['ants_status_stopcriteria_2'] = bitflags_antsstatus[10]
        ordict['ants_status_deploymentflag_2'] = bitflags_antsstatus[11]
        ordict['ants_status_deploymentactive_1'] = bitflags_antsstatus[13]
        ordict['ants_status_stopcriteria_1'] = bitflags_antsstatus[14]
        ordict['ants_status_deploymentflag_1'] = bitflags_antsstatus[15]

        return ordict

    @staticmethod
    def hextofloat(h, swap=False):
        import string
        if not isinstance(h, str):
            raise TypeError
        if not h.startswith('0x'):
            h = '0x' + h
        if not all(c in string.hexdigits.lower() for c in h[2:]):
            raise ValueError
        if swap:
            h = '0x' + ''.join(reversed([h[2:][i:i + 2] for i in range(0, len(h[2:]), 2)]))

        i = int(h[2:], 16)  # Convert hex to int
        b = bin(i)  # Convert int to binary
        b = b[2:].zfill(32)  # Pad binary to fill all 32 bits

        sign = 1 if int(b[0], 2) == 0 else -1
        exponent = int(b[1:9], 2)
        mantissa = b[9:]
        mval = 1
        for i in range(len(mantissa)):
            if mantissa[i] == '1':
                mval += 2 ** (-(i + 1))

        return sign * 2 ** (exponent - 127) * mval

    @staticmethod
    def hextodouble(h, swap=False):
        import string
        if not isinstance(h, str):
            raise TypeError
        if not h.startswith('0x'):
            h = '0x' + h
        if not all(c in string.hexdigits.lower() for c in h[2:]):
            raise ValueError
        if swap:
            h = '0x' + ''.join(reversed([h[2:][i:i + 2] for i in range(0, len(h[2:]), 2)]))

        i = int(h[2:], 16)  # Convert hex to int
        b = bin(i)  # Convert int to binary
        b = b[2:].zfill(64)  # Pad binary to fill all 32 bits

        sign = 1 if int(b[0], 2) == 0 else -1
        exponent = int(b[1:12], 2)
        mantissa = b[12:]
        mval = 1
        for i in range(len(mantissa)):
            if mantissa[i] == '1':
                mval += 2 ** (-(i + 1))

        return sign * 2 ** (exponent - 1023) * mval


def main():
    import os
    import datetime

    options = docopt(__doc__, version='1.0.10')  # parse options based on docstring above

    print('SwampSat II Beacon Parser (UF CubeSat)\n')

    # Look for either a file path or raw HEX string
    mode = 0
    if options['--file'] is not None and len(options['--file']) > 0:
        mode |= 1
        file = os.path.normcase(options['--file'])
    else:
        file = ''

    if options['--hexstring'] is not None and len(options['--hexstring']) > 0:
        mode |= 2
        hexstring = options['--hexstring']
    else:
        hexstring = ''

    # Raise an error if no input is found
    if mode == 0:
        raise IOError('A filepath or raw HEX string is required')

    # Raise an error if both inputs were provided together
    elif mode == 3:
        raise IOError('A file path and hex string were provided, only provide one at a time')

    # Check if the logpath is equal to its default value
    islogdefault = options['--logfile'] == '[$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json'

    # Normalize the logpath
    lpath = os.path.normcase(options['--logfile'])

    if islogdefault:

        # If the default logpath is used and a file was supplied, place the logfile in the same folder as the specified file
        if mode == 1:

            fname = os.path.split(os.path.splitext(file)[0])[1]  # File name without extension
            fpath = os.path.split(file)[0]  # Parent path of file
            logdir = '\\ss2logs\\'  # Path to log directory
            fext = '.json'  # File extension
            fsuffix = '_parsed'  # File name suffix
            lpath = fpath + logdir + fname + fsuffix + fext  # Put log path parts together
            lpath = os.path.normcase(lpath)  # Normalize the new logpath

        # If the default logpath is used and a string was supplied, place the log path in the home folder
        elif mode == 2:

            lpath = lpath.replace(os.path.normcase('[$HOME]'), os.path.expanduser('~'))  # Replace the $HOME placeholder with the OS/user corrected home folder

    else:

        # Check if a directory was specified by looking for a file extension
        if os.path.splitext(lpath)[1] == '' or os.path.isdir(lpath):

            # Create a filename at the specified directory
            ppath = os.path.join(lpath, '')
            lpath = ppath + os.path.normcase('ss2beacon_parsed_[$TIMESTAMP].json')

    # Replace the $HOME placeholder with the OS/user corrected home folder
    lpath = lpath.replace(os.path.normcase('[$HOME]'), os.path.expanduser('~'))

    # Add a timestamp to the file if the "[$TIMESTAMP]" marker still exists
    lpath = lpath.replace(os.path.normcase('[$TIMESTAMP]'), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

    # Make directory path to the logfile, if it doesn't already exist
    try:
        os.makedirs(os.path.split(lpath)[0], exist_ok=True)
    except OSError:
        pass

    # Look for additional (optional) parameters
    if options['--delimiter'] is not None and len(options['--delimiter']) > 0:
        delimiter = options['--delimiter'].lower()
    else:
        delimiter = ''

    # If a raw HEX string was provided
    if mode == 2:

        # Call the parser
        output = ParseDownlink.parserecord(hexstring, lpath, delimiter)

        # Check for parsed data
        if len(output) > 0:
            print('\tString successfully read')
            print('\tLog file created:', lpath)
        else:
            print('\tProvided string is not valid')

    # If a file path was provided
    elif mode == 1:

        fpath = os.path.normcase(file.strip())
        counter = 0
        with open(fpath, 'rt', encoding='utf-8') as r:
            for line in r:

                # Call the parser
                output = ParseDownlink.parserecord(line, lpath, delimiter)

                # Check for parsed data
                if len(output) > 0:
                    print('\t\tLine successfully read')
                    counter += 1
                else:
                    print('\t\tInvalid line')
        print('\r\n\tSuccessfully read: ' + str(counter) + ' lines from file')
        if counter > 0:
            print('\tLog file created:', lpath)


if __name__ == "__main__":
    main()