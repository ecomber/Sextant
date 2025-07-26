import math
import sys
import datetime
from zoneinfo import ZoneInfo




def deg_to_dm(deg):
	"""Converts decimal degrees to printable D°m.m string

    Parameters
    ----------
    deg: float
    Decimal degrees

    Returns
    -------
    str :
    degrees as printable string
    """
	if deg < 0:
		sign = "-"
	else:
		sign = "+"
	decimals, number = math.modf(deg)
	d = int(number)
	m = decimals * 60
	#return f"{sign}{abs(d)}°{round(abs(m), 2):05.02f}'".rjust(8)
	return f"{sign}{abs(d)}°{abs(m):05.02f}'".rjust(8)


class Sextant(object):

	def __init__(self):
		self.index_error = 0
		self.eye_height = 0
		self.Hs = 0
		self.semi_diameter = 0
		self.jsonDict = {}
		self.table = []

	def __str__(self):
		#value, string = self.Calculate()
		#return string
		return str(self.table)

	def correction(self, x):
		pass
		# y =-0.0271 * x3  +0.585 * x2 -4.5737 X + 3.8811
		#y = -0.0271 * pow(x, 3) + 0.585 * pow(x, 2) - 4.5737 * x + 3.8811
		y = -0.0271 * x*x*x + 0.585 * x*x - 4.5737 * x + 3.8811
		return y
		
	def correction_1(self, x):
		y = (-0.027097902097902 * x*x*x) + (0.585039960039961 * x*x)  - (4.57367632367633 * x) + 3.8811188811189
		return y
		
	def correction_2(self, x):
		y = -0.0000006 * x*x*x*x + 0.0001 * x*x*x - 0.0052 * x*x - 0.0989 * x -1.096
		return y
		
	def formattedTable(self):
		#self.Calculate()
		return self.table

	def dip(self, eye_height):
		# returns dip in degrees
		return 1.76 * math.sqrt(eye_height) / 60

	def bennett(self, Ho):
		# returns refraction correction in degrees
		# Ho in degrees https://en.wikipedia.org/wiki/Atmospheric_refraction
		return (1 / math.tan(math.radians(Ho + (7.31 / (Ho + 4.4))))) / 60

	def Ho(self):
		value, string = self.Calculate()
		return value

	def Calculate(self):
		self.table.clear()
		retStr = ""
		self.jsonDict["TimeStampCode"] = datetime.datetime.now(ZoneInfo('UTC'))
		self.jsonDict["TimeStampISO"] = str(datetime.datetime.now(ZoneInfo('UTC')))
		self.jsonDict["Hs"] = self.Hs

		index_error = self.index_error / 60
		semi_diameter = self.semi_diameter / 60  # +ve Lower Limb

		retStr += f"Hs                           {deg_to_dm(self.Hs)}\n"
		self.table.append(["Sextant:", ""])
		self.table.append(["Hs (Height by Sextant)", f"{deg_to_dm(self.Hs)}"])

		retStr += f"Index Error (On - / Off +)    {deg_to_dm(index_error)}\n"
		self.table.append(
		 [f"Index Error (On - / Off +)", f"{deg_to_dm(index_error)}"])
		self.jsonDict["IndexError"] = self.index_error
		Hs = self.Hs + index_error
		retStr += f"Hs                           {deg_to_dm(Hs)}\n"
		self.table.append(["Hs", f"{deg_to_dm(Hs)}"])

		self.jsonDict["EyeHeight"] = self.eye_height
		dip_of_horizon = self.dip(self.eye_height)
		self.jsonDict["Dip"] = self.dip(self.eye_height)
		retStr += f"Dip at {self.eye_height}m eye height        {deg_to_dm(-dip_of_horizon)}\n"
		self.table.append(
		 [f"Dip at {self.eye_height}m eye height", f"{deg_to_dm(-dip_of_horizon)}"])
		Hs = Hs - dip_of_horizon
		retStr += f"Hs                           {deg_to_dm(Hs)}\n"
		self.table.append(["Hs", f"{deg_to_dm(Hs)}"])

		refraction_correction = self.bennett(Hs)
		
		retStr += f"Refraction at {deg_to_dm(Hs)}      {deg_to_dm(-refraction_correction)}\n"
		self.jsonDict["RefractionCorrection"] = refraction_correction
		self.table.append(
		 [f"Refraction at {deg_to_dm(Hs)}", f"{deg_to_dm(-refraction_correction)}"])
		Hs = Hs - refraction_correction
		self.table.append(["Hs", f"{deg_to_dm(Hs)}"])
		retStr += f"Semi-diameter (Almanac)                 {deg_to_dm(semi_diameter)}\n"
		self.jsonDict["Semi-diameter (Almanac)"] = self.semi_diameter
		if self.semi_diameter != 0:
			self.table.append([f"Semi-diameter (Almanac)", f"{deg_to_dm(semi_diameter)}"])
			Hs = Hs + self.semi_diameter / 60
			retStr += f"Hs                           {deg_to_dm(Hs)}\n"
			#self.table.append(["Hs", f"{deg_to_dm(Hs)}"])
		Ho = Hs
		retStr += f"Ho                           {deg_to_dm(Ho)}\n"
		self.jsonDict["Ho (Height Observed|)"] = Ho
		retStr += f"Ho decimal degrees           {Ho:0.6f}\n"
		self.table.append(["Ho (Height Observed)", f"{deg_to_dm(Ho)}"])
		#self.table.append(["Ho as decimal",str(Ho)])
		return Ho, retStr


if __name__ == '__main__':
	pass
	freib = Sextant()
	freib.index_error = +2.1
	freib.eye_height = 2.5
	freib.Hs = 29 + 36.8 / 60
	freib.semi_diameter = 15.8
	freib.Calculate()
	print(f"Sextant example output.")
	print(f"Dip is 1.76 * sqrt(eye_height_meters) / 60")
	print(
	 f"Refraction is Bennett's formula https://en.wikipedia.org/wiki/Atmospheric_refraction"
	)
	print(
	 f"Reported to be consistent within 0.07′ over the entire range from the zenith to the horizon.\n"
	)
	for row in freib.table:
		print(row[0].ljust(28), row[1].rjust(12))

	#print(deg_to_dm( freib.correction(20)*3600))
	with open("corrections.csv","w") as outfile:
		outfile.write("a,b\n")
		for i in range(0,13):
			outfile.write(f"{i}, {freib.correction(i)}\n")

