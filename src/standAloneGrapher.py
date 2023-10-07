import cv2 as cv2
import multiprocessing
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import numpy as np
#This whole section of code is far to complicated and messy for me to explain in comments, good luck figuring it out
def coordinator(pathToData):
    data = loadData(pathToData)
    #myplot(data[0],data[1],20)
    graph(data[0],data[1])
    
def graph(foundData,loopNumber):
    total = loopNumber[-1]
    ticks = []
    labels = []
    iteration = 0
    for i in range(total):
        if iteration % 120 == 0:
            ticks.append(iteration)
            labels.append(str(int(iteration/120)))
        iteration = iteration + 1
    x,y=(smoothing(foundData,loopNumber))
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(6, 8))
    ax = fig.add_subplot(111)
    ax.set_xlim([0, total])
    ax.set_xticks(ticks,labels,rotation=15)
    ax.set_xlabel("Time (mins)")
    ax.set_ylabel("Data")
    ax.plot(x,y)
    plt.show()
    plt.pause(1000)

def myplot(x, y, s, bins=(int(5461/5),int(4096/5))):
    map = 'maps/mapWE4by3.png'
    
    img =  cv2.cvtColor(cv2.imread(map), cv2.COLOR_BGR2RGB)
    img = cv2.flip(cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),0)
    width = int(img.shape[1] / 5)
    height = int(img.shape[0] / 5)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    img = img.astype('float32')/255

    # resize image
    
    fig = plt.figure(figsize=(6, 8))
    ax = fig.add_subplot(111, projection='3d')
    z, xedges, yedges = np.histogram2d(x,y, bins=bins,range=[[0,5461],[0,4096]])
    z = gaussian_filter(z, sigma=s)
    z=np.log1p(z)
    #extent = [xedges[0], xedges[-0], yedges[0], yedges[-0]]
    yedges = yedges[:-1]
    xedges = xedges[:-1]
    X, Y = np.meshgrid(yedges, xedges)
    #img, extent = myplot(x, y, s)
    plt.axis('off')
    #ax.plot_surface(X, Y, heatmap, linewidth=1, antialiased=True,cstride=5, rstride=5)
    #x1, y1 = np.ogrid[0:img.shape[0], 0:img.shape[1]]
    #x12, y12 = np.meshgrid(x1, y1)
    # stride args allows to determine image quality 
    # stride = 1 work slow
    #ax.plot_surface(x12, y12, np.atleast_2d(-2), rstride=4, cstride=4, facecolors=img)
    
    #ax.plot_surface(X, Y, heatmap,linewidth=1, cmap=cm.jet,antialiased=True)
    print(len(X))
    print(len(Y))
    print(len(z))
    ax.plot_surface(X, Y, z, linewidth=5, antialiased=True,facecolors=img,rstride=4, cstride=4)
    plt.ion()
    plt.show()
    #plt.imshow(heatmap.T, extent=extent, origin='upper',interpolation='none',cmap=cm.jet,vmin=0, vmax=100)
    plt.pause(999)

    
def loadData(pathToData):
    a =  np.asarray(np.load(pathToData))
    return a



def smoothing(y,x):
    y = filterValues(y)
    lowess_frac = 0.0001 # size of data (%) for estimation =~ smoothing window
    lowess_it = 0
    lowess_delta = 2
    x_smooth = x
    y_smooth = lowess(y, x, is_sorted=False, frac=lowess_frac, it=lowess_it, delta=lowess_delta, return_sorted=False)
    return x_smooth, y_smooth


def filterValues(values):
    loopNumber = 2
    newValues = values.copy()
    for i in values:
        loopNumber = loopNumber + 1
        if loopNumber > len(values)-2:
            break
                
        if values[loopNumber-1]==values[loopNumber+1]:
            newValues[loopNumber]=values[loopNumber-1]
    return newValues

if __name__ == "__main__":
    print('Starting standalone grapher')
    pathToData = 'outputdata/playerHealthData.npy'
    process1 = multiprocessing.Process(target=coordinator, args=(pathToData,))
    process1.start()
