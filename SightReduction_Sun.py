import datetime
from zoneinfo import ZoneInfo

import astroCalculator
import sextant
from sextant import deg_to_dm, dm_tup_to_deg

Logging = True

# Chosen Position for plotting sheet.
# You could use your Dead Reckoning position, but plotting might be awkward.
# If you use your GPS position at time of sight the Intercept will be your observation error.
CP_latitude_degrees = 37
CP_longitude_degrees = -9

# Time of observation. Always UTC. If Time Zone info is omitted it is forced to UTC. Can accept e.g. microsecond=500000
observation_time = datetime.datetime(year=2025, month=5, day=29, hour=15, minute=19, second=28, tzinfo=ZoneInfo('UTC'))

# We need the following information from the Nautical Almanac,
# available at https://www.thenauticalalmanac.com
GHA_of_body_at_hour = 45, 38.1  # Almanac. GHA of Sun on the hour (degrees , minutes) sign of minutes is ignored
Declination_of_body_at_hour = 21, 43.2  # Almanac. Decl of Observed Body.
Declination_d_correction_per_hour = 0.4  # Almanac. N.B. sign. -ve 21 June to 21 December for Sun.

# GHA and Decl increments are calculated (GHA at 15°/hr) and (Decl at 'd' *  minutes of time)
# Enter Sun semi-diameter below

mySextant = sextant.Sextant()
mySextant.Hs = 50, 58.1  # Uncorrected sextant reading (degrees , minutes) sign of minutes is ignored
mySextant.index_error = +2.2  # Minutes of arc (On - / Off +)
mySextant.eye_height = 2.5  # Cockpit = 2.5 Mast = 3.3
mySextant.semi_diameter = +15.8  # Almanac. Minutes of arc. Varies. Negative for upper limb.

# end of user observation data. Run the program with:  >python3 SightReduction_Sun.py [ >Output.txt ]

if observation_time.tzinfo != ZoneInfo('UTC'):
    print("Warning - observation_time TZ not was not set to UTC, has now been set to UTC.")
    print("Put tzinfo=ZoneInfo('UTC') as the last parameter in the observation_time declaration.")
    observation_time.replace(tzinfo=ZoneInfo('UTC'))

# convert tuples to decimal degrees
GHA_of_body_at_hour = dm_tup_to_deg(GHA_of_body_at_hour)
Declination_of_body_at_hour = dm_tup_to_deg(Declination_of_body_at_hour)
mySextant.Hs = dm_tup_to_deg(mySextant.Hs)
ac = astroCalculator.AstroCalculator()
mySextant.Calculate()
Ho = mySextant.Ho()

GHA_m_s_increment = observation_time.minute / 4 + observation_time.second / 240  # e.g. 4 arc' in 1 minute of time
GHA_of_body_degrees = GHA_of_body_at_hour + GHA_m_s_increment

LHA_of_body_degrees = (GHA_of_body_degrees + CP_longitude_degrees + 360) % 360
Declination_m_increment = observation_time.minute * Declination_d_correction_per_hour / 3600  # specified in minutes of arc
Declination_of_body_degrees = Declination_of_body_at_hour + Declination_m_increment

Z, Hc = ac.sightReduction(CP_latitude_degrees, Declination_of_body_degrees, LHA_of_body_degrees)  # Z later corrected to Zn

observed_body = "Sun"
information_header = f"""
Observed Body: {observed_body}
Observation time {observation_time} UTC
Calculation time {str(datetime.datetime.now(ZoneInfo('UTC')))} UTC
"""

outputTable = []
outputTable.append(["", ""])
outputTable.append([f"Position of {observed_body}:", ""])
outputTable.append(
    [f"GHA of {observed_body} {observation_time.year}-{observation_time.month:02g}-{observation_time.day:02g} {observation_time.hour:02g}h (Almanac)", f"{deg_to_dm(GHA_of_body_at_hour % 360)}"])
