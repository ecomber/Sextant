import datetime
import math
from zoneinfo import ZoneInfo

import sextant


class AstroCalculator(object):

    def __str__(self):
        # help(self )
        return "Class AstroCalculator(object), astronomical functions for navigation.\n"

    def julian_day(self, dt):
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

    def greenwich_sidereal_time(self, jd):
        """ Greenwich Sidereal Time (GAST) = GHA of Aries in degrees """
        T = (jd - 2451545.0) / 36525.0
        GST = 280.46061837 + 360.98564736629 * (jd - 2451545) + 0.000387933 * T ** 2 - T ** 3 / 38710000
        return GST % 360

    def local_sidereal_time_from_gst(self, gst, longitude):
        """Calculate Local Sidereal Time (in degrees)"""
        LST = gst + longitude
        return LST % 360

    def local_sidereal_time_from_dt(self, dt_utc, longitude):
        jd = self.julian_day(dt_utc)
        gst = self.greenwich_sidereal_time(jd)
        lst = self.local_sidereal_time_from_gst(gst, longitude)
        return lst

    def sightReduction(self, EP_latitude_degrees, Declination_of_body_degrees, LHA_of_body_degrees):
        Lat = math.radians(EP_latitude_degrees)
        Dec = math.radians(Declination_of_body_degrees)
        LHA = math.radians(LHA_of_body_degrees)
        #  sin_Hc = math.sin(Lat) * math.sin(Dec) + math.cos(Lat) * math.cos(Dec) * math.cos(LHA)
        Hc = math.asin(math.sin(Lat) * math.sin(Dec) + math.cos(Lat) * math.cos(Dec) * math.cos(LHA))
        # wrong? cos_Z = (math.sin(Dec)/(math.cos(Hc)*math.cos(Lat)))-(math.tan(Hc)*math.tan(Lat))
        cos_Z = (math.sin(Dec) - math.sin(Hc) * math.sin(Lat)) / (math.cos(Hc) * math.cos(Lat))
        Z = math.acos(cos_Z)
        # return (360-math.degrees(Z))%360, math.degrees(Hc)%360
        return math.degrees(Z) % 360, math.degrees(Hc) % 360

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
        era = math.degrees(2 * math.pi * (0.7790572732640 + 1.00273781191135448 * tu))
        return era


if __name__ == '__main__':
    ac = AstroCalculator()
    print(ac)
    now = datetime.datetime.now(ZoneInfo('UTC'))
    print(f"Now: {now} UTC")
    jd = ac.julian_day(now)
    print(f"Julian Day: {jd}")
    gst = ac.greenwich_sidereal_time(jd)
    print(f"GST {gst}°")
    print(f"GST {sextant.deg_to_dm(gst)}")
    era = ac.earth_rotation_angle(now)
    print(f"Earth rotation Angle {sextant.deg_to_dm(era % 360)}")
