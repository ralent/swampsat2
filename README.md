# README



## COMPATIBLE PLATFORMS


Windows

Linux



## INSTALL


On Windows or Linux, the following command will install the python package:

	pip3 install swampsat2

On Linux systems, the sudo priviledge can be circumvented with the follow command which downloads the package to the local user path by default `$HOME/.local/bin/*`:

	pip3 install --user swampsat2

If `pip` is not installed on your system it can be installed with one of the following approaches:

**Windows:**

`pip` is often packaged with python on Windows and a standard installation of python will include `pip`

**Linux:**

Run the following command on linux to install `pip`:

	sudo apt-get install python3-pip



## NOTES


The SwampSat II beacon parser utility is implemented in Python and can be called from command-line. The input/data, whether a string or file containing strings, must be in HEX


**HEX String Formatting**

- All whitespace is ignored

- Parsing is case insensitive

- Strings must contain only HEX characters [0-9, A-F]

- The header containing the callsigns should **not** be included in the string

- Strings are identified by number of bytes included; valid lengths are {163, 185, and 46} bytes


**Example strings**

	12 00 94 03 02 00 7B 03 02 00 93 03 26 00 5B 03 19 00 05 03 09 03 0F 03 12 00 17 00 28 00 02 00 03 00 02 00 03 00 02 00 5B 03 02 00 02 00 03 00 05 03 06 00 05 03 0E 00 04 03 1D 00 27 02 4D 02 29 01 05 00 39 02 81 02 3F 01 1C 00 74 00 27 02 6A 02 18 02 02 00 0F 00 51 01 01 00 05 00 18 01 09 00 57 00 00 40 82 00 77 00 84 00 00 00 3C 00 3C 00 D3 00 FF 03 1B 80 06 03 FF 03 E3 02 E8 02 EA 02 01 00 01 00 11 00 03 9F 06 0E 0C 02 D6 01 FE 00 0F DE 46 06 00 3A 03 E8 04 74 01 61 01 3E 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

**OR**

	1400940302007C03 030093031D005B03 190005030B031103 1200170028000300 0300020003000300 5B03020002000300 0403060004030E00 04031C0027024B02 36011A003D027802 41012D004C002202 7E02110202000400 1C0115001E001701 1900140000408200 7700840000003C00 3C00D300FF031480 0603FF03E502EA02 EA02010001001100 033D050F0D02D601 FE000FAF4600003A 03E804740160012F 0200000000000000 0000000000000000 0000000000000000 00



## USAGE: COMMAND-LINE


Usage:

	swampsat2 [-i] [-l LOGFILE] [-t FILETYPE] [-d DELIMITER] [-f FILE]
	
	swampsat2 [-i] [-l LOGFILE] [-t FILETYPE] [-d DELIMITER] [-s HEXSTRING]

Parse SwampSat II beacons from either a file or command-line string

Options:

	-f FILE, --file=FILE  input file containing hex strings from a SwampSat II beacon

	-s HEXSTRING, --hexstring=HEXSTRING  hex string from a SwampSat II beacon

	-l LOGFILE, --logfile=LOGFILE  file where parsed data will be saved [default: [$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json]

	-t FILETYPE, --filetype=FILETYPE     file type of input file (default behavior is to read the file extension, valid extensions are: '.txt', '.log', '.kss')

	-i, --image                          flag to read data as jpg image (log name remains the same as default but a .jpg file extension is added)

	-d DELIMITER, --delimiter=DELIMITER  delimiter for input HEX string (whitespace is automatically removed)

	-h --help  prints this help message

	--version  prints current version


---

**Options Flag `FILETYPE`:**

The `FILETYPE` option let's you provide the file type the parser should expect

The parser can accept either `.log`, `.txt` or `.kss` files (`.log` and `.txt` are treated the same)

The default behavior is to read the file type from the file path; thus this flag should usually not be necessary

Examples of acceptable files can be found on GitHub: `github.com/ralent/swampsat2`

**Options Flag `image`:**

You should use this flag if you expect your file to have image data (JPG); this flag will try to parse an image from the data in the file

The default log path remains the same except that the file is saved with a `.jpg` extension

**Options Flag `DELIMITER`:**

Whitespace is ignored in any HEX strings so there is no need to specify a whitespace delimiter

If there are additional delimiters, such as a comma, then they can be specified using the delimiter flag (*example for comma delimiting*: `-d ','`)

**Options Flag `LOGFILE`:**

Specifying a `LOGFILE` path will ignore the following default behaviors except for placeholder substitutions

- Default `LOGFILE` path when used with `FILE` flag


	[FILE_PATH]/ss2logs/[FILE_NAME]_parsed.json


- Default `LOGFILE` path when used with `HEXSTRING` flag


	[$HOME]/ss2logs/ss2beacon_parsed_[$TIMESTAMP].json

- Default filename when `LOGFILE` is a directory


	[LOGFILE]/ss2beacon_parsed_[$TIMESTAMP].json


Regardless of the above default behavior, the following placeholders will always be substituted for the following values:

- The placeholder `[$HOME]` is substuted with the home directory adjusted for the current OS and User
- The placeholder `[$TIMESTAMP]` is substuted with the current datetime in the following format: `%Y-%m-%d_%H-%M-%S`

---


Example parsing data with HEX string (*Windows* and *Linux* respectively):

	swampsat2 -s "        1400940302007C03 030093031D005B03 190005030B031103 1200170028000300 0300020003000300 5B03020002000300 0403060004030E00 04031C0027024B02 36011A003D027802 41012D004C002202 7E02110202000400 1C0115001E001701 1900140000408200 7700840000003C00 3C00D300FF031480 0603FF03E502EA02 EA02010001001100 033D050F0D02D601 FE000FAF4600003A 03E804740160012F 0200000000000000 0000000000000000 0000000000000000 00"

	swampsat2 -s '        1400940302007C03 030093031D005B03 190005030B031103 1200170028000300 0300020003000300 5B03020002000300 0403060004030E00 04031C0027024B02 36011A003D027802 41012D004C002202 7E02110202000400 1C0115001E001701 1900140000408200 7700840000003C00 3C00D300FF031480 0603FF03E502EA02 EA02010001001100 033D050F0D02D601 FE000FAF4600003A 03E804740160012F 0200000000000000 0000000000000000 0000000000000000 00'


---


Example parsing data from file (*Windows* and *Linux* respectively):

	swampsat2 -f "<filepath>/beacondata.txt"

	swampsat2 -f '<filepath>/beacondata.txt'


---


Example parsing data from file and specifying a log file path (*Windows* and *Linux* respectively):

	swampsat2 -l "ss2logs/ss2beacon_parsed_.json" -f "<filepath>/beacondata.txt"

	swampsat2 -l 'ss2logs/ss2beacon_parsed_.json' -f '<filepath>/beacondata.txt'

