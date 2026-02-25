import datetime
import math
from zoneinfo import ZoneInfo

import sextant


class AstroCalculator(object):

    def __str__(self):
        # help(self )
        return "Class AstroCalculator(object), astronomical functions for navigation."

    @staticmethod
    def julian_day(dt):
        """Calculate Julian Day from datetime (UTC)"""
        if dt.tzname() != "UTC":
            print(f"Warning: julian_day(self, dt) dt.tzname() is not UTC")
        year = dt.year
        month = dt.month
        day = dt.day + dt.hour / 24 + dt.minute / 1440 + dt.second / 86400
        if month <= 2:
            year -= 1
            month += 12
        A = math.floor(year / 100)
        B = 2 - A + math.floor(A / 4)
        JD = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
        return JD

    @staticmethod
    def greenwich_sidereal_time(jd):
        """ Greenwich Sidereal Time (GAST) = GHA of Aries in degrees """
        T = (jd - 2451545.0) / 36525.0
        GST = 280.46061837 + 360.98564736629 * (jd - 2451545) + 0.000387933 * T ** 2 - T ** 3 / 38710000
        return GST % 360

    @staticmethod
    def local_sidereal_time_from_gst(gst, longitude):
        """Calculate Local Sidereal Time (in degrees)"""
        LST = gst + longitude
        return LST % 360

    def local_sidereal_time_from_dt(self, dt_utc, longitude):
        jd = self.julian_day(dt_utc)
        gst = self.greenwich_sidereal_time(jd)
        lst = self.local_sidereal_time_from_gst(gst, longitude)
        return lst

    @staticmethod
    def sightReduction(CP_latitude_degrees, Declination_of_body_degrees, LHA_of_body_degrees):
        Lat_of_CP = math.radians(CP_latitude_degrees)
        Dec_of_body = math.radians(Declination_of_body_degrees)
        LHA_of_body = math.radians(LHA_of_body_degrees)
        #  sin_Hc = math.sin(Lat_of_CP) * math.sin(Dec) + math.cos(Lat_of_CP) * math.cos(Dec) * math.cos(LHA_of_body)
        Hc = math.asin(math.sin(Lat_of_CP) * math.sin(Dec_of_body) + math.cos(Lat_of_CP) * math.cos(Dec_of_body) * math.cos(LHA_of_body))
        # wrong? cos_Z = (math.sin(Dec)/(math.cos(Hc)*math.cos(Lat_of_CP)))-(math.tan(Hc)*math.tan(Lat_of_CP))
        cos_Z = (math.sin(Dec_of_body) - math.sin(Hc) * math.sin(Lat_of_CP)) / (math.cos(Hc) * math.cos(Lat_of_CP))
        Z = math.acos(cos_Z)
        # return (360-math.degrees(Z))%360, math.degrees(Hc)%360

        # calculate Zn (Azimuth) of the observed body depending on N or S hemisphere and LHA_of_body
        # needs to be converted to radians or v.v. depending on choice
        if Lat_of_CP > 0:  # North
            # outputTable.append(["Latitude North",""]) # explanation in output
            if LHA_of_body > math.pi: # > 180 deg
                # outputTable.append([" and LHA_of_body > 180°: Zn = Z",""])
                Zn = Z
            else:
                # outputTable.append([" and LHA_of_body < 180°: Zn = 360° - Z",""])
                Zn = 2*math.pi - Z # 360 deg
        else:  # South
            #outputTable.append(["Latitude South", ""])
            if LHA_of_body > math.pi: # > 180 deg
                #outputTable.append([" and LHA_of_body > 180°: Zn = 180° - Z", ""])
                Zn = math.pi - Z # 180
            else:
                #outputTable.append([" and LHA_of_body < 180°: Zn = 180° + Z", ""])
                Zn = math.pi + Z # 180

        return math.degrees(Hc) % 360, math.degrees(Z) % 360,  math.degrees(Zn) % 360

    def earth_rotation_angle(self, dt):
        """Earth rotation angle - ERA
        The modern equivalent of Greenwich Sidereal Time (GST), referred to a point called the Celestial Intermediate Origin (CIO) instead of the equinox.
        The CIO is a point defined not by its position but by its motion, and at present lies very close to the prime meridian of the Geocentric Celestial Reference System (within 0.1 arcsec throughout the 21st century).
        Unlike GST, which is a complicated function of both UT1 and Terrestrial Time and includes precession and nutation terms, ERA is a simple linear function of UT1 alone."""
        """Measured in radians, is related to UT1 by a simple linear relation:"""
        """ERA replaces Greenwich Apparent Sidereal Time (GAST)."""
        """https://astronomy.stackexchange.com/questions/53233/how-is-earths-rotation-angle-era-defined-and-measured"""
        """ERA = 2π(0.7790572732640 + 1.00273781191135448 · Tu) radians, where Tu = (Julian UT1 date - 2451545.0) """
        JD = self.julian_day(dt)
        tu = JD - 2451545.0
        return math.degrees(2 * math.pi * (0.7790572732640 + 1.00273781191135448 * tu))


if __name__ == '__main__':
    ac = AstroCalculator()
    print(ac)
    print("An example output:")
    now = datetime.datetime.now(ZoneInfo('UTC'))
    print(f"Now: {now} UTC")
    jd = ac.julian_day(now)
    print(f"Julian Day: {jd}")
    gst = ac.greenwich_sidereal_time(jd)
    print(f"GST {gst:.2f}°")
    print(f"GST {sextant.deg_to_dm(gst)}")
    print(f"LST at 08°W: {sextant.deg_to_dm(ac.local_sidereal_time_from_gst(gst, -8))}")
    era = ac.earth_rotation_angle(now)
    print(f"Earth rotation Angle {sextant.deg_to_dm(era % 360)}")
