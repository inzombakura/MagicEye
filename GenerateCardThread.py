from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import requests
import json
import base64
import numpy as np


class GenerateCardThread(QThread):
    sig = pyqtSignal()

    def __init__(self, matchname, texttarget, imagetarget, parent=None):
        super(GenerateCardThread, self).__init__(parent=parent)
        self.matchname = matchname
        self.texttarget = texttarget
        self.imagetarget = imagetarget
        self.done = False

    def cvimg2qpixmap(cvimg):
        cvimgRGB = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        qpiximg = QPixmap(
            QImage(cvimgRGB, cvimgRGB.shape[1], cvimgRGB.shape[0], cvimgRGB.shape[1] * 3, QImage.Format_RGB888))
        return qpiximg

    def run(self):
        # generate image
        url = "https://solving-story-dodge-chess.trycloudflare.com//dalle"
        myobj = {'num_images': 1, 'text': self.matchname}
        im_b64 = requests.post(url, json=myobj)
        resp = json.loads(im_b64.content.decode('utf-8'))['generatedImgs'][0]
        im_bytes = base64.b64decode(resp)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        cvimgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        matchimage = QPixmap(QImage(cvimgRGB, cvimgRGB.shape[1], cvimgRGB.shape[0], cvimgRGB.shape[1] * 3, QImage.Format_RGB888))
        self.imagetarget.setPixmap(matchimage)
        self.texttarget.setText('Generated Card: '+self.matchname)
        self.done = True
        self.quit()
