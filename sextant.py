import math


def sign(x):
    return -1 if x < 0 else 1


def dm_tup_to_deg(tup):
    s = sign(tup[0])
    return s * (abs(tup[0]) + abs(tup[1] / 60))


def deg_to_dm(deg):
    """Converts decimal degrees to printable D°m.m string"""
    if deg < 0:
        sign = "-"
    else:
        sign = "+"
    decimals, number = math.modf(deg)
    d = int(number)
    m = decimals * 60
    return f"{sign}{abs(d)}°{abs(m):05.02f}′".rjust(8)  # UNICODE ′ (PRIME) char, not apostrophe


class Sextant(object):

    def __init__(self):
        self.index_error = 0
        self.eye_height = 0
        self.Hs = 0
        self.semi_diameter = 0
        self.table = []

    def __str__(self):
        self.Calculate()
        return str(self.table)

    @staticmethod
    def dip(eye_height):
        # Correction for dip of horizon, returns dip in degrees
        return 1.76 * math.sqrt(eye_height) / 60

    @staticmethod
    def atmospheric_refraction_bennett(Ho):
        """ Correction for atmospheric refraction, see: https://en.wikipedia.org/wiki/Atmospheric_refraction
        Ho input in degrees
        returns refraction correction in degrees"""
        return (1 / math.tan(math.radians(Ho + (7.31 / (Ho + 4.4))))) / 60

    def Ho(self):
        Ho = self.Calculate()
        return Ho

    def Calculate(self):
        self.table.clear()

        index_error = self.index_error / 60
        semi_diameter = self.semi_diameter / 60  # +ve Lower Limb

        self.table.append(["Sextant:", ""])
        self.table.append(["Sextant Altitude (Hs)", f"{deg_to_dm(self.Hs)}"])
        self.table.append([f"Index Error (On - / Off +)", f"{deg_to_dm(index_error)}"])

        Hs = self.Hs + index_error
        self.table.append(["Observed Altitude", f"{deg_to_dm(Hs)}"])

        dip_of_horizon = self.dip(self.eye_height)
        self.table.append([f"Dip at {self.eye_height}m eye height", f"{deg_to_dm(-dip_of_horizon)}"])

        Hs = Hs - dip_of_horizon
        self.table.append(["Apparent Altitude", f"{deg_to_dm(Hs)}"])

        refraction_correction = self.atmospheric_refraction_bennett(Hs)
        self.table.append([f"Refraction at {deg_to_dm(Hs)}", f"{deg_to_dm(-refraction_correction)}"])

        Hs = Hs - refraction_correction
        self.table.append(["Apparent Altitude", f"{deg_to_dm(Hs)}"])

        if self.semi_diameter != 0: # Not a star
            self.table.append([f"Semi-diameter (Almanac)", f"{deg_to_dm(semi_diameter)}"])
            Hs = Hs + self.semi_diameter / 60

        Ho = Hs
        self.table.append(["Height Observed (Ho)", f"{deg_to_dm(Ho)}"])
        return Ho


if __name__ == '__main__':
    print(f"Sextant example output.")
    print(f"Dip is 1.76 * sqrt(eye_height_meters) / 60")
    print(f"Refraction is Bennett's formula https://en.wikipedia.org/wiki/Atmospheric_refraction")

    freiberger = Sextant()
    freiberger.index_error = +2.1
    freiberger.eye_height = 2.5
    freiberger.Hs = 29 + 36.8 / 60
    freiberger.semi_diameter = 15.8
    freiberger.Calculate()

    column0_width = max(len(str(row[0])) for row in freiberger.table)
    column1_width = max(len(str(row[1])) for row in freiberger.table)
    for row in freiberger.table:
        print(f"{row[0]:<{column0_width}}  {row[1]:>{column1_width}}")