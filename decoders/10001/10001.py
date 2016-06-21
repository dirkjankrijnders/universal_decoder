#from decconf.categories import Formatter

import decconf.datamodel.CV as cv

def cv2slot(cv):
	slot = int((cv-32)/10);
	return slot, int((cv-32)-(slot*10))

class I10001(cv.CVDelegate):
	name = "Universal LN Module"
	description = "Universal LocoNet module"
	nConfiguredPins = 0;
	
	def print_name(self):
		print("This is plugin 1");
	
	def generalCVs(self):
		return [1,2,3,4,5,6,7,8];
	
	def cvDescription(self, cv):
		desc = ['', 'Address', 'bla', '', '','',"No configured pins", "Manufacturer", "Version", "Pin configuration slot 1"];
		if cv < len(desc):
			return desc[cv];
		
		if cv > 31:
			slot, slotcv = cv2slot(cv);
			if self.parent.CVs[9+slot] == 1:
				slotcvdesc = ["Ard. pin", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			elif self.parent.CVs[9+slot] == 2:
				slotcvdesc = ["Ard. pin", "LN Add.", "Pos 1", "Pos 2", "Speed", "Res. 1", "Res. 2", "FB slot 1", "FB slot 2", "Power slot"];
			elif self.parent.CVs[9+slot] == 3:
				slotcvdesc = ["Ard. pin", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			else:
				slotcvdesc = ["Unconfigured", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			
			return "Slot {}, {}".format(slot, slotcvdesc[slotcv]);
		return super(I10001, self).cvDescription(cv);
	
	def setCV(self, cv, value):
		if cv == 6:
			self.nConfiguredPins = value;
			for cv2 in range(9, 9+value):
				self.parent.readCV(cv2);
		if cv > 8 and cv < 9+ self.nConfiguredPins:
			slot = cv -  9
			print("Slot: ", str(slot))
			if value == 1: # Input pin
				for cv2 in [0, 1]:
					self.parent.readCV(slot*10 + 32 + cv2);
			if value == 2: # Servo pin
				for cv2 in [0, 1, 2, 3, 4,7,8,9]:
					self.parent.readCV(slot*10 + 32 + cv2);
			if value == 3: # Output pin
				for cv2 in [0, 1, 2]:
					self.parent.readCV(slot*10 + 32 + cv2);
