###################################
# Shows timezone 
#
# Use  date '+%Z' instead
##############

import datetime;

now = datetime.datetime.now()
local_now = now.astimezone()
local_tz = local_now.tzinfo
tzname = local_tz.tzname(local_now)
print(f"{tzname}")

# so = 31299580, works
so31 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z")
print(f"{so31}")