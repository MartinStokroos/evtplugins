"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame import item
from libopensesame.oslogging import oslogger
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libopensesame.py3compat import *
from openexp.canvas import Canvas, canvas
from openexp.canvas_elements import (
	Line,
	Rect,
	Polygon,
	Ellipse,
	Image,
	Gabor,
	NoisePatch,
	Circle,
	FixDot,
	ElementFactory,
	RichText,
	Arrow,
	Text
)
from openexp.mouse import mouse

import os
import time
import math
import sys

from pyEVT import EvtExchanger

class TactileStimulator(item.item):

	description = u"Allows the calibration *and* the use of the Tactile Stimulator."

	def reset(self):
		self.var._value = 0
		#self.var._calibrationvalue = 100
		self.var._duration = 150
		self.var._productName = u"DUMMY"
		self.var._calibrate = u"Calibrate"
		# time in seconds.

				
	def prepare(self):
		self.experiment.set("ShockDuration", self.var._duration)
		self.var._shockTimeOut = 1
		self.var._shockHoldOffTime = 8
		item.item.prepare(self)
		self.EE = EvtExchanger()
		Device = self.EE.Select(self.var._productName)

		try:
			if Device is None:
				raise
		except:
			self.var._productName = u"DUMMY"
			oslogger.warning("Did not find a Tactile Stimulator: code to debugwindow")
			
		if self.var._calibrate == u"Calibrate":
			self.Calibrate_Prepare()
		elif self.var._calibrate == u"Shock":
			self.Do_Shock_Prepare()

			
	def run(self):
		self.set_item_onset()
		if 	self.var._productName == u"DUMMY":
			if self.var._calibrate == u"Shock":
				oslogger.info('dummy shock: {} for {} ms'.format(self.var._value, self.var._duration) )
			else:
				self.Calibrate_Run()			
		else:
			#self.EE.Select(self.PATH)
			if self.var._calibrate == u"Calibrate":
				self.Calibrate_Run()
			elif self.var._calibrate == u"Shock":
				self.Do_Shock_Run()
		return True


	def Calibrate_Prepare(self):
		self.canvas = Canvas(self.experiment)
		self.canvas.set_bgcolor("black")
		self.canvas.clear()
        
		self.canvas['Title'] = RichText("Tactile Stimulator Calibration",	
						center = True , 
						x = 0 ,
						y = -int(self.canvas.height/3) , 
						color = "white" , 
						font_family = "mono", 
						font_size = 28)

		self.canvas['Instruction'] = RichText("Point at the desired value position"\
						" on the axis and click ... "\
						"Then click TEST",\
						center = True, 
						x = 0,
						y = -int(self.canvas.height / 8), 
						color = "white")
		# Draw the slider axis

		self.canvas.set_fgcolor("white")
		self.canvas['SliderBox'] = Rect(-self.canvas.width / 2.2,
					 	0,
					 	2 * self.canvas.width / 2.2,
					 	28,
					 	fill=False)

		self.canvas.set_fgcolor("white")
		self.canvas['Slider'] = Rect((-self.canvas.width / 2.2) + 6,
						 6,
						 (2 * self.canvas.width / 2.2) - 12,
						 16,
						 fill=True)
						 
		self.canvas['TestBox'] = Rect((-self.canvas.width / 3),
						 self.canvas.height / 4,
						 self.canvas.width  / 10,
						 self.canvas.height / 10,
						 fill=True,
						 color = "red")
						 
		self.canvas['TestText'] = RichText("TEST", 
						x=(-self.canvas.width / 3)+(self.canvas.width / 20),
						y=(self.canvas.height / 4)+(self.canvas.height / 20),
						color = "black")
		
		self.canvas['OKBox'] = Rect((self.canvas.width / 3),
						 self.canvas.height / 4,
						 -self.canvas.width / 10,
						 self.canvas.height / 10,
						 fill=True,
						 color = "green")
						 
		self.canvas['OKText'] = RichText("OK", 
						x=(self.canvas.width / 3)-(self.canvas.width / 20),
						y=(self.canvas.height / 4)+(self.canvas.height / 20),
						color = "black")
		
		self.canvas['ValuemA'] = RichText(str(round(0,3)) + "mA", 
						x=0,
						y=-(self.canvas.height / 4)+(self.canvas.height / 20),
						color = "green")
						
		self.canvas['ValuePerc'] = RichText("("+str(round(0)) + "%)", 
						x=0,
						y=-(self.canvas.height / 4)+(self.canvas.height / 12),
						color = "green")
		
		self.canvas['wait... '] = RichText(str(round(0)), 
						x=0,
						y=-(self.canvas.height / 10)+(self.canvas.height / 2),
						color = "black")
						
		if not (self.var._productName == u"DUMMY"):
			self.EE.SetLines(0)
			oslogger.info("In (Hardware) Shock: reset port")


	def Calibrate_Run(self):
		slmouse = mouse(self.experiment, timeout=20, visible=True)
		slmouse.show_cursor(True)
		slmouse.set_pos(pos=(0,0))
		xperc = 0;
		self.canvas['Slider'].w = (xperc / 100) * ((2 * self.canvas.width / 2.2) - 12)
		self.canvas.show()	
		
		while True:
		# Poll the mouse for buttonclicks
			button = None
			while button == None:
				button, position, timestamp = slmouse.get_click()

			button = None
			pos, mtime = slmouse.get_pos()
			x, y = pos
			
			if (x, y) in self.canvas['SliderBox']:				
				xperc = min((x + self.canvas.width / 2.2) / (2 * ((self.canvas.width / 2.2) - 6)) * 100.0, 100)
				self.canvas['Slider'].w = (xperc / 100) * ((2 * self.canvas.width / 2.2) - 12)
				self.canvas['ValuePerc'].text = "("+str(round(xperc,1)) + "%)"
				self.canvas['ValuemA'].text = str(round(5*(xperc/100.0),1)) + "mA"
				self.canvas.show()	

			if (x, y) in self.canvas['TestBox']:
				if (self.var._productName == u"DUMMY"):
					oslogger.info("In (Dummy) Shock: shocking with value: {}".format(math.floor( (xperc/100.0) * 255) ) )
				else:
					self.EE.PulseLines(math.floor((xperc/100.0) * 255), self.var._duration)
				
				self.canvas['TestBox'].color = "blue"
				self.canvas.show()
				
				self.canvas['wait... '].color = "green"
				for n in range (1, self.var._shockHoldOffTime):
					self.canvas['wait... '].text = "wait... " + str(self.var._shockHoldOffTime-n)
					self.canvas.show()
					time.sleep(1)
				self.canvas['wait... '].color = "black"
				self.canvas['wait... '].text = "wait... " + str(0)
				
				self.canvas['TestBox'].color = "red"
				self.canvas.show()	
				
				
			if (x, y) in self.canvas['OKBox']:
				self.var.ShockerCalibrationBinvalue = math.floor((xperc/100.0) * 255)
				self.var.ShockerCalibrationmAvalue = round(5*(xperc/100.0),1)
				oslogger.info("Shocker calibration value (binary, mA): {}, {:1}".format(self.var.ShockerCalibrationBinvalue, self.var.ShockerCalibrationmAvalue))
				self.experiment.set("ShockerCalibration", self.var.ShockerCalibrationBinvalue)
				self.experiment.set("ShockermACalibration", self.var.ShockerCalibrationmAvalue)
				break
				
												
	def Do_Shock_Prepare(self):
		if not (self.var._productName == u"DUMMY"):
			self.EE.SetLines(0)
			oslogger.info("In (Hardware) Shock: reset port")


	def Do_Shock_Run(self):
		try:
			self.experiment.get("ShockerCalibration")
		except:
			oslogger.error("No calibration step taken: First run the Tactile Stimulator in calibration mode!")
			return
		
		if (self.var._productName == u"DUMMY"):
			oslogger.info("In (Dummy) Shock: shocking with value: " + str(self.var._value))
		else:
			try:
				tLast = self.experiment.get("lastShockTime")
			except:
				tLast = 0;
				
			td = math.floor( time.time() ) - tLast
			#oslogger.info("Time duration inbetween shocks: " + str(td))
			# This line is to prevent the possibility to shock if the previous shock was less then the minimum time ago
			if (td > self.var._shockTimeOut):
				oslogger.info("In (Hardware) Shock: shocking with value: " + str(math.floor((self.var._value/100.0) * self.experiment.get("ShockerCalibration")))) # better do in shock preparation...
				self.EE.PulseLines(math.floor((self.var._value/100.0) * self.experiment.get("ShockerCalibration")), self.var._duration)
				#oslogger.warning("Shock now!")
				# TODO: here?
				#mA = round((self.var._value/100.0) * self.experiment.get("ShockermACalibration"),2)
				#self.experiment.set("BinaryShockValue", math.floor((self.var._value/100.0) * self.experiment.get("ShockerCalibration"))) 
				#self.experiment.set("ShockPercValue", self.var._value)
				#self.experiment.set("ShockMaValue", mA)
			else:
				oslogger.warning("In Shock: the shock came too early: please don't give shocks in rapid succession!")
			
		self.experiment.set("lastShockTime", math.floor( time.time() ) ) # update the time stamp of the last call
			
	
