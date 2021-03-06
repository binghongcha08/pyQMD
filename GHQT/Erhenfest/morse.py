# TD quantum dynamics with TD Gauss-Hermite basis 
# Two basis only
# Test anharmonic system 

import numpy as np
from math import *  
import numba 

Ntraj = 1000 
print('Number of trajectories = {} \n'.format(Ntraj))

dt = 0.5
am = 918.0

# initial values has to be stored to compute autocorrelation function 
ho =  dict({'x0' : -1.0, 'p0' : 0.0, 'alpha0' : 1.+0j}) # harmonic oscilator 
morse = dict({'x0' : 1.3, 'p0' : 0.0, 'alpha0' : 2.0 * 9.16+0j})


x0 = morse['x0']
p0 = morse['p0'] 
alpha0 = morse['alpha0']  
 

alpha = alpha0 
a = alpha.real 
b = alpha.imag


Nt = input('Time interval = {} \n How many time steps? '.format(dt))
p = np.zeros(Ntraj)

# phaes of quantum trajectories 
s = np.zeros(Ntraj)

sampling = 'uniform' 
if sampling == 'normal':

    x = np.random.randn(Ntraj)/np.sqrt(2.0*alpha.real) + x0 
    w = np.array([1.0/float(Ntraj)]*Ntraj)

elif sampling == 'uniform':
    # use uniform sampling between [xmin, xmax]
    xmin = 0.01 
    xmax = 6  
    x = np.linspace(xmin,xmax,Ntraj) 
    dx = x[1]-x[0] 
    w = np.sqrt(a/np.pi) * np.exp(-a*(x-x0)**2) * dx 
else: 
    print('There is no {} sampling'.format(sampling))



g = 0.1 # anharmonic constant in potential  

@numba.autojit
def derivs(x):
    
    # harmonic oscilator     
    #v0 =  x**2/2.0 + g * x**4 / 4.0 
    #dv =  x + g * x**3 
    #ddv = 1.0 + 3.0 * g * x**2 

    # morse oscilator 
    a, x0, De = 1.02, 1.4, 0.176
    
    d = (1.0-np.exp(-a*(x-x0)))
    
    v0 = De*d**2
    
    dv = De * 2.0 * d * a * np.exp(-a*(x-x0))
    
    ddv = 2.0 * De * (-d*np.exp(-a*((x-x0)))*a**2 + (np.exp(-a*(x-x0)))**2*a**2)
        
    return v0, dv, ddv
    
#@numba.autojit
#def Hessian(x):
#    V0 =  x**2/2.0 + g*x**4/4. 
#    V1 =  x + g * x**3
#    V2 =  1.0 + 3.0 * g * x**2
#
#    return V0,V1,V2

@numba.autojit 
def LQF(x,w,xAve,var):
    
    a = 1. / 2. / var 
    r = - a * (x-xAve) 
    dr = - a 

    u =  -1.0 / 2.0 / am * ( r**2 + dr ) 
    
    du = -1./am * (r*dr)

    return u, du 

def qpot(x,w,xAve,xVar):

    alpha =  1.0 / xVar / 2.0 
    z = x - xAve 

    g0 = (alpha/2./np.pi)**0.5 * np.exp(-alpha*z**2/2.)
    g1 = z*g0

    s00 = np.sqrt(alpha/np.pi)/2.0
    s11 = 1./4./np.sqrt(alpha*np.pi) 

    b0 = np.dot(g0,w) 
    b1 = np.dot(g1,w) 

    # c0 = b0/s00 
    c0 = 1.0 
    c1 = b1/s11

    P = c0*(-alpha*(x-xAve)) + c1*(-alpha + alpha**2*(x-xAve)**2)
    dP = - alpha*c0 + c1 * alpha**2 * 2.0*(x-xAve) 
    ddP = 2.0 * c1 * alpha**2

    Q = c0 + c1*(x-xAve)     
    dQ = c1 
    # ddQ = 0.0, ignore P*ddQ/Q
    r = 0.5 * P/Q
    dr = 0.5 *(-P*dQ/Q**2 + dP/Q)
    ddr = 0.5 * (-(dP*dQ/Q**2 - P*dQ*dQ/Q**3) + (ddP/Q - dP*dQ/Q**2))

    du = -(2.0*r*dr + ddr)/2.0/am 

    uAve = np.dot(r**2,w)/2./am 

    return uAve,du  

