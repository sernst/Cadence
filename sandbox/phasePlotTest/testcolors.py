import pylab as plt

from numpy import outer

plt.rc('text', usetex=False)
a=outer(plt.arange(0,1,0.01),plt.ones(10))
plt.figure(figsize=(10,5))
plt.subplots_adjust(top=0.8,bottom=0.05,left=0.01,right=0.99)

colormap=plt.get_cmap("seismic")

plt.imshow(a,aspect='auto',cmap=plt.get_cmap("seismic"),origin="lower")

print colormap(0.5)
plt.show()


