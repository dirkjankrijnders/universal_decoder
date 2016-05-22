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
		desc = ['', 'Address', 'bla'];
		if cv < len(desc):
			return desc[cv];
		
		if cv > 31:
			slotcvdesc = ["Ard. pin", "LN Add.", "Pos 1", "Pos 2", "Speed", "Res. 1", "Res. 2", "FB slot 1", "FB slot 2", "Res. 3"];
			slot, slotcv = cv2slot(cv);
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
				for cv2 in [0, 1, 2, 3, 4,7,8]:
					self.parent.readCV(slot*10 + 32 + cv2);