def expand(alpha,V1,V2,x,xAve,pAve,w,c): 

    """
    Compute potential matrix elements using to propagate coefficients c      
    
    z = x - xAve 
    V = < m | DeltaV | n >     
    Hermite polynomails 
    H0 = 1. 
    H1 = z * sqrt(2.) 
    H2 = (4. * z**2 - 2.) / 4. / sqrt(2.) 
    """
    a = alpha.real 

    V = Vmat(a,x,xAve,w)
    #K = Kmat(alpha,x,pAve)
    #D = Dmat(alpha,xAve,pAve)

    V0 = derivs(xAve)[0] 

    matV0 = np.identity(Nb)
    matV0 = matV0 * V0 

    M1 = M1mat(a) 
    M2 = M2mat(a) 

    matK = np.identity(Nb) 
    for j in range(Nb):
        matK[j,j] = float(j) * a/am 



    #f6.write(' {} {} '.format(t,np.vdot(c,(K+V).dot(c)).real))

    #V[0,2] = np.dot(DeltaV * H0 * H2, w)
    #V[1,2] = np.dot(DeltaV * H1 * H2, w) 

    #V = symmetrize(V)

    #V[1,1] = np.dot(DeltaV * H1 * H1, w) 
    #V[2,2] = np.dot(DeltaV * H2 * H2, w) 

    dc = (-1j* (-matV0 - V1 * M1 - V2/2.0 * M2 + V + matK )).dot(c)

    return dc 

@numba.autojit
def gwp_vp(a,x,xAve,w,c):
    """
    Variational principle used to determine effective potential used to propagate the GWP     
    V = V0 + V1*(x-xAve) + V2*(x-xAve)**2/2
    V1 = <V'>, V2 = <V''>
    """

    indicator = 'average_phi0' 
    
    z = np.sqrt(a)*(x-xAve)

    v0, dv, ddv = derivs(x)
        
    if indicator == 'average_psi':
    
        mat_dv = np.zeros((Nb,Nb))
        mat_ddv = np.zeros((Nb,Nb))
        
        H = Hermite(z) # Hermite polynomails 
    
        for i in range(Nb):
            for j in range(i+1):
                mat_dv[j,i] =  np.dot(dv * H[i] * H[j], w)
                mat_ddv[j,i] = np.dot(ddv * H[i] * H[j], w)
        
        mat_dv = sym(mat_dv) 
        mat_ddv = sym(mat_ddv)
    
        V1 = np.vdot(c,mat_dv.dot(c)).real 
        V2 = np.vdot(c,mat_ddv.dot(c)).real 
    
    elif indicator == 'average_phi0': # average computed with ensemble only 
    
    
        V1 = np.dot(dv, w)
        V2 = np.dot(ddv, w)
    
    elif indicator == 'CT': # classical force and Hessian at qt  
        
        V0, V1, V2 = derivs(xAve)
        

    return V1,V2 

@numba.autojit 
def Vmat(a,x,xAve,w):

    z = (x - xAve)*np.sqrt(a)
    #H0 = 1.0 
    #H1 = z * np.sqrt(2.)

    V = derivs(x)[0] 
    #V0 = Potential(xAve) 
    #V = V - V0 

    #v = V0 * np.identidy(Nb) 
    
    Vm = np.zeros((Nb,Nb))
    
    H = Hermite(z) # Hermite polynomails 

    order = 4 # highest-order in popential energy 
    
    for i in range(Nb):
        for j in range(max(i-order,0), i+1):
            Vm[j,i] =  np.dot(V * H[i] * H[j], w)

    #Vm = symmetrize(Vm) 
    for i in range(Nb):
        for j in range(i):
            Vm[i,j] = Vm[j,i] 

    #Vm[0,0] = np.dot(V,w) 
    #Vm[0,1] = np.dot(V * H[] * H1, w) 
    #Vm[1,1] = np.dot(V * H1 * H1, w)    
    #Vm[1,0] = Vm[0,1] 

    return Vm 