outputTable.append([f"GHA increment at {observation_time.minute}m {observation_time.second}s ", f"{deg_to_dm(GHA_m_s_increment)}"])
outputTable.append([f"GHA of {observed_body} at {observation_time.hour}h {observation_time.minute}m {observation_time.second}s", f"{deg_to_dm(GHA_of_body_degrees % 360)}"])
outputTable.append([f"Declination at {observation_time.hour}h (Almanac)", f"{deg_to_dm(Declination_of_body_at_hour)}"])
outputTable.append([f"Decl incr {Declination_d_correction_per_hour}'/hr at {observation_time.minute}m (Almanac)", f"{deg_to_dm(Declination_m_increment)}"])
outputTable.append([f"Declination of {observed_body}", f"{deg_to_dm(Declination_of_body_degrees)}"])

outputTable.append(["", ""])
outputTable.append([f"Chosen Position:", ""])
outputTable.append([f"CP Latitude", f"{deg_to_dm(CP_latitude_degrees)}"])  # , CP_latitude_degrees])
outputTable.append([f"CP Longitude", f"{deg_to_dm(CP_longitude_degrees)}"])  # , CP_longitude_degrees])
outputTable.append([f"LHA of {observed_body} (GHA + CP Lon)", f"{deg_to_dm(LHA_of_body_degrees)}"])  # , LHA_of_body_degrees])

outputTable.append(["", ""])
outputTable.append([f"Hc calculated from CP lat, Decl, LHA", f"{deg_to_dm(Hc)}"])
outputTable.append([f"Ho from sextant", f"{deg_to_dm(Ho)}"])

if Ho > Hc:
    direction = "Towards"
else:
    direction = "Away"

outputTable.append([f"Intercept ({direction})", f"{deg_to_dm(Hc - Ho)}"])
outputTable.append([f"Intercept ({direction})", f"{abs((Hc - Ho) * 60):5.2f} nm "])

# calculate Zn (Azimuth) of the observed body depending on N or S hemisphere and LHA
if CP_latitude_degrees > 0:  # North
    # outputTable.append(["Latitude North",""]) # explanation in output
    if LHA_of_body_degrees > 180:
        # outputTable.append([" and LHA > 180°: Zn = Z",""])
        Zn = Z
    else:
        # outputTable.append([" and LHA < 180°: Zn = 360° - Z",""])
        Zn = 360 - Z
else:  # South
    outputTable.append(["Latitude South", ""])
    if LHA_of_body_degrees > 180:
        outputTable.append([" and LHA > 180°: Zn = 180° - Z", ""])
        Zn = 180 - Z
    else:
        outputTable.append([" and LHA < 180°: Zn = 180° + Z", ""])
        Zn = 180 + Z

outputTable.append([f"  Zn (Azimuth) {round(Zn)}°, LoP {round((Zn + 90) % 360)}°", ""])

print(information_header)
combined_tables = mySextant.table + outputTable

column0_width = max(len(str(row[0])) for row in combined_tables)
column1_width = max(len(str(row[1])) for row in combined_tables)
for row in combined_tables:
    print(f"{row[0]:<{column0_width}}  {row[1]:>{column1_width}}")
        #or - print(row[0].ljust(column0_width + 2), row[1].rjust(column1_width))

if Logging is True:
    OutFileName = f"Logs/{str(observation_time.strftime("%Y-%m-%d %Hh%Mm%Ss UTC"))} {observed_body}.txt"
    # ':' not permitted in filename
    with open(OutFileName, "w", encoding="utf-8") as logfile:
        logfile.write(information_header + "\n")
        for row in combined_tables:
            logfile.write(f"{row[0]:<{column0_width}}  {row[1]:>{column1_width}}\n")
            # or - logfile.write(f"{row[0].ljust(column0_width + 2)}{row[1].rjust(column1_width)}\n")
