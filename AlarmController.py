import time
from Buzzer import *
from Displays import *
from Button import *
from Lights import *
from CompositeLights import *
from Model import *
from Counters import *
from Sensors import *
from Scanner import *

class AlarmController:

  def __init__(self):
    self._display = LCDDisplay(sda = 0, scl = 1, i2cid = 0)
    self._cancelButton = Button(9, "cancel", buttonhandler=None)
    self._armingButton = Button(8, "arm", buttonhandler=None)
    self._light = Light(12, 'activeLight')
    self._buzzer = PassiveBuzzer(10)
    self._triggeredLight = NeoPixel(pin=27, numleds=16, brightness=1)
    self._sensor = DigitalSensor(28, lowactive=False)
    self._timer = SoftwareTimer(None)
    self._scanner = Scanner()
    self.armingCode = 0
    self.disarmingCode = 0

    self._model = Model(6, self, debug=True)
    self._model.addButton(self._armingButton)
    self._model.addButton(self._cancelButton)
    self._model.addTimer(self._timer)

    self._model.addTransition(0, [BTN1_PRESS], 1)
    self._model.addTransition(1, [BTN2_PRESS], 0)
    self._model.addTransition(1, [BTN1_PRESS], 2)
    self._model.addTransition(2, [BTN1_PRESS], 4)
    self._model.addTransition(3, [BTN1_PRESS], 4)
    self._model.addTransition(3, [TIMEOUT], 2)
    self._model.addTransition(4, [BTN1_PRESS], 5)
    self._model.addTransition(4, [TIMEOUT], 2)
  
  def run(self):
    self._model.run()
  
  def stateEntered(self, state, event):
    if state == 0:
        self._display.reset()
        self._light.off()
        self._triggeredLight.off()
        self._display.showText("Standing By")
        self.armingCode = 0
        self.disarmingCode = 0
    elif state == 1:
        self._display.showText("Set the Keypin")
        self._display.showText("Code:", 1)
        self.armingCode = self._scanner.scanData()
        self._display.showText(f"Code: {self.armingCode}", 1)
    elif state == 2:
        self._display.reset()
        self._display.showText("Arming")
        time.sleep(5)
        self._light.on()
        self._triggeredLight.off()
        self._display.reset()
        self._display.showText("Armed")
    elif state == 3:
        self._triggeredLight.onRed()
        self._display.showText("Intruder! Halt!")
        self._display.showText("BarkBarkArfWoof!", 1)
        self._timer.start(30)
    elif state == 4:
        self._display.reset()
        self._display.showText("Enter the Keypin")
        self._display.showText("Code:", 1)
        self.disarmingCode = self._scanner.scanData()
        self._display.showText(f"Code: {self.disarmingCode}", 1)
        print(f"Disarming Code is {self.disarmingCode} and Arming Code is {self.armingCode}")
    elif state == 5:
        self._display.reset()
        self._display.showText("Verifying")
        time.sleep(2)
        if self.disarmingCode == self.armingCode:
            self._model.gotoState(0)
        else:
            self._model.gotoState(3)


  
  def stateDo(self, state):
    if state == 2:
        if self._sensor.tripped():
            self._model.gotoState(3)
    elif state == 3:
        self._timer.check()
        self._buzzer.beep(750)
        self._buzzer.beep(500)


  def stateLeft(self, state, event):
    if state == 3:
        self._buzzer.stop()
        self._timer.cancel()
    