def Hermite(x):
    """
    Define Hermite polynomials multipiled by the normalization constant.  
    Corresponding to the eigenstates of harmonic oscilator. 
    """

    cons = np.array([1. / np.sqrt(float(2**n * factorial(n))) for n in range(Nb)])
    
    H = [] 
    H.append(1.0) 
    H.append( x * 2.0 ) 
    if Nb > 2:
        for n in range(2,Nb):
            Hn = 2.0 * x * H[n-1] - 2.0*(n-1) * H[n-2]
            H.append(Hn)
    
    for n in xrange(Nb):
        H[n] = H[n]*cons[n] 

    return H

@numba.autojit 
def M1mat(a):
    
    M1 = np.zeros((Nb,Nb)) 

    for m in range(Nb-1):
        M1[m,m+1] = np.sqrt(float(m+1)/2.0/a)

    M1 = sym(M1) 

    return M1 
    
@numba.autojit
def M2mat(a):
    
    M2 = np.zeros((Nb,Nb)) 

    for m in range(Nb):
        M2[m,m] = (float(m) + 0.5)/a 
    
    if Nb > 1: 
        for m in range(Nb-2):
            M2[m,m+2] = np.sqrt(float((m+1)*(m+2)))/2.0/a 

    M2 = sym(M2)

    return M2 



@numba.autojit
def Kmat(alpha,x,pAve):

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
    K = K / (2.*am) 

    return K 
    
@numba.autojit
def Dmat(alpha,xAve,pAve):

    D = np.zeros((Nb,Nb),dtype=complex)

    V0, V1, ak  = Hessian(xAve) 

    # time derivative 
    dq = pAve / am
    dp = - V1
    da = (-1.0j/am * alpha**2 + 1.j * ak) 
    
    a = alpha.real 

    for k in range(Nb):
        D[k,k] = - 1j*da.imag/2./a * (float(k) + 0.5) - 1j * pAve**2/am    
    
    for k in range(1,Nb):
        D[k-1,k] = np.sqrt(float(k)/2./a) * ( - np.conj(alpha) * dq + 1j * dp) 
        D[k,k-1] = np.sqrt(float(k)/2./a) * ( alpha * dq + 1j * dp )
    
    if Nb > 2: 
        for k in range(2,Nb):
            D[k-2,k] = np.conj(da)/2./a * np.sqrt(float(k*(k-1)))/2.0 
            D[k,k-2] = - da/2./a * np.sqrt(float(k*(k-1)))/2.0
            


    #D[0,0] = - 1j * pAve**2 / am 
    #D[1,1] = - 1j * pAve**2 / am 
    #D[0,1] = - (np.conj(alpha)*pAve/am + 1j * V1) / np.sqrt(2.*alpha.real)
    #D[1,0] = (alpha * pAve / am - 1j * V1) / np.sqrt(2.*alpha.real)

    return D 


def sym(V):
    n = V.shape[-1] 
    for i in range(n):
        for j in range(i):
            V[i,j] = V[j,i] 
    return V 
    


def SaveWf(alpha, pAve, S,c,xAve,xVar,fname='wft.dat'):
    """
    save wavefunction to file 
    """
    f = open(fname,'w')
    
    x = np.linspace(xmin,xmax,200) 

    a = alpha.real 
    z = (x - xAve) * np.sqrt(a) 

    #print('GWP width parameter {}, Real alpha {}'.format(a,alpha.real))

    phi0 = np.exp( - alpha * (x-xAve)**2/2.0 + 1j*pAve*(x-xAve) + 1j * S)
    
    H = Hermite(z) 

    basis = [] 
    for i in range(Nb):
        basis.append(H[i]*phi0)
    #phi1 = Hermite(z,1) * phi0 
    #phi2 = Hermite(z,2) * phi0 
    #phi2 = (4. * z*z - 2.) / 4. / np.sqrt(2.) * phi0 

    for i in xrange(len(x)):
        wf = 0.+0.j 
        for j in xrange(Nb):
            wf += c[j]*basis[j][i] 
        f.write('{} {} {} \n'.format(x[i], wf.real,wf.imag))

    f.close() 


