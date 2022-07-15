def track(self):
  print("Track called")

def cancel(self):
  print("Cancel called")


SERVICES = {
  "track": track,
  "cancel": cancel
}

MAPPING = {
  "0" : SERVICES
}


class MethodCaller: 
  def call_cancel(self, key, *args, **kwargs):
    return MAPPING[key]['cancel'](*args, **kwargs)

  def call_track(self, key, *args, **kwargs):
    print("key = %s and track={}" % key, MAPPING[key]['track'])
    return MAPPING[key]['track'](*args, **kwargs)


if __name__  == '__main__':
  mc = MethodCaller()
  val = mc.call_track("0")
  print("cancel 0 = %s" % (val))
  
