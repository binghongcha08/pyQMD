import numpy as np 
import matplotlib.pyplot as plt 

import scipy 

#print(scipy.constants.value(u'hartree-inverse meter relationship'))

def plt_pes():
 
    #data = np.genfromtxt('pes.out')
    
    x = np.linspace(0.1,10,200)
    a, x0 = 1.02, 1.4 
    
    De = 0.176/1000
    
    d = (1.0-np.exp(-a*(x-x0)))
        
    v0 = De*(d**2-1.0)

    plt.figure()  
    plt.plot(x, v0,'b-',lw=3) 

    #plt.ylim(-0.001,0.01)
    #plt.xlim(2,10) 

def plt_en(ax1,ax2):

    data = np.genfromtxt(fname='en.out')
    
    #ax1.plot(data[:,0],data[:,2],linewidth=2,label='Potential')
    ax1.plot(data[:,0],data[:,3],linewidth=2,label='Quantum Potential')
    ax1.plot(data[:,0],data[:,4],linewidth=2,label='Energy')
      
    #ax1.legend() 
	#pl.legend(bbox_to_anchor=(0.5, 0.38, 0.42, .302), loc=3,ncol=1, mode="expand", borderaxespad=0.)
	
	
    ax2.plot(data[:,0],data[:,1],linewidth=2,label='K')
    ax2.legend() 


#plt.legend()
    ax2.set_ylabel('Energy [hartree]')



#plt.savefig('energy.pdf')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1) 
	
plt_en(ax1, ax2) 
plt.show() 