def xObs(a,c,x,xAve):
    """
    Compute <x> = tr[rho * M1] + xAve 
    """
    X = M1mat(a)
    
    y = np.vdot(c,X.dot(c)) 
    
    return  y.real + xAve 
    
def corr(alpha,w,x,xAve,c,pAve,s):
    """
    Compute correlation function 
    C(t) = <psi(0) | psi(t)> 
    For real initial wavefunction 
    C(t) = <psi(-t/2)|psi(t/2)> = psi(t/2)**2 = sum_n c_n**2    
    """
    a = alpha.real
    
    #phase = np.exp(1j*(- b * (x-xAve)**2 / 2.0 + pAve * (x-xAve) + S.real))
    #phase = phase**2  
    
    z = (x-xAve) * sqrt(a)
    
    H = Hermite(z) # Hermite polynomails multiplied with normalization constant  

    P = np.zeros((Nb,Nb), dtype=complex) # phase matrix elements
    
    for i in range(Nb):
        for j in range(i+1):
            P[j,i] =  sum(H[i] * H[j] * np.exp(2j*s) * w) 
    
    P = sym(P) 

    cor = np.dot(c,P.dot(c))
    
    return cor 
    
def corr_single_basis(alpha,w,x,xAve,c,pAve,S):

    """
    Compute correlation function for case of single basis. <g0|gt>     
    """
    
    global alpha0, x0, p0 
    
    a2 = -(np.conj(alpha0) + alpha) / 2.0 
    a1 = x0 * np.conj(alpha0) + xAve * alpha + 1j * (pAve - p0) 
    a0 = 1j * (S - np.conj(S0)) - (alpha0 * x0**2 + alpha * xAve**2) / 2.0 + 1j * (p0 * x0 - pAve * xAve) 
    
    return gwp_int(a2,a1) * np.exp(a0)
    
def gwp_int(a2,a1):
    """
    compute Gaussian integral int(exp( a2 * x**2 + a1 * x ), dx)    
    """
    return np.exp(-a1 * a1 / 4.0 / a2) * np.sqrt(np.pi/-a2)
    
@numba.autojit 
def overlap(aj,qj,pj,ak,qk,pk):
    """
    Gaussian integration with complex alpha <zj|zk> 
    """
    dq = qk - qj 
    dp = pk - pj 
    return (aj.real*ak.real)**0.25 * sqrt(2./(np.conj(aj) + ak))   * exp(    \
                -0.5 * np.conj(aj)*ak/(np.conj(aj)+ak) * (dp**2/np.conj(aj)/ak + dq**2  \
                + 2.0*1j* (pj/np.conj(aj) + pk/ak) *dq)  )
    
f1 = open('traj.dat', 'w')
f2 = open('xAve.dat', 'w')
f3 = open('energy.dat', 'w')
f4 = open('coeff.dat', 'w')
f5 = open('norm.dat', 'w')
f6 = open('energy.dat', 'w')
f_cor = open('corr.out', 'w')

t = 0.0
dt2 = dt/2.0 
S0 = -1j*np.log(a/np.pi)/4.0 # complex phase factor in GWP 
S = S0 

xAve = np.dot(x,w)
xSqdAve = np.dot(x*x,w) 
xVar = (xSqdAve - xAve**2) 


pAve = np.dot(p,w) 
print('\n Initial Time \n ')
print('Mean position = {}, Variance = {} '.format(xAve,xVar))
print('Initial momentum {}'.format(pAve))

# initial expansion coeffs
Nb = input('Please enter number of basis function \n ')
c = np.zeros(Nb,dtype=complex) 
c[0] = 1.0
# ----------
# initialize the force 

