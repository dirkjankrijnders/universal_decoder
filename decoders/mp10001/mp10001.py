#from decconf.categories import Formatter

import decconf.datamodel.CV as cv

def cv2slot(cv):
	slot = int((cv-32)/10);
	return slot, int((cv-32)-(slot*10))

class I10001(cv.CVDelegate):
	name = "Universal LN Module"
	description = "Universal LocoNet module"
	nConfiguredPins = 0;
	uiController = None;
	
	def close(arg):
		pass
		
	def print_name(self):
		print("This is plugin 1");
	
	def generalCVs(self):
		return [1,2,3,4,5,6,7,8];
	
	def cvDescription(self, cv):
		desc = ['', 'Address', 'bla', '', '','',"No configured pins", "Manufacturer", "Version"];
		if cv < len(desc):
			return desc[cv];
		elif cv in range(9,31):
			return "Pin configuration slot {}".format(cv-8);
		elif cv > 1000:
			desc_map = {1018: 'Temperature', 1019: 'Serial no.', 1023: 'Firmware version'};
			if cv in desc_map:
				return desc_map[cv]
		elif cv > 31:
			slot, slotcv = cv2slot(cv);
			if self.parent.CVs[9+slot] == 1:
				slotcvdesc = ["Ard. pin", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			elif self.parent.CVs[9+slot] == 2:
				slotcvdesc = ["Ard. pin", "LN Add.", "Pos 1", "Pos 2", "Speed", "Res. 1", "Res. 2", "FB slot 1", "FB slot 2", "Power slot"];
			elif self.parent.CVs[9+slot] == 3:
				slotcvdesc = ["Ard. pin", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			elif self.parent.CVs[9+slot] == 101:
				slotcvdesc = ["LTC. channel", "LN Add.", "Options", "Res. 1", "Res. 2", "Res. 3", "Res. 4", "Res. 5", "Res. 6", "Res. 7"];
			elif self.parent.CVs[9+slot] == 102:
				slotcvdesc = ["PCA. channel", "LN Add.", "Pos 1", "Pos 2", "Speed", "Res. 1", "Res. 2", "FB slot 1", "FB slot 2", "Power slot"];
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
			if value == 4: # Dual action pin
				for cv2 in [0, 1, 2, 3, 4, 5, 6]:
					self.parent.readCV(slot*10 + 32 + cv2);
			if value == 101: # Output pin
				for cv2 in [0, 1, 2]:
					self.parent.readCV(slot*10 + 32 + cv2);
			if value == 102: # PCA Servo pin
				for cv2 in [0, 1, 2, 3, 4,7,8,9]:
					self.parent.readCV(slot*10 + 32 + cv2);
		if self.uiController:
			self.uiController.cvChange(cv, value);
	
	def getCV(self, cv):
		self.parent.getCV(cv);
		
	def formatCV(self, cv):
		if not self.parent.CVs[cv]:
			return '';
		if cv == 1018:
			return str(self.parent.CVs[cv]/16);
		if cv == 1019:
			return "{:04x} {:04x} {:04x} {:04x}".format(self.parent.CVs[cv],self.parent.CVs[cv+1],self.parent.CVs[cv+2],self.parent.CVs[cv+3])
		if cv == 1023:
			v = str(self.parent.CVs[cv]);
			return "{}.{}.{}".format(int(v[0:1]), int(v[2:3]), int(v[4:5]))
		return super(I10001, self).formatCV(cv);
	
	def controller(self, tabwidget):
		from decoders.mp10001.dec10001 import dec10001controller
		self.uiController = dec10001controller(self, tabwidget);
		return self.uiController;