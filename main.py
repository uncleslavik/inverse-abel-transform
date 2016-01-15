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

import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from abel import Abel
from specter import Specter

class Application:

    def __init__(self, dirPath, specterCenter, columnNumber, windowLength):
        self.specter=[]
        self.dirPath=dirPath
        self.specterCenter=specterCenter
        self.columnNumber=columnNumber
        self.windowLength=windowLength

    def loadSpecterFromFiles(self):
        fileList=glob.glob(self.dirPath+'*.asc')
        for fileName in fileList:
            self.specter.append(Specter(np.loadtxt(fileName),self.specterCenter,self.windowLength))

    def showSpecterPlot(self):
        fig, ax = plt.subplots()
        cax = ax.imshow(app.specter[0].data, interpolation='nearest', cmap=cm.coolwarm )
        ax.set_title('Specter')
        #ax.set_xticklabels(app.specter[0].wavelength)
        plt.show()

    def showPlots(self):

        plt.subplot(3, 1, 1)
        plt.title("Signal & smoothed signal", size=13)
        plt.plot(app.specter[0].data[self.columnNumber,:],'k.')
        plt.plot(app.specter[0].dataSmooth[self.columnNumber,:],'r-')

        plt.subplot(3, 1, 2)
        plt.title("Two halves and combined", size=13)
        plt.plot(app.specter[0].dataSplit[self.columnNumber,:])
        plt.plot(app.specter[0].dataCombinedHalf[self.columnNumber,:], 'k--')

        plt.subplot(3, 1, 3)
        plt.title("Abel inverse transform", size=13)
        plt.plot(Abel.transform(app.specter[0].dataCombinedHalf[self.columnNumber,:]), 'r-')

        plt.show()

app=Application('test-data/', 130, 255, 11)
app.loadSpecterFromFiles()
app.showSpecterPlot()
app.showPlots()



print(app.specter[0].dataSplit[255][:,1])

plt.plot(Abel.transform(app.specter[0].dataSplit[255][:,1]), 'r-')
plt.show()