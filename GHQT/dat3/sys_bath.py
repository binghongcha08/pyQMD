# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 09:42:22 2016

@author: bing
"""
import numpy as np
#import scipy  
import numba 
import sys 




bohr_angstrom = 0.52917721092
hartree_wavenumber = 219474.63 

#hartree_wavenumber = scipy.constants.value(u'hartree-inverse meter relationship') / 1e2 


def M1mat(a, Nb):
    
    M1 = np.zeros((Nb,Nb)) 

    for m in range(Nb-1):
        M1[m,m+1] = np.sqrt(float(m+1)/2.0/a)

    M1 = Sym(M1) 

    return M1 

def M2mat(a, Nb):
    
    M2 = np.zeros((Nb,Nb)) 

    for m in range(Nb):
        M2[m,m] = (float(m) + 0.5)/a 
    
    if Nb > 1: 
        for m in range(Nb-2):
            M2[m,m+2] = np.sqrt(float((m+1)*(m+2)))/2.0/a 

    M2 = Sym(M2)

    return M2 

def M3mat(a, Nb):
    
    M3 = np.zeros((Nb,Nb)) 

    for m in range(Nb-1):
        M3[m,m+1] = 3.0 * (float(m+1)/2./a)**1.5 

    if Nb > 2:
        for m in range(Nb-3):
            M3[m,m+3] = np.sqrt(float((m+1)*(m+2)*(m+3))) / (2.0*a)**1.5 
    
    M3 = Sym(M3) 

    return M3 

def M4mat(a, Nb):
    
    M4 = np.zeros((Nb,Nb))

    for m in range(Nb):
        M4[m,m] =  float(3.0 * m**2 + 3.0 * (m+1)**2) / (2.*a)**2
    
    if Nb > 1: 
        for m in range(Nb-2):
            M4[m,m+2] = (4.0*m + 6.0) * np.sqrt(float((m+1)*(m+2))) / (2.*a)**2
            
    if Nb > 3: 
        for m in range(Nb-4):
            M4[m,m+4] = np.sqrt(float((m+1)*(m+2)*(m+3)*(m+4))) / (2.0*a)**2

    M4 = Sym(M4) 

    if Nb > 1:
        if not M4[0,1] == M4[1,0]: 
            print(M4) 
            print('\n ERROR: Not symmetric matrix M4.\n')
            sys.exit() 
    return M4


def Hermite(x):

    cons = np.array([1. / np.sqrt(float(2**n) * float(math.factorial(n))) for n in range(Nb)])
    
    H = [] 
    H.append(1.0) 
    H.append( x * 2.0 ) 
    if Nb > 2:
        for n in range(2,Nb):
            Hn = 2.0 * x * H[n-1] - 2.0*(n-1) * H[n-2]
            H.append(Hn)
    
    for n in range(Nb):
        H[n] = H[n]*cons[n] 

    return H

#    if n == 0: 
#        H.append(1.)  
#    elif n == 1: 
#        return 2. * x * cons 
#    elif n == 2: 
#        return (4. * x**2 - 2.) * cons   
#    elif n == 3: 
#        return (8.0 * x**3 - 12.0 * x) * cons 
#    elif n == 4:
#        return (16.0 * x**4 - 48.0 * x**2 + 12.0) * cons 
#    elif n == 5:
#        return (32.0*x**5 - 160.0*x**3 + 120.0*x) * cons 
#    elif n == 6: 
#        return ()

def Vx(x):
    
    g = 0.1    
    return  x**2/2.0 + g * x**4 / 4.0

def Kmat(alpha,pAve, Nb):

    K = np.zeros((Nb,Nb),dtype=complex)

    ar = alpha.real 

    for j in range(Nb): 
        K[j,j] = np.abs(alpha)**2 / ar * (2. * j + 1.)/2. +  pAve**2 
    
    for j in range(1,Nb):
        K[j-1,j] = -1j*np.conj(alpha) * pAve * np.sqrt(2. * j / ar)
        K[j,j-1] = np.conj(K[j-1,j])

    if Nb > 2: 
        for j in range(2,Nb):
            K[j-2,j] = - np.sqrt(float((j-1)*j)) * np.conj(alpha)**2 / 2. / ar  
            K[j,j-2] = np.conj(K[j-2,j])
    

    #K[0,0] = np.abs(alpha)**2/alpha.real / 2. + pAve**2
    #K[1,1] = np.abs(alpha)**2/alpha.real * 3.0 / 2. + pAve**2 

    #K[0,1] = -1j*np.conj(alpha) * pAve * np.sqrt(2.*j/alpha.real)
    #K[1,0] = np.conj(K[0,1])
    K = K / (2.*amx) 

    return K 

def Sym(V):
    n = V.shape[-1]
    
    for i in range(n):
        for j in range(i):
            V[i,j] = V[j,i] 
    return V 

@numba.autojit
def Vint(x,y):
    """
    interaction potential between x and y     
    """ 
    
    PES = 'HO' 
    
    if PES == 'Morse':
        
        a, x0 = 1.02, 1.4 
        De = 0.176 / 100.0 
    
        d = (1.0-np.exp(-a*x))
        
        v0 = De*d**2
            
        dv = 2. * De * d * a * np.exp(-a*x)
        
    elif PES == 'HO':
        
        v0 = x**2/2.0  + y**2/2.0 
         

    elif PES == 'AHO':
        
        eps = 0.4 
        
        v0 = x**2/2.0 + eps * x**4/4.0 
        dv = x + eps * x**3  
        #ddv = 2.0 * De * (-d*np.exp(-a*((x-x0)))*a**2 + (np.exp(-a*(x-x0)))**2*a**2)

#    elif PES == 'pH2':
#        
#        dx = 1e-4
#        
#        v0 = np.zeros(Ntraj)
#        dv = np.zeros(Ntraj)
#        
#        for i in range(Ntraj):
#            v0[i] = vpot(x[i])
#            dv[i] = ( vpot(x[i] + dx) - v0[i])/dx
        
    return v0 

def Vy(y):
    v0 = y**2/2.0
    dv = y
    return v0,dv 
    
@numba.autojit
def qpot(x,p,r,w):

    """
    Linear Quantum Force : direct polynomial fitting of derivative-log density (amplitude)    
    curve_fit : randomly choose M points and do a nonlinear least-square fitting to a 
            predefined functional form      
    """
    
    #tau = (max(xdata) - min(xdata))/(max(x) - min(x))
    #if tau > 0.6:
    #    pass 
    #else: 
    #    print('Data points are not sampled well.'
    am= amy 
    
    Nb = 2
    S = np.zeros((Nb,Nb))
    
    for j in range(Nb):
        for k in range(Nb):
            S[j,k] = np.dot(x**(j+k), w)  
    
    bp = np.zeros(Nb)
    br = np.zeros(Nb)
    
    for n in range(Nb):
        bp[n] = np.dot(x**n * p, w)
        br[n] = np.dot(x**n * r, w)
        
        
    cp = np.linalg.solve(S,bp)
    cr = np.linalg.solve(S,br)  

    #unit = np.identity(Nb)
    #r_approx = cr[0] * unit + cr[1] * x + cr[2] * x**2 + cr[3] * x**3 
    #p_approx = cp[0] * unit + cp[1] * x + cp[2] * x**2 + cp[3] * x**3

    N = len(x)
    
    dr = np.zeros(N)
    dp = np.zeros(N)
    ddr = np.zeros(N)
    ddp = np.zeros(N)
    
    for k in range(1,Nb):    
        dr += float(k) * cr[k] * x**(k-1) 
        dp += float(k) * cp[k] * x**(k-1)  
    
    for k in range(2,Nb-1):
        ddr += float(k * (k-1)) * cr[k] * x**(k-2) 
        ddp += float(k * (k-1)) * cp[k] * x**(k-2) 
    
    fr =  -1./2./am * (2. * r * dp + ddp)
    fq = 1./2./am * (2. * r * dr + ddr)  
    
    Eu = -1./2./am * np.dot(r**2 + dr,w)
        
    return Eu,fq,fr 



# initialization 
# for DOF y : an ensemble of trajectories 
# for DOF x : for each trajectory associate a complex vector c of dimension M 
   
Ntraj = 1024*2
M = 8  
ax = 1.0 # width of the GH basis 
ay0 = 4.0   
y0 = 0.0  

# initial conditions for c 
c = np.zeros((Ntraj,M),dtype=np.complex128)

c[:,0] = 1.0/np.sqrt(2.0)+0j
c[:,1] = 1.0/np.sqrt(2.0)+0j
for i in range(2,M):
    c[:,i] = 0.0+0.0j


# ---------------------------------
# initial conditions for QTs     
   
y = np.random.randn(Ntraj)     
        
y = y / np.sqrt(2.0 * ay0) + y0 
py = np.zeros(Ntraj)
ry = - ay0 * (y-y0) 

w = np.array([1./Ntraj]*Ntraj)

# -------------------------------

amx = 1.0 
amy = 10.0  

f_MSE = open('rMSE.out','w')
nout = 20       # number of trajectories to print 
fmt =  ' {}' * (nout+1)  + '\n'  
Eu = 0.  

Ndim = 1           # dimensionality of the bath   
fric_cons = 0.0      # friction constant  


Nt = 2**12
dt = 1.0/2.0**9
dt2 = dt/2.0 
t = 0.0 

print('time range for propagation is [0,{}]'.format(Nt*dt))
print('timestep  = {}'.format(dt))
    
# construct the Hamiltonian matrix for anharmonic oscilator 
g = 0.10 
V = 0.5 * M2mat(ax,M) + g/4.0 * M4mat(ax,M)
K = Kmat(ax,0.0,M)
H = K+V

print('Hamiltonian matrix in DOF x = \n')
print(H)
print('\n')


@numba.autojit
def fit_c(c,y):
    """
    global approximation of c vs y to obtain the derivative c'',c'     
    """
    dc = np.zeros((Ntraj,M),dtype=np.complex128)
    ddc = np.zeros((Ntraj,M),dtype=np.complex128)
    
    for j in range(M):

        z = c[:,j]
        p = np.polyfit(y,z,3)
        
        for k in range(Ntraj):
            dc[k,j] = 3.0 * p[0] * y[k]**2 + p[1] * 2.0 * y[k]  
            ddc[k,j] = 6.0 * p[0] * y[k] + 2.0*p[1]  
            
    return dc, ddc
    
@numba.autojit 
def prop_c(H,c,y,ry,py):
    
    dc, ddc = fit_c(c,y)
    
    eps = 0.25e0 # bilinear coupling Vint = eps*x*y
    
    for k in range(Ntraj):
        
        Vp = eps * y[k] * M2mat(ax,M) 
        tmp = (H+Vp).dot(c[k,:]) - ddc[k,:]/2.0/amy - dc[k,:] * (ry[k] + 1j*py[k])/amy 
        tmp *= -1j

        c[k,:] += tmp * dt 
       
    return c 
    
@numba.autojit 
def xAve(c,y,w):
    """
    compute expectation value of x     
    """
    Xmat = M1mat(ax,M)

    x_ave = 0.0+0.0j    
    for k in range(Ntraj):
        for m in range(M):
            for n in range(M):
              x_ave += Xmat[m,n] * np.conjugate(c[k,m]) * c[k,n] * w[k]   
    
    return x_ave.real 
    
# propagate the QTs for y 


# update the coeffcients for each trajectory 
fmt_c = ' {} '*(M+1)
  
f = open('traj.dat','w')
fe = open('en.out','w')
fc = open('c.dat','w')
fx = open('xAve.dat','w')

v0, dv = Vy(y)
Eu,fq,fr = qpot(y,py,ry,w)

for k in range(Nt):
    
    t = t + dt 

    py += (- dv + fq) * dt2 - fric_cons * py * dt2   
    ry += fr * dt2
    
    y +=  py*dt/amy

    # force field 
    Eu, fq, fr = qpot(y,py,ry,w)
    if Eu < 0:
        print('Error: U = {} should not be negative. \n'.format(Eu))
        #sys.exit()
        
    v0, dv = Vy(y)

    py += (- dv + fq) * dt2 - fric_cons * py * dt2 
    ry += fr * dt2 
    
    # update c 
    
    c = prop_c(H,c,y,ry,py)
    
    #  output data for each timestep 
    x_ave = xAve(c,y,w)
    fx.write('{} {} \n'.format(t,x_ave))
           
    f.write(fmt.format(t,*y[0:nout]))
    fc.write('{} {} {} {} {} \n'.format(t, *c[0,:]))
    
    Ek = np.dot(py*py,w)/2./amy  
    Ev = np.dot(v0,w) 
    Eu = Eu 
    Etot = Ek + Ev + Eu
    
    fe.write('{} {} {} {} {} \n'.format(t,Ek,Ev,Eu,Etot))
    
    if k == Nt-1:
        print('The total energy = {} Hartree. \n'.format(Etot))

fe.close()
f.close() 
fc.close()
fx.close()


#a, x0, De = 1.02, 1.4, 0.176/100 
#print('The well depth = {} cm-1. \n'.format(De * hartree_wavenumber))
#
#omega  = a * np.sqrt(2. * De / am )
#E0 = omega/2. - omega**2/16./De
#dE = (Etot-E0) * hartree_wavenumber 
#print('Exact ground-state energy = {} Hartree. \nEnergy deviation = {} cm-1. \n'.format(E0,dE))
#    


    
