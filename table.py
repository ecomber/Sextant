import sextant

print(f"Sextant example output.")
print(f"Dip is 1.76 * sqrt(eye_height_meters) / 60")
print(f"Refraction is Bennett's formula https://en.wikipedia.org/wiki/Atmospheric_refraction")

freiberger = sextant.Sextant()
freiberger.index_error = +2.1
freiberger.eye_height = 2.5
freiberger.Hs = 29 + 36.8 / 60
freiberger.semi_diameter = 15.8
freiberger.Calculate()

column0_width = max(len(str(row[0])) for row in freiberger.table)
column1_width = max(len(str(row[1])) for row in freiberger.table)
for row in freiberger.table:
    print(f"{row[0]:<{column0_width}}  {row[1]:>{column1_width}}")

freiberger.table.append(["a", "b", "c"])

print(max(len(row) for row in freiberger.table))
columns = []
colwidth = max(len(str(row[0])) for row in freiberger.table)
print(f"{colwidth:<{colwidth}}  ")