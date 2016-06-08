# ABEL INVERSE TRANSFORM FOR MULTIPLY 2D SPECTERS

# Author: Shcherbakov Viacheslav
# Email: uncle.slavik@gmail.com
# Version: 0.3
# Status: Development
# Date created: 01/12/2016
# Date last modified: 01/15/2016
# Python Version: 3.4
# Require modules: numpy, matplotlib, scipy, six, dateutil, pyparsing

# TODO:  batch specter processing, define spectral line parameters, temperature calculation, UI, documentation

import sys


from PyQt4 import QtGui,QtCore



import glob
import time
import numpy as np
import matplotlib.pyplot as plt

import random
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.gridspec as gridspec

from matplotlib.ticker import MultipleLocator, FixedLocator
from matplotlib import cm
from abel import Abel
from specter import Specter
from temperature import Tempereture
'''
    def showPlots(self):
        plt.subplot(3, 1, 1)
        plt.title("Signal & smoothed signal", size=13)
        plt.plot(self.specter[0].data[self.columnNumber,:],'k.')
        plt.plot(self.specter[0].dataSmooth[self.columnNumber,:],'r-')

        plt.subplot(3, 1, 2)
        plt.title("Two halves and combined", size=13)
        plt.plot(self.specter[0].dataSplit[self.columnNumber,:])
        plt.plot(self.specter[0].dataCombinedHalf[self.columnNumber,:], 'k--')

        plt.subplot(3, 1, 3)
        plt.title("Abel inverse transform", size=13)
        plt.plot(Abel.transform(self.specter[0].dataCombinedHalf[self.columnNumber,:]), 'r-')

        plt.show()

'''
class AppForm(QtGui.QMainWindow):
    def __init__(self, parent=None, specterCenter=0, columnNumber=0, windowLength=0):
        QtGui.QMainWindow.__init__(self, parent)
        #self.x, self.y = self.get_data()
        self.create_main_frame()
        self.specter=[]
        self.currentSpecter=0
        self.abelData=[]
        self.specterCenter=specterCenter
        self.columnNumber=columnNumber
        self.windowLength=windowLength

        exitAction = QtGui.QAction(QtGui.QIcon('icons/svg/power.svg'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        openAction = QtGui.QAction(QtGui.QIcon('icons/svg/folder-open.svg'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open file sequence')
        openAction.triggered.connect(self.loadSpecterFromFiles)

        #plotAction = QtGui.QAction(QtGui.QIcon('icons/svg/chart-line-outline.svg'), '&Plot', self)
        #plotAction.setShortcut('Ctrl+P')
        #plotAction.setStatusTip('Plot')
        #plotAction.triggered.connect(self.on_draw)

        nextSpecterAction = QtGui.QAction(QtGui.QIcon('icons/svg/chevron-right-outline.svg'), '&Next specter', self)
        nextSpecterAction.setStatusTip('Next specter')
        nextSpecterAction.triggered.connect(self.nextSpecter)

        self.currentSpecterInput = QtGui.QLabel()
        #self.currentSpecterInput.setMaxLength(150)
        #self.currentSpecterInput.setValidator(QtGui.QIntValidator())
        self.currentSpecterInput.setFixedWidth(500)

        self.totalSpecterLabel = QtGui.QLabel()
        self.totalSpecterLabel.setFixedWidth(40)

        prevSpecterAction = QtGui.QAction(QtGui.QIcon('icons/svg/chevron-left-outline.svg'), '&Next specter', self)
        prevSpecterAction.setStatusTip('Prev specter')
        prevSpecterAction.triggered.connect(self.prevSpecter)

        self.statusBar().showMessage('Ready')

        self.setWindowTitle('Abel transform and temperature calculation')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        #fileMenu.addAction(plotAction)
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Main')
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(prevSpecterAction)
        self.toolbar.addAction(nextSpecterAction)
        self.toolbar.addWidget(self.currentSpecterInput)
        self.toolbar.addWidget(self.totalSpecterLabel)

        #self.toolbar.addAction(plotAction)
        #self.toolbar.addAction(exitAction)



    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()
        self.fig = Figure((10.0, 8.0), dpi=72)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        #self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('motion_notify_event', self.mouse_moved)
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['L1', "L2","LNIST","Aki","Ek","g"])
        header = self.table.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.itemChanged.connect(self.setLine)
        self.buttonAddLine = QtGui.QPushButton("Add a line")
        self.buttonAddLine.clicked.connect(self.addLine)
        self.buttonComputeTemp = QtGui.QPushButton("Compute temperature")
        self.buttonComputeTemp.clicked.connect(self.computeTemp)
        self.lines=[]

        vbox = QtGui.QGridLayout()
        vbox.addWidget(self.table, 0, 0, 1, 1)
        vbox.addWidget(self.buttonAddLine, 1, 0, 1, 1)
        vbox.addWidget(self.buttonComputeTemp, 2, 0, 1, 1)
        vbox.addWidget(self.canvas, 0, 1, 1, 4)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar, 1, 1, 1, 4)
        vbox.setColumnStretch(1,5)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def on_draw(self):
        self.fig.clear()
        gs = gridspec.GridSpec(2, 2, width_ratios=[5,1], height_ratios=[4,1], wspace=0.12, hspace=0.12, left=0.05, bottom=0.05, right=0.95, top=0.95)
        self.axes1 = self.fig.add_subplot(gs[0])
        self.axes2 = self.fig.add_subplot(gs[1])
        self.axes3 = self.fig.add_subplot(gs[2])
        self.drawSpecter()
        self.drawPlots()

    def drawSpecter(self):
        abelData=self.abelData[self.currentSpecter]
        self.axes1.imshow(np.transpose(abelData), interpolation='nearest', aspect='auto')
        self.axes11 = self.axes1.twiny()
        self.axes11.set_xticklabels(self.specter[self.currentSpecter].wavelength)

        majorLocator = FixedLocator(5)
        #majorFormatter = FormatStrFormatter('%d')
        minorLocator = MultipleLocator(5)

        #self.axes11.get_xaxis().set_major_locator(majorLocator)
        #self.axes11.get_xaxis().set_major_formatter(majorFormatter)
        self.canvas.draw()

    def drawPlots(self,x=0,y=0):
        abelData=self.abelData[self.currentSpecter]
        vertPixels=len(abelData[x])
        self.axes2.cla()
        self.axes2.set_ylim([vertPixels,0])
        self.axes2.grid()
        self.axes2.plot(abelData[x], np.arange(0,vertPixels,1))

        transp=np.transpose(abelData)[y]
        self.axes3.cla()
        self.axes3.set_xlim([0,len(transp)])
        self.axes3.grid()
        self.axes3.plot(transp)

        for line in self.lines:
            self.axes3.axvline(x=int(line[0]), color='r', linestyle='-')
            self.axes3.axvline(x=int(line[1]), color='r', linestyle='-')

        self.canvas.draw()

    def on_key_press(self, event):
        print('you pressed', event.key)

    def mouse_moved(self, mouse_event):
        if mouse_event.inaxes:
            x, y = int(round(mouse_event.xdata)), int(round(mouse_event.ydata))
            self.drawPlots(x,y)

    def loadSpecterFromFiles(self):
        self.dirPath = QtGui.QFileDialog.getExistingDirectory(self.main_frame, "Open Directory","D:")
        fileList=glob.glob(self.dirPath+'\*.asc')
        for fileName in fileList:
            self.specter.append(Specter(np.loadtxt(fileName),fileName,self.specterCenter,self.windowLength))

        if len(self.specter)>0:
            self.currentSpecter=0

        self.updateSpecterInput()
        for specNum in range(0, len(self.specter)):
            self.statusBar().showMessage('Busy...')
            self.computeAbelTransform(specNum)

        self.statusBar().showMessage('Ready')
        self.on_draw()

    def nextSpecter(self):
        if self.currentSpecter<(len(self.specter)-1):
            self.currentSpecter+=1
            self.updateSpecterInput()
            self.on_draw()

    def prevSpecter(self):
        if self.currentSpecter>1:
            self.currentSpecter-=1
            self.updateSpecterInput()
            self.on_draw()

    def updateSpecterInput(self):
        self.currentSpecterInput.setText(str(self.currentSpecter+1) + ' / ' + str(len(self.specter)) + ' (' +self.specter[self.currentSpecter].name+ ')')

    def computeAbelTransform(self, specterNum):
        abelData=[]
        for column in self.specter[specterNum].dataCombinedHalf:
            abelData.append(Abel.transform(column))

        self.abelData.append(np.array(abelData))

    def addLine(self):
        #self.lines.append((0,0,0,0,0,0))

        #test case
        self.lines.append((244,265,250,10,3000,2))
        self.lines.append((305,343,325,10,2000,2))
        self.updateTable()

    def setLine(self,item):
        lineNum=item.row()
        self.lines[lineNum]=(
            int(self.table.item(lineNum,0).text()),
            int(self.table.item(lineNum,1).text()),
            float(self.table.item(lineNum,2).text()),
            float(self.table.item(lineNum,3).text()),
            float(self.table.item(lineNum,4).text()),
            float(self.table.item(lineNum,5).text())
        )

    def computeTemp(self):
        abelData=self.abelData[self.currentSpecter]
        Tempereture.compute(abelData,self.lines)

    def updateTable(self):
        self.table.setRowCount(0)
        for line in self.lines:
            currentRowCount = self.table.rowCount()
            self.table.insertRow(currentRowCount)
            for col, value in enumerate(line):
                self.table.setItem(currentRowCount, col, QtGui.QTableWidgetItem(str(value)))

    def saveDataToFile(self, data, fileName):
        np.savetxt(fileName,data, fmt='%10.5f')


def main():
    app = QtGui.QApplication(sys.argv)
    form = AppForm(specterCenter=130, columnNumber=255, windowLength=51)
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()