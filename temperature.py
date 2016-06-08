import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

class Tempereture:

    @staticmethod
    def compute(specter,lines):
        h=6.62606957*10**-34
        c=3*10**8
        kb=1.3806488*10**-23

        temp=[]
        z=[]

        for row, spec in enumerate(np.transpose(specter)):

            tempData=[]

            for key, line in enumerate(lines):
                intLine = sp.trapz(spec[line[0]:line[1]])

                #print(intLine)
                lambdaNist=line[2]
                Aki=line[3]
                Ek=line[4]
                g=line[5]
                if intLine>0:
                    nkgk=np.log(intLine/((h*c*Aki*g)/lambdaNist))
                    tempData.append((Ek,nkgk))

            if len(tempData)>0:
                tempArray=np.array(tempData)
                print(tempArray)
                koef=np.polyfit(tempArray[:,0], tempArray[:,1], 1)
                temp.append(koef[0])
                z.append(row)



        print(temp)
        plt.plot(z,temp)
        plt.show()