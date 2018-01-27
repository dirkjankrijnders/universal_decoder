# from decconf.categories import Formatter

import decconf.datamodel.CV as cv


def cv2slot(cv):
    slot = int((cv - 32) / 10)
    return slot, int((cv - 32) - (slot * 10))


class I10004(cv.CVDelegate):
    name = "Trainlift LN Module"
    description = "Trainlift LocoNet module"
    nConfiguredPins = 0
    uiController = None

    def __init__(self):
        super(I10004, self).__init__()

    def print_name(self):
        print(self.name)

    def general_cvs(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 32, 34, 35, 36]

    def cv_description(self, cv):
        desc = ['', 'Address', '', '', '', '', "# levels", "Manufacturer", "Version"]
        if cv < len(desc):
            return desc[cv]
        elif cv in range(9, 31):
            return "Pin configuration slot {}".format(cv - 8)
        elif cv > 1000:
            desc_map = {1018: 'Temperature', 1019: 'Serial no.', 1023: 'Firmware version'}
            if cv in desc_map:
                return desc_map[cv]
        elif cv > 31:
            slot, slot_cv = cv2slot(cv)
            if slot == 0:
                slot_cv_desc = ["", "", "feed speed", "top x", "bottom x", "options", "state", "", "", ""]
            else:
                slot_cv_desc = ["", "", "mm", "um", "options", "feedback address", "reserved", "", "", ""]

            return "Slot {}, {}".format(slot, slot_cv_desc[slot_cv])
        return super(I10004, self).cv_description(cv)

    def set_cv(self, cv, value):
        if cv == 6:
            self.nConfiguredPins = value
            for level in range(0, value):
                for cv2 in [2, 3, 4, 5]:
                    self.parent.read_cv((level +1) *10 + cv2 + 32)

        if self.uiController:
            self.uiController.cvChange(cv, value)

    def getCV(self, cv):
        self.parent.get_cv(cv)

    def format_cv(self, cv):
        if not self.parent.CVs[cv]:
            return ''
        if cv == 1018:
            return str(self.parent.CVs[cv] / 16)
        if cv == 1019:
            try:
                return "{:04x} {:04x} {:04x} {:04x}".format(int(self.parent.CVs[cv]),
                                                            int(self.parent.CVs[cv + 1]),
                                                            int(self.parent.CVs[cv + 2]),
                                                            int(self.parent.CVs[cv + 3]))
            except ValueError:
                pass

        if cv == 1023:
            v = str(self.parent.CVs[cv])
            return "{}.{}.{}".format(int(v[0:1]), int(v[2:3]), int(v[4:5]))
        return super(I10004, self).format_cv(cv)

    def controller(self, tabwidget, decoder):
        return super(I10004, self).controller(tabwidget, decoder)

    def close(self):
        if self.uiController:
            self.uiController.close()
