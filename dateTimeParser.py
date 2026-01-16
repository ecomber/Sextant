import datetime
from zoneinfo import ZoneInfo

observation_time = datetime.datetime(year=2025, month=5, day=29, hour=15, minute=9, second=28, tzinfo=ZoneInfo('UTC'))

observation_time_string_a = ("2025, 05, 29, 15, 9, 28")
observation_time_string_b = ("2025-05-29 15:09:28")
observation_time_string_c = ("2025, 05, 29, 15, 9, 28")
print(observation_time.isoformat())
print(observation_time.astimezone())
print(observation_time.timestamp())
b_split = observation_time_string_b.split()
minutes = b_split[1].split(':')[1]

#print(int(minutes)+3)