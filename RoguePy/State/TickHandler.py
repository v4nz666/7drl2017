class TickHandler:
  def __init__(self, interval, fn):
    self.interval = interval
    self.fn = fn

  def run(self):
    self.fn()