# classical Force Field 
V1,V2 = gwp_vp(a,x,xAve,w,c)
print('V1,V2 = {} {} '.format(V1,V2))

# effective potential and force field 
V0 = derivs(xAve)[0] 
Veff = V0 + V1 * (x-xAve) + V2/2.0 * (x-xAve)**2 

dv_eff = V1 + V2 * (x-xAve)

# quantum force 
u, du = LQF(x,w,xAve,xVar)
uAve = sum(u * w)

V = derivs(x)[0]  
v = np.dot(V,w) 
print(' Quantum potential = {} \n '.format(uAve))
#print(' Potential = {} \n '.format(vAve))
#print(' Total energy = {} \n '.format(uAve+vAve))
# ---------------




SaveWf(alpha, pAve, S, c, xAve,xVar,fname='wf0.dat') # save initial wavefunction 

# format for output data 
fmt = ' {} '*11 + '\n'
fmtC = ' {} '*(Nb+1) + '\n'

# update c for one timestep 
cold = c 
dc = expand(alpha,V1,V2,x,xAve,pAve,w,c)
c = c + dc*dt 

for k in range(Nt):
    
    t += dt 

    # leap-frog alg for {x,p}
    p = p - dv_eff*dt2 - du*dt2 
    
    x += p/am * dt2 
    s += (p * p / 2.0 / am - (Veff + u)) * dt 
    x += p/am * dt2 
    
    # compute observables 
    xAve = np.dot(x,w)
    xSqdAve = np.dot(x*x,w) 
    xVar = (xSqdAve - xAve**2) 
    
    # effective force fields
    V1,V2 = gwp_vp(a,x,xAve,w,c)
    #print('V1,V2 = {} {} '.format(V1,V2))
    Veff = V0 + V1 * (x-xAve) + V2/2.0 * (x-xAve)**2
    dv_eff = V1 + V2 * (x-xAve) 

    u, du = LQF(x,w,xAve,xVar)

    p += - dv_eff*dt2 - du*dt2 

    # average momentum, update phase parameters 
    pAve = np.dot(p,w) 

    alpha += (-1.0j/am * alpha**2 + 1.j * V2) * dt 
    #a = 1.0 / 2.0 / xVar 
    #b += (- (a**2 - b**2) / am + V2)*dt 
    a, b = alpha.real, alpha.imag 

    # S is the real part of the complex phase term, imaginary part is absorbed 
    # S contains the normalization constant N = exp(-S.imag)
    V0 = derivs(xAve)[0] 
    S  += ( pAve**2/2./am - V0 - alpha/2./am ) * dt 
    # classical action S += (pAve**2/2./am - V0 ) * dt 

    # update c, second-order difference 
    dc = expand(alpha,V1,V2,x,xAve,pAve,w,c)
    cnew = cold + 2.0*dc*dt 
    cold = c 
    c = cnew 

    # observables 
    xt = xObs(a,c,x,xAve)
    
    # correlation function 
    cor = corr(alpha,w,x,xAve,c,pAve,s) 
    f_cor.write('{} {} {} \n'.format(2.0 * t,cor.real, cor.imag))    
    
    f5.write( '{} {} \n'.format(t,np.vdot(cold,cold)))
    

    #vAve = np.dot(V,w)
    kAve = np.dot(p*p/2./am, w) 
    
    # overlap with a GWP ~ (xAve, xVar)
    #uAve = overlap(x,w,xAve,xVar) 
    #print('overlap with GWP {} \n'.format(ov))
    
    # save data 
    SaveWf(alpha, pAve,S, cold, xAve,xVar)

    f3.write('{} {} {} \n'.format(t,kAve,uAve))
    f1.write(fmt.format(t,*x[0:10]))
    f2.write(' {} {} {} {} {} \n'.format(t,xt, xAve,pAve,xVar))
    f4.write(fmtC.format(t,*np.abs(c[0:Nb])**2))

f1.close()
f2.close() 
f4.close() 
f3.close() 
f_cor.close() 


