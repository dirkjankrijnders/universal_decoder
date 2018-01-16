#from decconf.categories import Formatter

import decconf.datamodel.CV as cv

class I10003(cv.CVDelegate):
	name = "Loconet S88 Bridge"
	description = "Loconet S88 Bridge"
	nConfiguredPins = 0;
	
	def print_name(self):
		print("This is plugin 1");
	
	def general_cvs(self):
		return [1,5,6,7,8,9];
	
	def cv_description(self, cv):
		desc = ['', 'Address', '', '', '','Max Modules supported',"No configured modules", "Manufacturer", "Version", "Speed"];
		if cv < len(desc):
			return desc[cv];
		return super(I10003, self).cv_description(cv);
	
	def set_cv(self, cv, value):
		pass