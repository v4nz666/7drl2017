class TickHandler:
  def __init__(self, interval, fn):
    self.interval = interval
    self.fn = fn
    self.enabled = True

  def run(self):
    self.fn()