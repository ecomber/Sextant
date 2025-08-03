import datetime
from zoneinfo import ZoneInfo

import astroCalculator
import sextant
from sextant import deg_to_dm

Logging = False

# Chosen Position for plotting sheet
CP_latitude_degrees = 37
CP_longitude_degrees = -9

observation_time = datetime.datetime(2025, 5, 29, 15, 19, 28, 914876, ZoneInfo('UTC'))

GHA_of_body_at_hour = (45 + 38.1/60) # GHA of Sun on the hour from Almanac (deg + min), increment is calculated
Declination_of_body_at_hour = (21 + 43.2/60) # of Observed Body, from Almanac.
Declination_d_correction = 0.4 # N.B. sign. + ve 21 December to 21 June for Sun, from Almanac.
# GHA and Decl increments are calculated (GHA at 15°/hr) and (Decl at 'd' * minutes)
# Enter Sun semi-diameter below

mySextant = sextant.Sextant()
mySextant.Hs = 50 + 58.1 /60 # uncorrected sextant reading (deg + min)
mySextant.index_error= +2.2 # (On - / Off +)
mySextant.eye_height = 2.5 # Cockpit = 2.5 Mast = 3.3
mySextant.semi_diameter = +15.8 # Varies, get from Almanac. negative for upper limb

# end of observation data
ac = astroCalculator.AstroCalculator()
mySextant.Calculate()
Ho = mySextant.Ho()

GHA_m_s_increment = observation_time.minute / 4 + observation_time.second / 240 # e.g. 4 arc' in 1 minute of time
GHA_of_body_degrees = GHA_of_body_at_hour + GHA_m_s_increment

LHA_of_body_degrees = (GHA_of_body_degrees + CP_longitude_degrees + 360) % 360
Declination_m_increment = observation_time.minute * Declination_d_correction/3600 # specified in minutes of arc
Declination_of_body_degrees = Declination_of_body_at_hour + Declination_m_increment

Z, Hc = ac.sightReduction(CP_latitude_degrees, Declination_of_body_degrees, LHA_of_body_degrees) # Z later corrected to Zn

observed_body = "Sun"

infoTable = []
infoTable.append("")
infoTable.append(f"Observed Body: {observed_body}")
infoTable.append(f"Observation time {observation_time} UTC")
infoTable.append(f"Calculation time {str(datetime.datetime.now(ZoneInfo('UTC')))} UTC")
infoTable.append("")

outputTable = []
outputTable.append(["",""])
outputTable.append([f"Position of {observed_body}:", ""])
outputTable.append([f"GHA of {observed_body} {observation_time.year}-{observation_time.month:02g}-{observation_time.day:02g} {observation_time.hour:02g}h (Almanac)",f"{deg_to_dm(GHA_of_body_at_hour%360)}", GHA_of_body_at_hour])
outputTable.append([f"GHA increment at {observation_time.minute}m {observation_time.second}s ",f"{deg_to_dm(GHA_m_s_increment)}"])
outputTable.append([f"GHA of {observed_body} at {observation_time.hour}h {observation_time.minute}m {observation_time.second}s",f"{deg_to_dm(GHA_of_body_degrees%360)}", GHA_of_body_degrees])
outputTable.append([f"Declination at {observation_time.hour}h (Almanac)",f"{deg_to_dm(Declination_of_body_at_hour)}"])
outputTable.append([f"Decl incr {Declination_d_correction} at {observation_time.minute}m (Almanac)",f"{deg_to_dm(Declination_m_increment)}"])
outputTable.append([f"Declination of {observed_body}",f"{deg_to_dm(Declination_of_body_degrees)}",Declination_of_body_degrees])

outputTable.append(["",""])
outputTable.append([f"Chosen Position:",""])
outputTable.append([f"CP Latitude",f"{deg_to_dm(CP_latitude_degrees)}", CP_latitude_degrees])
outputTable.append([f"CP Longitude",f"{deg_to_dm(CP_longitude_degrees)}", CP_longitude_degrees])
outputTable.append([f"LHA of {observed_body} (GHA + CP Lon)",f"{deg_to_dm(LHA_of_body_degrees)}", LHA_of_body_degrees])

outputTable.append(["",""])
outputTable.append([f"Hc calculated from CP lat, Decl, LHA",f"{deg_to_dm(Hc)}",Hc])
outputTable.append([f"Ho from sextant",f"{deg_to_dm(Ho)}",Ho])

if Ho > Hc:
	direction = "Towards"
else:
	direction = "Away"

outputTable.append([f"Intercept ({direction})",f"{deg_to_dm(Hc-Ho)}"])
outputTable.append([f"Intercept ({direction})",f"{abs((Hc-Ho)*60):5.2f} nm "])

if CP_latitude_degrees > 0: # North
	#outputTable.append(["Latitude North",""])
	if LHA_of_body_degrees > 180:
		#outputTable.append([" and LHA > 180°: Zn = Z",""])
		Zn = Z
	else:
		#outputTable.append([" and LHA < 180°: Zn = 360° - Z",""])
		Zn = 360 - Z
else: # South
	outputTable.append(["Latitude South",""])
	if LHA_of_body_degrees > 180:
		outputTable.append([" and LHA > 180°: Zn = 180° - Z",""])
		Zn = 180 - Z
	else:
		outputTable.append([" and LHA < 180°: Zn = 180° + Z",""])
		Zn = 180 + Z

outputTable.append([f"  Zn (Azimuth) {round(Zn)}°, LoP {round((Zn+90)%360)}°",""])

for row in infoTable:
	print(row)
tables = [mySextant.formattedTable(),outputTable]
column0_width = column1_width = 0 # get max column widths
for table in tables:
	for row in table:
		column0_width = max(len(row[0]), column0_width)
		column1_width = max(len(row[1]), column1_width)
for table in tables:
	for row in table:
		print(row[0].ljust(column0_width + 2), row[1].rjust(column1_width))

if Logging is True:
	OutFileName = "Logs/" + str(observation_time.strftime("%Y-%m-%d %Hh%Mm%Ss UTC")) + f" Sun.txt"
	# ':' not permitted in filename
	with open(OutFileName, "w", encoding="utf-8") as logfile:
		for row in infoTable:
			logfile.write(row + "\n")
		for row in mySextant.formattedTable():
			logfile.write(f"{row[0].ljust(column0_width + 2)}{row[1].rjust(column1_width)}\n")
		for row in outputTable:
			logfile.write(f"{row[0].ljust(column0_width + 2)}{row[1].rjust(column1_width)}\n")
