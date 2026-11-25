import numpy as np, itertools
rng=np.random.default_rng(0); ok=lambda n,c: print(('PASS ' if c else 'FAIL ')+n)
# random positive Markoff triples from (3,3,3) by Vieta moves
def triples(k=200):
    out=[]; t=np.array([3.,3.,3.])
    for _ in range(k):
        i=rng.integers(3); j,l=[x for x in range(3) if x!=i]; t=t.copy(); t[i]=t[j]*t[l]-t[i]
        if t.max()>1e6: t=np.array([3.,3.,3.])
        out.append(t)
    return out
T=triples()
ok('triples on surface', all(abs(a*a+b*b+c*c-a*b*c)<1e-6*a*b*c for a,b,c in T))
# 2.3 / 2.7 series law
res=[]
for A,B,C in T:
    Cp=A*B-C; a,b,c,cp=2/A,2/B,2/C,2/Cp; res.append(abs(1/(c*cp)-(1/a**2+1/b**2))/(1/(c*cp)))
ok('series law 1/(cc\')=1/a^2+1/b^2', max(res)<1e-9)
# 3.7 DtN identity and rank
g=rng.uniform(0.1,1,3); G=g.sum(); L=np.diag(g)-np.outer(g,g)/G; x=rng.normal(size=3)
ok('3.7 DtN form', abs(x@L@x - sum(g[i]*g[j]*(x[i]-x[j])**2 for i,j in [(0,1),(0,2),(1,2)])/G)<1e-12 and np.linalg.matrix_rank(L)==2)
# 4.3 at (3,3,3)
g=np.full(3,4/18); L=np.diag(g)-np.outer(g,g)/g.sum(); ok('4.3 Lambda_0 = 2/27 P_A2', np.allclose(L,2/27*np.array([[2,-1,-1],[-1,2,-1],[-1,-1,2]])))
# 6.2 metric in A,B coords: dC=-dA-dB
M=np.zeros((2,2))
for i,(da,db) in enumerate([(1,0),(0,1)]):
    pass
def q(da,db):
    d=np.array([da,db,-da-db]); return (1/g.sum())*sum(g[i]*g[j]*(d[i]-d[j])**2 for i,j in [(0,1),(0,2),(1,2)])
Q=np.array([[q(1,0),(q(1,1)-q(1,0)-q(0,1))/2],[(q(1,1)-q(1,0)-q(0,1))/2,q(0,1)]]); ok('6.2 metric 2/9 [[2,1],[1,2]]', np.allclose(Q,2/9*np.array([[2,1],[1,2]])))
# 7.3 parametrisation and Vieta actions, 8.2 symplectic form
ok7=ok8=True
for _ in range(100):
    l=rng.uniform(0.3,3); u=rng.uniform(-4,4); A=2*np.cosh(l); B=2/np.tanh(l)*np.cosh(u-l); C=2/np.tanh(l)*np.cosh(u)
    ok7 &= abs(A*A+B*B+C*C-A*B*C)<1e-8*A*B*C
    ok7 &= np.isclose(2/np.tanh(l)*np.cosh(-u-l), A*C-B) and np.isclose(2/np.tanh(l)*np.cosh(2*l-u), A*B-C)
    h=1e-6; X=lambda u,l: (np.log(np.cosh(u-l)/np.sinh(l)), np.log(np.cosh(u)/np.sinh(l)))
    J=np.array([[(X(u+h,l)[k]-X(u-h,l)[k])/(2*h), (X(u,l+h)[k]-X(u,l-h)[k])/(2*h)] for k in (0,1)]); ok8 &= abs(np.linalg.det(J)-1)<1e-5
ok('7.3-7.7 parametrisation, V_B: u->-u, V_C: u->2l-u', ok7); ok('8.2 dx^dy = du^dl', ok8)
# 9.5 and 13.4 kinks
x,y=rng.normal(size=(2,1000)); ok('9.5 |x+y|+|x-y|=2max', np.allclose(abs(x+y)+abs(x-y),2*np.maximum(abs(x),abs(y))))
p,qq,r,s=2,1,1,1; E=lambda x: np.maximum(abs(p+qq*x),abs(r+s*x)); xs=np.linspace(-6,6,240001); d2=np.diff(E(xs),2)/(xs[1]-xs[0])
kinks=xs[1:-1][abs(d2)>1e-3*d2.max()]; ok('13.3 kinks at -(p-r)/(q-s), -(p+r)/(q+s)', np.allclose(sorted({round(k,2) for k in kinks}), sorted([-(p+r)/(qq+s), -(p-r)/(qq-s)]) if qq!=s else [-(p+r)/(qq+s)]))
# 14.3 ray
xn=[3,3]; [xn.append(3*xn[-1]-xn[-2]) for _ in range(10)]; lam=(3+5**.5)/2
ok('14.3 closed form', all(np.isclose(xn[n], 3*(5-5**.5)/10*lam**n+3*(5+5**.5)/10*lam**-n) for n in range(12)))
# 16.1 modular cusp
A=np.array([[2,1],[1,1]]); P=np.array([[-1,-6],[0,-1]]); ok('16.1 |tr AP^n| = 3(2n+1)', all(abs(np.trace(A@np.linalg.matrix_power(P,n)))==3*(2*n+1) for n in range(20)))
# 18.2/18.3, 19.1/19.2, 22.2
a_,b_=3.,6.; d=a_/b_; ok18=all(np.isclose(4/((a_+b_*n)**2+(a_+b_*(n+1))**2), 2/b_**2/((n+d+.5)**2+.25)) and np.isclose(4/((a_+b_*n)**2+(a_+b_*(n+1))**2), 1/18/((n+1)**2+.25)) for n in range(50)); ok('18.2, 18.3 cusp conductance', ok18)
c=2/b_; k=1/c; r=lambda n: c/(n+d); ok('19.1, 19.2 Mobius recurrence and g(r)', all(np.isclose(r(n+1), r(n)/(1+k*r(n))) and np.isclose(4/((a_+b_*n)**2+(a_+b_*(n+1))**2), r(n)**2/(k*k*r(n)**2+2*k*r(n)+2)) for n in range(50)))
rr=lambda n: 2/(3*(2*n+1)); ok('22.2 r_{T_m n} = r_n/m', all(np.isclose(rr((m*(2*n+1)-1)//2), rr(n)/m) for m in (1,3,5,7) for n in range(30)))
# 21.4 log divergence at Re s = 1/2: D_s(N) / log N -> 6|s|^2
s=0.5+2j; gg=lambda n: 4/((3+6*n)**2+(9+6*n)**2); D=lambda N: sum(abs(rr(n+1)**s-rr(n)**s)**2/gg(n) for n in range(N))
slope=(D(200000)-D(20000))/np.log(10); ok('21.5 slope 6|s|^2 = %.3f (measured %.3f)'%(6*abs(s)**2, slope), abs(slope-6*abs(s)**2)<0.05*6*abs(s)**2)
