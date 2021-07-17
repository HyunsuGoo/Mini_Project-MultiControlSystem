import RPi.GPIO as GPIO
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
#pin dictionary
pin = {
	"led1": 21,
	"led2": 20,
	"servo": 17,
	"trigger": 0,
	"echo": 1,
	"piezo": 13
	}
# motor default dictionary
motor = {
	"min": 3.0,
	"zero": 6.75,
	"max": 11.0,
	"pos": 5
	}
# melody list
melody = [262, 294, 330, 349, 392, 440, 494, 523]
musicAirplane = [2, 1, 0, 1, 2, 2, 2, 1, 1, 1, 2, 4, 4, 2, 1, 0, 1, 2, 2, 2, 2, 1, 1, 2, 1, 0]
delayAirplane = [1, 0.5, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1.5, 0.5, 3]
musicLittleStar = [0, 0, 4, 4, 5, 5, 4, 3, 3 ,2, 2, 1, 1, 0, 4, 4, 3, 3, 2, 2, 1, 4, 4, 3, 3, 2, 2, 1, 0, 0, 4, 4, 5, 5, 4, 3, 3, 2, 2, 1, 1, 0]
delayLittleStar = [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3]


GPIO.setmode(GPIO.BCM)
# LED set
GPIO.setup(pin["led1"], GPIO.OUT)
GPIO.setup(pin["led2"], GPIO.OUT)
GPIO.output(pin["led1"], False)
GPIO.output(pin["led2"], False)
# motor set
GPIO.setup(pin["servo"], GPIO.OUT)
pwmMotor = GPIO.PWM(pin["servo"], 50)
pwmMotor.start(motor["zero"])
# ultra set
GPIO.setup(pin["trigger"], GPIO.OUT)
GPIO.setup(pin["echo"], GPIO.IN)
# piezo set
GPIO.setup(pin["piezo"], GPIO.OUT)
pwmPiezo = GPIO.PWM(pin["piezo"], 1.0)

# Ultrasound distance thread
class ThreadDistance(QThread):
	distanceEvent = pyqtSignal(float)
	
	def __init__(self, parent = None):
		super().__init__(parent)
		self.UFlag = False	# Thread flag
		
# Run thread function
	def run(self):
		while self.UFlag == True:
			distance = self.measure()
			time.sleep(1)
			self.distanceEvent.emit(distance)	# Send distance data

# ultrasound distance function
	def measure(self):
		GPIO.output(pin["trigger"], True)
		time.sleep(0.0001)
		GPIO.output(pin["trigger"], False)

		start = time.time()

		while GPIO.input(pin["echo"]) == False:
			start = time.time()
		while GPIO.input(pin["echo"]) == True:
			stop = time.time()

		lapsed = stop - start
		distance = (lapsed * 19000) / 2
		return distance

# Piezo Music thread
class ThreadMusic(QThread):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.flag = False
		self.airplane = False
		self.star = False
		self.PNote = 0
		self.SNote = 0

# Run thread funtion
	def run(self):
		while self.flag == True:
			if self.airplane == True:
				pwmPiezo.start(70.0)
				pwmPiezo.ChangeFrequency(melody[musicAirplane[self.PNote]])
				time.sleep(delayAirplane[self.PNote])
				self.PNote += 1
				if self.PNote == len(musicAirplane):
					self.PNote = 0
			if self.star == True:
				pwmPiezo.start(70.0)
				pwmPiezo.ChangeFrequency(melody[musicLittleStar[self.SNote]])
				time.sleep(delayLittleStar[self.SNote])
				self.SNote += 1
				if self.SNote == len(musicLittleStar):
					self.SNote = 0
			
# widget(main) class
class MyWindow(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.ui = uic.loadUi("Project.ui", self)
		self.ui.show()

		self.thUltra = ThreadDistance(self)
		self.thUltra.daemon = True
		self.thUltra.distanceEvent.connect(self.threadEventHandler1)

		self.thPiezo = ThreadMusic(self)
		self.thPiezo.daemon = True
		
# LED function
	def slot_led1_on(self):
		GPIO.output(pin["led1"], True)
		self.ui.label_3.setText("LED1 ON!!")
		self.ui.label_3.setStyleSheet("Color : red")
	def slot_led1_off(self):
		GPIO.output(pin["led1"], False)
		self.ui.label_3.setText("LED1 OFF...")
		self.ui.label_3.setStyleSheet("Color : black")

	def slot_led2_on(self):
		GPIO.output(pin["led2"], True)
		self.ui.label_5.setText("LED2 ON!!")
		self.ui.label_5.setStyleSheet("Color : red")
	def slot_led2_off(self):
		GPIO.output(pin["led2"], False)
		self.ui.label_5.setText("LED2 OFF...")
		self.ui.label_5.setStyleSheet("Color : black")

# Servo motor function
	def slot_motor_up(self):
		degree = self.ui.lcdNumber.intValue() + motor["pos"]
		self.ui.horizontalSlider.setValue(degree)
		self.slot_slider()
	def slot_motor_down(self):
		degree = self.ui.lcdNumber.intValue() - motor["pos"]
		self.ui.horizontalSlider.setValue(degree)
		self.slot_slider()
	def slot_slider(self):
		degree = self.ui.lcdNumber.intValue()
		pwmMotor.ChangeDutyCycle(motor["zero"] + (-4.75 * (degree / 90)))

# Ultrasound function
	def slot_ultra_start(self):
		if self.thUltra.UFlag == False:
			self.thUltra.UFlag = True
			self.thUltra.start()
	def slot_ultra_stop(self):
		if self.thUltra.UFlag == True:
			self.thUltra.UFlag = False
	def threadEventHandler1(self, distance):
		self.ui.lcdNumber_2.display(distance)

# Piezo function
	def slot_plane_play(self):
		self.thPiezo.airplane = True
		self.thPiezo.star = False
		if self.thPiezo.flag == False:
			self.thPiezo.flag = True
			self.thPiezo.start()
	def slot_plane_pause(self):
		self.thPiezo.airplane = False
		if self.thPiezo.flag == True:
			self.thPiezo.flag = False
			pwmPiezo.stop()
	def slot_star_play(self):
		self.thPiezo.star = True
		self.thPiezo.airplane = False
		if self.thPiezo.flag == False:
			self.thPiezo.flag = True
			self.thPiezo.start()
	def slot_star_pause(self):
		self.thPiezo.star = False
		if self.thPiezo.flag == True:
			self.thPiezo.flag = False
			pwmPiezo.stop()
			
# exti finction
	def slot_exit(self):
		GPIO.cleanup()
		sys.exit()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myapp = MyWindow()
	app.exec_()
