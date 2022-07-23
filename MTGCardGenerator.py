import sys
from PyQt5.QtWidgets import QWidget, QToolTip, QMessageBox, QPushButton, QApplication, QDesktopWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QComboBox,  QPlainTextEdit, QSizePolicy, QFileDialog
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2

from compare2set import compare2set
from mtg_json_get import getSets
from QWebcamThread import QWebcamThread
from GenerateCardThread import GenerateCardThread


class MTGCardReader(QWidget):
    
    # readsig = pyqtSignal()
    # setsig = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def closeEvent(self, event):
        #Handles qutting when using the top-right X
        reply = QMessageBox.question(self, 'Quitting?',
            "Do you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()  
            
    def keyPressEvent(self, event):
        key = event.key()
        print(key)
        
    def center(self):
        #Function to center the window
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
            
    
    ## Set Up Main UI
    
    def initUI(self):
        global oldset
        
        ##Functions
        
        def read_match(c2s,cvim):
            # uses the compare2set object to identify a card
            print('Reading and Matching')
            name_match_lab.setText('Card: ')
            statuslab.setText('Reading Card...')
            img_match_lab.setPixmap(blank)
            img_gen_lab.setPixmap(blank)
            setButtons(False)
            QApplication.processEvents()
            (matchname,matchcvimage) = c2s.compareimg(cvim)
            matchimage = cvimg2qpixmap(matchcvimage)
            name_match_lab.setText('Card: '+matchname)
            name_gen_lab.setText('Generated Card: (Loading)')
            img_match_lab.setPixmap(matchimage)
            genimgthread = GenerateCardThread(matchname, name_gen_lab, img_gen_lab, self)
            genimgthread.start()


            statuslab.setText('Ready')
            setButtons(True)
            QApplication.processEvents()
        
        oldset = 'None'
        def switchset(text):
            # creates a new compare2set object when the user select a new set
            global compareset
            global oldset
            if not (text == oldset):
                print('Switching to Set: ',text)
                name_match_lab.setText('Card: ')
                name_gen_lab.setText('Generated Card: ')
                statuslab.setText('Loading {}...'.format(text))
                img_match_lab.setPixmap(blank)
                img_gen_lab.setPixmap(blank)
                setButtons(False)
                QApplication.processEvents()
                start = setselect.findText('None', Qt.MatchFixedString)
                if start != -1:
                    setselect.removeItem(start)
                compareset = compare2set(text)
                statuslab.setText('Ready')
                #---------------------------
                setButtons(True)
                #---------------------------
                QApplication.processEvents()
            oldset = text

        def cvimg2qpixmap(cvimg):
            cvimgRGB = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
            qpiximg = QPixmap(QImage(cvimgRGB, cvimgRGB.shape[1], cvimgRGB.shape[0], cvimgRGB.shape[1] * 3,QImage.Format_RGB888))
            return qpiximg
            
        def WebCamMissingDialog():
            # create error message window when QWebCamThread detects an error
            reply = QMessageBox.question(self, 'Webcam Error',"Webcam Error:\n\nPlease ensure that your webcam is connected, then save your work and restart the program.", QMessageBox.Ok, QMessageBox.Ok)
        
        
        ##GUI Widget SETUP
        
        ##INPUT SECTION
        
        #Main Window
        grid = QGridLayout()
        self.setLayout(grid)
        self.setWindowTitle('MTG Card Generator')
        self.setWindowIcon(QIcon('Mana_U.png'))
        #Set Tooltip Font
        QToolTip.setFont(QFont('SansSerif', 10))
        
        setinfoh = QHBoxLayout()
        grid.addLayout(setinfoh, 1,1,1,2)

        
        #Set Seclection Drop Down Menu
        setselectlab = QLabel(self)
        setselectlab.setText('Set:')
        setselectlab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        setinfoh.addWidget(setselectlab)
        
        setselect = QComboBox(self)
        setselect.addItem('None')
        sets = getSets()
        for set in sets:
            setselect.addItem(set)
        setinfoh.addWidget(setselect)
        
        #Status Indicator
        statuslab2 = QLabel(self)
        statuslab2.setText('Status:')
        statuslab2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        setinfoh.addWidget(statuslab2)
        
        statuslab = QLabel(self)
        statuslab.setText('Choose a Set')
        statuslab.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setinfoh.addWidget(statuslab)
        
        #Read Button
        readbtn = QPushButton('Read', self)
        readbtn.setToolTip('Press when your card is in the frame')
        readbtn.setEnabled(False)
        readbtn.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred)
        grid.addWidget(readbtn, 2, 1, 2, 1)
        readbtn.setDefault(True)
        
        #Image Window
        imgwindow = QLabel(self)
        grid.addWidget(imgwindow, 2, 2, 2, 1)
        
        
        ##INFORMATION SECTION
        
        cardinfov = QVBoxLayout()
        grid.addLayout(cardinfov, 2, 3, 1, 1)

        cardinfov2 = QVBoxLayout()
        grid.addLayout(cardinfov2, 2, 4, 1, 1)

         
        #Name of Matched Card
        name_match_lab = QLabel(self)
        name_match_lab.setText('Card: ')
        grid.addWidget(name_match_lab, 1, 3, 1, 1)
        
        #Image of Matched Card
        img_match_lab = QLabel(self)
        blankcv = cv2.imread('blank.png')
        blank = cvimg2qpixmap(blankcv)
        img_match_lab.setPixmap(blank)
        cardinfov.addWidget(img_match_lab)

        # Name of Generated Card
        name_gen_lab = QLabel(self)
        name_gen_lab.setText('Generated Card: ')
        grid.addWidget(name_gen_lab, 1, 4, 1, 1)

        # Image of Generated Card
        img_gen_lab = QLabel(self)
        blankcv = cv2.imread('blank.png')
        blank = cvimg2qpixmap(blankcv)
        img_gen_lab.setPixmap(blank)
        cardinfov2.addWidget(img_gen_lab)


        buttons = [readbtn,setselect]
        
        #Webcam Thread
        camthread = QWebcamThread(imgwindow,self)
        #comparesetthread = QCompareSetThread(name_match_lab, img_match_lab, statuslab,setselect,blank,buttons,self)
        
        ##Signal/Slot System - Connets signals to slots
        
        setselect.activated[str].connect(switchset)
        readbtn.clicked.connect(lambda:read_match(compareset,camthread.getFrame()))

        
        camthread.sig.connect(WebCamMissingDialog)
        
        def setButtons(state):
            for btn in buttons:
                btn.setEnabled(state)
        
        
        ##Start Main Camera Update Thread
        self.show()
        camthread.start()
        #comparesetthread.start()
        self.center()

if __name__ == '__main__':# If this file is the main script being run, run MTGCardReader as it's own window.
    
    app = QApplication(sys.argv)
    mtg_cr = MTGCardReader()
    sys.exit(app.exec_())