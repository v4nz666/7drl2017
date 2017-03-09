class TickHandler:
  def __init__(self, interval, fn, enabled):
    self.interval = interval
    self.fn = fn
    self.enabled = enabled

  def run(self):
    self.fn()