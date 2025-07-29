import datetime
from zoneinfo import ZoneInfo

import astroCalculator
import sextant
from sextant import deg_to_dm

Logging = False

EP_latitude_degrees = 37 # 37.00649000203111 # +37°00.39'
EP_longitude_degrees = -9 #-8.878539625348163 # -8°52.71'

# Suggested Chosen Position for plotting sheet, comment out to use GPS
#EP_latitude_degrees = 37.0 # +37°00.00'
#EP_longitude_degrees = -8.833333333333334 # -8°50.00'

observation_time = datetime.datetime(2025, 5, 29, 15, 19, 28, 914876, ZoneInfo('UTC'))

GHA_of_body_at_hour = (45 + 38.1/60) # GHA of Sun on the hour from Almanac (deg + min), increment is calculated

Declination_of_body_at_hour = (21 + 43.2/60) # of Observed Body, from Almanac.
Declination_d_correction = 0.4 # N.B. sign. + ve 21 December to 21 June for Sun.
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

LHA_of_body_degrees = (GHA_of_body_degrees + EP_longitude_degrees + 360) % 360
Declination_m_increment = observation_time.minute * Declination_d_correction/3600 # specified in minutes of arc
Declination_of_body_degrees = Declination_of_body_at_hour + Declination_m_increment

Z, Hc = ac.sightReduction(EP_latitude_degrees, Declination_of_body_degrees, LHA_of_body_degrees) # Z later corrected to Zn

infoTable = []
infoTable.append("")
infoTable.append(f"Observed Body: Sun")
infoTable.append(f"Observation time {observation_time} UTC")
infoTable.append(f"Calculation time {str(datetime.datetime.now(ZoneInfo('UTC')))} UTC")
infoTable.append("")

outputTable = []
outputTable.append(["",""])
outputTable.append([f"Estimated or Chosen Position:",""])
outputTable.append([f"EP Latitude",f"{deg_to_dm(EP_latitude_degrees)}",EP_latitude_degrees])
outputTable.append([f"EP Longitude",f"{deg_to_dm(EP_longitude_degrees)}", EP_longitude_degrees])

outputTable.append([f"GHA Sun {observation_time.year}-{observation_time.month:02g}-{observation_time.day:02g} {observation_time.hour:02g}h (Almanac)",f"{deg_to_dm(GHA_of_body_at_hour%360)}", GHA_of_body_at_hour])

outputTable.append([f"GHA increment at {observation_time.minute}m {observation_time.second}s ",f"{deg_to_dm(GHA_m_s_increment)}"])
outputTable.append([f"GHA of body at {observation_time.hour}h {observation_time.minute}m {observation_time.second}s",f"{deg_to_dm(GHA_of_body_degrees%360)}", GHA_of_body_degrees])
outputTable.append([f"LHA of body (GHA + EP Lon)",f"{deg_to_dm(LHA_of_body_degrees)}", LHA_of_body_degrees])
outputTable.append([f"Declination at {observation_time.hour}h (Almanac)",f"{deg_to_dm(Declination_of_body_at_hour)}"])
outputTable.append([f"Decl incr {Declination_d_correction} at {observation_time.minute}m (Almanac)",f"{deg_to_dm(Declination_m_increment)}"])
outputTable.append([f"Declination of body",f"{deg_to_dm(Declination_of_body_degrees)}",Declination_of_body_degrees])
outputTable.append(["",""])
outputTable.append([f"Hc from EP lat, Decl, LHA",f"{deg_to_dm(Hc)}",Hc])
outputTable.append([f"Ho from sextant",f"{deg_to_dm(Ho)}",Ho])

if Ho > Hc:
    direction = "Towards"
else:
    direction = "Away"

outputTable.append([f"Intercept ({direction})",f"{deg_to_dm(Hc-Ho)}"])
outputTable.append([f"Intercept ({direction})",f"{abs((Hc-Ho)*60):5.2f} nm "])

if EP_latitude_degrees > 0: # North
    #outputTable.append(["Latitude North",""])
    if LHA_of_body_degrees > 180:
        #outputTable.append([" and LHA > 180°: Zn = Z",""])
        Zn = Z
    else:
        #outputTable.append([" and LHA < 180°: Zn = 360° - Z",""])
        Zn = 360 - Z
else: # South
    outputTable.append("Latitude South","")
    if LHA_of_body_degrees > 180:
        outputTable.append(" and LHA > 180°: Zn = 180° - Z","")
        Zn = 180 - Z
    else:
        outputTable.append(" and LHA < 180°: Zn = 180° + Z","")
        Zn = 180 + Z

outputTable.append([f"  Zn (Azimuth) {round(Zn)}°, LoP {round((Zn+90)%360)}°",""])


for row in infoTable:
    print(row)

column0_width = column1_width = 0
for row in mySextant.formattedTable():
    column0_width = max(len(row[0]), column0_width)
    column1_width = max(len(row[1]), column1_width)

for row in outputTable:
    column0_width = max(len(row[0]), column0_width)
    column1_width = max(len(row[1]), column1_width)

for row in mySextant.formattedTable():
	print(row[0].ljust(column0_width+2), row[1].rjust(column1_width))
for row in outputTable:
	print(row[0].ljust(column0_width+2), row[1].rjust(column1_width))

if Logging is True:
	OutFileName = "Logs/" + str(observation_time.strftime("%Y-%m-%d %Hh%Mm%Ss UTC")) + f" Sun.txt"
	# ':' not permitted in filename
	with open(OutFileName, "w", encoding="utf-8") as sll:
		for row in infoTable:
			sll.write(f"{row[0].ljust(35)}{row[1].rjust(12)}\n")
		for row in mySextant.formattedTable():
			sll.write(f"{row[0].ljust(35)}{row[1].rjust(12)}\n")
		for row in outputTable:
			sll.write(f"{row[0].ljust(35)}{row[1].rjust(12)}\n")
