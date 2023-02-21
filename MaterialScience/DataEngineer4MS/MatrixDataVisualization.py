
#load needed packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
from scipy import linalg

#read in data from matlab
#using 
#https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html
data_C = scipy.io.loadmat('CYLINDER.mat')
print(data_C)

#a sample data is like this
# sample = scipy.io.loadmat('CYLINDER.mat')
# print(sample)
sample = np.array([[1,2,3,4],[5,6,7,8],[2,3,4,2],[5,6,9,8]])
Us, ss, Vs = np.linalg.svd(sample)
print(Us)

#plotting
# plotting the first five modes (columns) of the orthogonal matrix
#first 4 modes
def plotOrthogomalModes(num,U):
  for i in range(num):
    mode = U[:,i]
    plt.plot(mode, label = f"Mode {i+1}")
  plt.title("First Five Modes of U")
  plt.legend()
  plt.show()

#c plot the first 50 sigmas of the eigen value matrix
def plotSemilogy(num,s):
  plt.title("First %d modes in S" % num)
  plt.semilogy(s[:num,:num], label = 'singular values')
  plt.legend()
  plt.show()


#compute the ratios for first r sigmas
# d compute ratios
def captureRatio(s,r):
  sum_r = 0
  #acquire the total sum square data
  sum_n = np.sum(np.square(ss))
  print(sum_n)
  sigmas = []
  #loop over the first r values
  for i in range(r):
    sum_r = np.sum(np.square(ss[0:i][0:i]))
    if sum_r > 0.99:
      print("It takes %d sigmas to capture 99% of the flow" % i )
    sigmas.append(sum_r/sum_n)
    print(sum_r/sum_n)
# to plot the ratios
  plt.title("Sigmas Ratio")
  plt.plot(sigmas, label = 'ratio')
  plt.xticks(np.arange(len(ss)), np.arange(1,len(ss)+1))
  plt.legend()
  plt.show()
