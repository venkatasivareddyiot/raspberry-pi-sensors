import sys
import time
import datetime

import Adafruit_BMP.BMP085 as BMP085
import gspread

# Google Docs account email, password, and spreadsheet name.
GDOCS_EMAIL            = 'your google docs account email address'
GDOCS_PASSWORD         = 'your google docs account password'
GDOCS_SPREADSHEET_NAME = 'your google docs spreadsheet name'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 30


def login_open_sheet(email, password, spreadsheet):
	"""Connect to Google Docs spreadsheet and return the first worksheet."""
	try:
		gc = gspread.login(email, password)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except:
		print 'Unable to login and get spreadsheet.  Check email, password, spreadsheet name.'
		sys.exit(1)


# Create sensor instance with default I2C bus (On Raspberry Pi either 0 or
# 1 based on the revision, on Beaglebone Black default to 1).
bmp = BMP085.BMP085()

print 'Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS)
print 'Press Ctrl-C to quit.'
worksheet = None
while True:
	# Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(GDOCS_EMAIL, GDOCS_PASSWORD, GDOCS_SPREADSHEET_NAME)

	# Attempt to get sensor readings.
	temp = bmp.read_temperature()
	pressure = bmp.read_pressure()
	altitude = bmp.read_altitude()

	print 'Temperature: {0:0.1f} C'.format(temp)
	print 'Pressure:    {0:0.1f} Pa'.format(pressure)
	print 'Altitude:    {0:0.1f} m'.format(altitude)
 
	# Append the data in the spreadsheet, including a timestamp
	try:
		worksheet.append_row((datetime.datetime.now(), temp, pressure, altitude))
	except:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print 'Append error, logging in again'
		worksheet = None
		time.sleep(FREQUENCY_SECONDS)
		continue

	# Wait 30 seconds before continuing
	print 'Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME)
	time.sleep(FREQUENCY_SECONDS)
