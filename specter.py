import numpy as np

class Specter:

    def __init__(self,data,specterCenter,windowLength=21):
        self.data=data[:,1:]                        # specter data
        self.wavelength=data[:,0]                   # wavelength
        self.windowLength=windowLength              # the dimension of the smoothing window; should be an odd integer
        self.specterCenter=specterCenter            # coordinate of specter center row

        colSmooth=[]
        colSplit=[]
        colCombine=[]

        for i,col in enumerate(self.data):
            colSmooth.append(self.smooth(col,self.windowLength))
            colSplit.append(self.split(colSmooth[i],self.specterCenter))
            colCombine.append(self.combine(colSplit[i]))

        self.dataSmooth=np.array(colSmooth)          # smoothed specter
        self.dataSplit=np.array(colSplit)            # right and left halves of a specter
        self.dataCombinedHalf=np.array(colCombine)   # half of a specter? combined from 2 halves

    def smooth(self,x,window_len=51,window='hanning'):
        """smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
           x: the input signal
           window_len: the dimension of the smoothing window; should be an odd integer
           window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
               flat window will produce a moving average smoothing.

        output:
           the smoothed signal
        """

        if x.ndim != 1:
            print("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            print("Input vector needs to be bigger than window size.")

        if window_len<3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            print("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


        s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]

        if window == 'flat': #moving average
           w=np.ones(window_len,'d')
        else:
           w=eval('np.'+window+'(window_len)')

        y=np.convolve(w/w.sum(),s,mode='valid')

        return y[(window_len/2-1):-(window_len/2)] #NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.

    def split(self,F,center):
        left=F[0:center-1]
        right=F[center:]
        left=left[::-1]

        if len(left)>len(right):
            zeros = np.zeros(len(right))
            zeros[0:len(right)]=left[0:len(right)]
            left=zeros
        elif len(left)<len(right):
            zeros = np.zeros(len(left))
            zeros[0:len(left)]=right[0:len(left)]
            right=zeros

        split = np.array([left,right]).transpose()
        return split

    def combine(self,split):
        return (split[:,0]+split[:,1])/2