class qtTactileStimulator(TactileStimulator, qtautoplugin):
	def __init__(self, name, experiment, string = None):

		#Pass the word on to the parents
		TactileStimulator.__init__(self, name, experiment, string)
		qtautoplugin.__init__(self, __file__)

	def perc_check(self):
		try:
			val = int(self.value_widget.text())
			val = min(max(val,0),100)
		except:
			val = 0
			
		self.value_widget.setText(str(val))
		 
	def type_check(self):
		self.value_widget.setEnabled(self.Calibrate_widget.currentText() == u'Shock')
	
	def init_edit_widget(self):
	# Pass the word on to the parent
		qtautoplugin.init_edit_widget(self)

		EE = EvtExchanger()
		listOfDevices = EE.Attached(u"SHOCKER")
		# if there is no shocker attached, the selected name defaults to 'Dummy' again.
		if listOfDevices:
			for i in listOfDevices:
				self.ProductName_widget.addItem(i)
		else:
			self.var._productName = u"DUMMY"
		
		self.duration_widget.setEnabled(False)
		self.value_widget.returnPressed.connect(self.perc_check)
		self.Calibrate_widget.currentTextChanged.connect(self.type_check)
		self.value_widget.setEnabled(self.Calibrate_widget.currentText() == u'Shock')
