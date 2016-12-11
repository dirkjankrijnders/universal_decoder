#from decconf.categories import Formatter

import decconf.datamodel.CV as cv

class I10003(cv.CVDelegate):
	name = "Loconet S88 Bridge"
	description = "Loconet S88 Bridge"
	nConfiguredPins = 0;
	
	def print_name(self):
		print("This is plugin 1");
	
	def generalCVs(self):
		return [1,5,6,7,8,9];
	
	def cvDescription(self, cv):
		desc = ['', 'Address', '', '', '','Max Modules supported',"No configured modules", "Manufacturer", "Version", "Speed"];
		return super(I10003, self).cvDescription(cv);
	
	def setCV(self, cv, value):
		pass