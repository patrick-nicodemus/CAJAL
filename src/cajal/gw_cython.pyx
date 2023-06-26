# cython: profile=True
# distutils: language=c++
# distutils: sources = src/cajal/EMD_wrapper.cpp
"""
GW
"""

cimport cython
import numpy as np
cimport numpy as np
import scipy
import warnings
np.import_array()
from libc.stdlib cimport rand
from libc.stdint cimport uint64_t
# from ot.lp import emd_c, emd
from math import sqrt
from scipy.sparse import lil_matrix
from scipy import sparse

cdef extern from "EMD.h":
    int EMD_wrap(int n1, int n2, double *X, double *Y, double *D, double *G, double* alpha, double* beta, double *cost, uint64_t maxIter) nogil
    cdef enum ProblemType: INFEASIBLE, OPTIMAL, UNBOUNDED, MAX_ITER_REACHED
# cdef extern from "EMD.h":
#     int EMD_wrap(int n1,int n2, double *X, double *Y,double *D, double *G, double* alpha, double* beta, double *cost, uint64_t maxIter) nogil
#     int EMD_wrap_omp(int n1,int n2, double *X, double *Y,double *D, double *G, double* alpha, double* beta, double *cost, uint64_t maxIter, int numThreads) nogil
#     cdef enum ProblemType: INFEASIBLE, OPTIMAL, UNBOUNDED, MAX_ITER_REACHED


cdef extern from "stdlib.h":
    int RAND_MAX

DTYPE=np.float64
ctypedef np.float_t DTYPE_t


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def matrix_tensor(
        np.ndarray[DTYPE_t,ndim=2] c_C_Cbar,
        np.ndarray[DTYPE_t,ndim=2] C,
        np.ndarray[DTYPE_t,ndim=2] Cbar,
        np.ndarray[DTYPE_t,ndim=2] T,
        np.ndarray[DTYPE_t,ndim=2] LCCbar_otimes_T):

    np.matmul(C,T,out=LCCbar_otimes_T)
    # Cbar should be equal to Cbar.T so the transpose here is unnecessary.
    # assert np.all(Cbar == Cbar.T)
    np.matmul(LCCbar_otimes_T,Cbar,out=LCCbar_otimes_T)
    np.multiply(LCCbar_otimes_T,2.,out=LCCbar_otimes_T)
    np.subtract(c_C_Cbar,LCCbar_otimes_T,out=LCCbar_otimes_T)

def frobenius(DTYPE_t[:,:] A, DTYPE_t[:,:] B) -> DTYPE_t:

    cdef int n = A.shape[0]
    cdef int m = A.shape[1]
    assert n==B.shape[0]
    assert m==B.shape[1]
    cdef DTYPE_t sumval = 0.0
    cdef int i, j
    
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            sumval+=A[i,j]*B[i,j]
    return sumval

def gromov_linesearch(
        np.ndarray[np.float64_t,ndim=2] c_C_Cbar,
        np.ndarray[np.float64_t,ndim=2] C,
        np.ndarray[np.float64_t,ndim=2] Cbar,
        int C_length,
        int Cbar_length,
        np.ndarray[np.float64_t,ndim=2] T,
        np.ndarray[np.float64_t,ndim=2] deltaT,
        DTYPE_t cost_T
):
    # GW loss is
    # (-2 * < C * (\Delta T) * Cbar.T, \Delta T>_F)  * t^2 +
    # (<c_C_Cbar, \Delta T>_F  - 2*( <C * T * Cbar.T, \Delta T>_F + <C*(\Delta T)*Cbar.T,T>_F)) * t +
    # cost_T
    cdef np.ndarray[np.float64_t,ndim=2] C_deltaT_Cbar_T = np.matmul(C,deltaT)
    np.matmul(C_deltaT_Cbar_T,Cbar.T,out=C_deltaT_Cbar_T)
    # C_deltaT_Cbar_T =np.multiply(C_deltaT_Cbar_T, -2.)
    cdef DTYPE_t x
    cdef DTYPE_t y

    cdef DTYPE_t a=frobenius(C_deltaT_Cbar_T,deltaT)
    a *= -2.0                   # a is done
    cdef DTYPE_t b=frobenius(C_deltaT_Cbar_T,T)
    cdef np.ndarray[np.float64_t,ndim=2] C_T_Cbar_T = np.matmul(C,T)
    np.matmul(C_T_Cbar_T,Cbar.T,out=C_T_Cbar_T)
    b+=frobenius(C_T_Cbar_T,deltaT)
    b*= -2.0
    b+=frobenius(c_C_Cbar,deltaT) # b is done
 
    if a > 0:
        x = min(1.,max(0., -b/(2.0*a)))
    elif (a + b) < 0:
        x = 1.0
    else:
        x = 0.0
    y=(a * (x ** 2) + (b * x) + cost_T)
    return (x,y)

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def gw_cython(
        np.ndarray[np.float64_t,ndim=2] C,
        np.ndarray[np.float64_t,ndim=2] Cbar,
        np.ndarray[np.float64_t,ndim=1] p,
        np.ndarray[np.float64_t,ndim=1] q,
        # assumed to be np.multiply(C,C) * p (not matmul!)
        # We will adopt the convention that this will be input as a matrix of shape (n,1)
        np.ndarray[np.float64_t,ndim=2] c_C, 
        # assumed to be q^T * np.multiply(Cbar.T,Cbar.T) (not matmul!)
        # We will adopt the convention that this will be input as a matrix of shape (1,n)
        np.ndarray[np.float64_t,ndim=2] c_Cbar,
        # Probably have to manually broadcast last two arguments.
        max_iters_OT : int =100000,
        max_iters_descent : int =1000
):
    # L(C,\overline{C}) \otimes T = (C_sq * p * 1^T) + ( - 2 * (C * T * Cbar)
    # L(C,\overline{C}) \otimes T = c_C_Cbar - 2 * (C * T * Cbar.T)

    cdef np.ndarray[np.float64_t,ndim=2] c_C_Cbar = c_C+c_Cbar
    cdef np.ndarray[np.float64_t,ndim=2] T = np.matmul(
        p[:,np.newaxis],
        q[np.newaxis,:])
    cdef int C_length=C.shape[0]
    cdef int Cbar_length=Cbar.shape[0]
    cdef int it = 0
    cdef DTYPE_t alpha
    cdef DTYPE_t gw_loss_T
    cdef DTYPE_t new_gw_loss_T
    log={ 'loss' : [], "alphas" : [] }
    cdef np.ndarray[np.float64_t,ndim=2] T_new =np.empty((C_length,Cbar_length),dtype=np.float64)
    cdef np.ndarray[np.float64_t,ndim=2] deltaT = np.empty((C_length,Cbar_length),dtype=np.float64)
    cdef np.ndarray[np.float64_t,ndim=2] LCCbar_otimes_T = np.empty((C_length,Cbar_length),dtype=DTYPE)

    matrix_tensor(c_C_Cbar,C,Cbar,T,LCCbar_otimes_T)
    gw_loss_T=frobenius(LCCbar_otimes_T,T)
    log['loss'].append(gw_loss_T)
    log['sparse']=[]

    while it<max_iters_descent:
        # T_new, inner_log = emd(p,q,2*LCCbar_otimes_T,max_iters_OT,log=True)
        # It's tempting to use the 'cost' from this function but remember that
        # it's a "mixed cost" between two different transport plans, T_r and T_r+1.
        # It's not meaningful! Don't use it
        # T_new, _, _, _,_ = emd_c(p,q,2*LCCbar_otimes_T,max_iters_OT,numThreads=1)
        T_new=np.zeros((1,1),dtype=DTYPE)
        log['sparse'].append(np.count_nonzero(T_new))
        matrix_tensor(c_C_Cbar,C,Cbar,T_new,LCCbar_otimes_T)
        new_gw_loss_T =frobenius(LCCbar_otimes_T,T_new)
        if (new_gw_loss_T >= gw_loss_T):
            return (T, sqrt(gw_loss_T)/2,log)
        elif (new_gw_loss_T/gw_loss_T - 1.0 > -(1e-9)) or (new_gw_loss_T-gw_loss_T > -(1e-9)):
            gw_loss_T=new_gw_loss_T
            log['loss'].append(gw_loss_T)
            return (T_new, sqrt(gw_loss_T)/2,log)
        T=T_new
        gw_loss_T=new_gw_loss_T
        it +=1

    log['loss'].append(gw_loss_T)
    # assert np.allclose(np.sum(T,axis=0),p)
    # assert np.allclose(np.sum(T,axis=1),q)
    return (T, sqrt(gw_loss_T)/2,log)


def n_c_2(int n):
    return <int>((n * (n-1))/2)

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def vf_ij(
        # np.ndarray[np.float64_t,ndim=1,mode='c'] A,
        np.float64_t[::1] A,
        int n,
        int i,
        int j):

    if i == j:
        return 0.0
    if i < j:
        return A[ (n_c_2(n)-n_c_2(n-i))+((j-i)-1)]
    return A[(n_c_2(n)-n_c_2(n-j))+((i-j)-1)]

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def vf_dot(
        DTYPE_t[::1] A,
        int n,
        DTYPE_t[:] B,
        DTYPE_t[:] C
):

    assert B.shape[0]==n
    cdef int k
    for k in range(n):
        C[k]=0.0
        for i in range(n):
            C[k]+= vf_ij(A,n,k,i)*B[i]

cpdef gw_cython_core(
        np.ndarray[DTYPE_t,ndim=2,mode='c'] A,
        np.ndarray[DTYPE_t,ndim=1,mode='c'] a,
        np.ndarray[DTYPE_t,ndim=1,mode='c'] Aa,
        DTYPE_t c_A,        
        np.ndarray[DTYPE_t,ndim=2,mode='c'] B,
        np.ndarray[DTYPE_t,ndim=1,mode='c'] b,
        np.ndarray[DTYPE_t,ndim=1,mode='c'] Bb,
        DTYPE_t c_B,
        int max_iters_descent =1000,
        uint64_t max_iters_ot = 200000,
):

    cdef int it = 0
    cdef int n = a.shape[0]
    cdef int m = b.shape[0]
    cdef int result_code
    # cdef DTYPE_t alpha
    # cdef DTYPE_t gw_loss_T
    # cdef DTYPE_t new_gw_loss_T
    cdef DTYPE_t cost=0.0
    cdef double temp=0.0        # I believe this number is not useful. I could be wrong.
    cdef DTYPE_t newcost=0.0
    # np.ndarray[np.float64_t,ndim=1] Aa = np.dot(A,a)
    cdef np.ndarray[double, ndim=1, mode="c"] alpha=np.zeros(n)
    cdef np.ndarray[double, ndim=1, mode="c"] beta=np.zeros(m)
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] neg2_PB
    # cdef np.ndarray[double, ndim=2, mode="fortran"] AP
    cdef np.ndarray[double, ndim=2, mode="c"] AP=np.zeros((n,m),dtype=DTYPE,order='C')
    # cdef np.ndarray[double, ndim=2, mode="c"] PB=np.zeros((n,m),dtype=DTYPE,order='C')

    # np.ndarray[np.float64_t,ndim=1] Bb = np.dot(B,b)

    # Cost matrix, C= initialized to -2*APB
    cdef np.ndarray[np.float64_t,ndim=2,mode='c'] C = np.multiply(Aa[:,np.newaxis],(-2.0*Bb)[np.newaxis,:],order='C')
    cdef np.ndarray[np.float64_t,ndim=2,mode='c'] P = np.zeros((n,m),dtype=DTYPE,order='C')
    cost=c_A+c_B
    cost+=frobenius(C,P)

    while it<max_iters_descent:
        result_code=EMD_wrap(n,m, <double*> a.data, <double*> b.data,
                             <double*> C.data, <double*>P.data,
                             <double*> alpha.data, <double*> beta.data,
                             <double*> &temp, max_iters_ot)

        if result_code != OPTIMAL:
            # cdef enum ProblemType: INFEASIBLE, OPTIMAL, UNBOUNDED, MAX_ITER_REACHED
            if result_code == INFEASIBLE:
                raise Exception("INFEASIBLE")
            if result_code == UNBOUNDED:
                raise Exception("UNBOUNDED")
            if result_code == MAX_ITER_REACHED:
                raise Warning("MAX_ITER_REACHED")
            
        # P_sparse = scipy.sparse.csc_matrix(P,shape=(n,m), dtype=DTYPE)
        # AP = sparse.csc_matrix.dot(A,P_sparse)
        np.dot(A,P,out=AP)
        np.multiply(AP,-2.0,out=AP)
        np.matmul(AP,B,out=C)
        # neg2_PB = (-2.0*P_sparse).dot(B)
        # newcost = (c_A+c_B)+frobenius(AP,neg2_PB)
        newcost=c_A+c_B
        newcost+=frobenius(C,P)
        if newcost >= cost:
            return (P,sqrt(cost)/2.0)
        cost=newcost 
        # np.dot(A,neg2_PB,out=C)
        it+=1

def gw_pairwise(
        list cell_dms
):

    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef Py_ssize_t k = 0
    cdef int N = len(cell_dms)
    
    # cdef list[double] gw_dists= ((N * (N-1))/2)*[0.0]
    cdef np.ndarray[DTYPE_t,ndim=1,mode='c'] gw_dists = np.zeros( (((N * (N-1))/2),),dtype=DTYPE)
    cdef double gw_dist

    cdef np.ndarray[DTYPE_t,ndim=2,mode='c'] A, B
    cdef np.ndarray[DTYPE_t,ndim=1,mode='c'] a, b
    cdef np.ndarray[DTYPE_t,ndim=1,mode='c'] Aa, Bb
    cdef DTYPE_t c_A, c_B

    for i in range(N):
        A, a, Aa, c_A = cell_dms[i]
        for j in range(i+1,N):
            B, b, Bb, c_B = cell_dms[j]
            _,gw_dist=gw_cython_core(A,a,Aa,c_A,B,b,Bb,c_B)
            gw_dists[k]=gw_dist
            del(B)
            del(b)
            del(Bb)
            del(c_B)
            k+=1
    return gw_dists


def intersection(DTYPE_t a, DTYPE_t b, DTYPE_t c, DTYPE_t d) -> DTYPE_t:
    cdef DTYPE_t maxac= a if a >= c else c
    cdef DTYPE_t minbd= b if b <= d else d
    minbd=minbd-maxac
    minbd = minbd if minbd >= <DTYPE_t>0.0 else <DTYPE_t>0.0
    return minbd

def oneD_ot_CHECK(
        DTYPE_t[:,:] T):

    cdef DTYPE_t mysum=0.0
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            mysum+=T[i,j]
    return mysum

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def oneD_ot_gw(
        DTYPE_t[::1] a,
        int a_len,
        DTYPE_t[::1] b,
        int b_len,
        DTYPE_t[:,:] T,
        DTYPE_t scaling_factor
):

    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef DTYPE_t cum_a_prob=0.0
    cdef DTYPE_t cum_b_prob=0.0

    # assert A.shape[0]==a_len
    # assert B.shape[0]==b_len
    # assert a.shape[0]==a_len
    # assert b.shape[0]==b_len
    # assert T.shape[0]==a_len
    # assert T.shape[1]==b_len
    # assert( abs(np.sum(a)-1.0)<1.0e-7 )
    # assert( abs(np.sum(b)-1.0)<1.0e-7 )
    while i+j < a_len+b_len-1:
        # Loop invariant:
        # [cum_a_prob,cum_a_prob+a[i]) intersects [cum_b_prob,cum_b_prob+b[j])
        # nontrivially.
        # assert i<a_len
        # assert j<b_len
        # assert cum_a_prob+a[i]>cum_b_prob and cum_b_prob+b[j]>cum_a_prob
        T[i,j]=intersection(cum_a_prob,
                            cum_a_prob+a[i],
                            cum_b_prob,
                            cum_b_prob+b[j])*scaling_factor
        if cum_a_prob+a[i]<cum_b_prob+b[j]:
            if i==a_len-1:
                # assert j==b_len-1
                break
            else:
                cum_a_prob+=a[i]
                i+=1
        elif cum_a_prob+a[i]>cum_b_prob+b[j]:
            if j==b_len-1:
                # assert i==a_len-1
                break
            else:
                cum_b_prob+=b[j]
                j+=1
        else:
            if i==a_len-1:
                # assert j==b_len-1
                break
            else:
                cum_a_prob+=a[i]
                i+=1
                cum_b_prob+=b[j]
                j+=1

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef sparse_oneD_OT_gw(
    int[::1] T_rows,
    int[::1] T_cols,
    DTYPE_t[::1] T_vals,
    int T_offset,
    int a_offset,
    int b_offset,
    DTYPE_t[::1] a, # 1dim
    int a_len, #int
    DTYPE_t[::1] b,#1dim
    int b_len, #int
    DTYPE_t scaling_factor #float
):
    # a, b are required to be probability distributions
    # The sparse matrix returned by this function may have triples of the form (0,0,0.0).
    # Code handling this should be aware of this.

    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef DTYPE_t cum_a_prob=0.0
    cdef DTYPE_t cum_b_prob=0.0
    cdef int index

    # assert A.shape[0]==a_len
    # assert B.shape[0]==b_len
    # assert a.shape[0]==a_len
    # assert b.shape[0]==b_len
    # assert T.shape[0]==a_len
    # assert T.shape[1]==b_len
    # assert( abs(np.sum(a)-1.0)<1.0e-7 )
    # assert( abs(np.sum(b)-1.0)<1.0e-7 )
    while i+j < a_len+b_len-1:
        # print("inner i:" + str(i))
        # print("inner j:" + str(j))
        # Loop invariant:  [cum_a_prob,cum_a_prob+a[i]) intersects [cum_b_prob,cum_b_prob+b[j])
        # nontrivially.
        # assert i<a_len
        # assert j<b_len
        # assert cum_a_prob+a[i]>cum_b_prob and cum_b_prob+b[j]>cum_a_prob
        index=T_offset+i+j
        T_rows[index]= a_offset + i
        T_cols[index ]= b_offset + j
        assert T_vals[index]==0.0
        T_vals[index]=\
            intersection(cum_a_prob,cum_a_prob+a[i],cum_b_prob,cum_b_prob+b[j])*scaling_factor
        if cum_a_prob+a[i]<cum_b_prob+b[j]:
            if i==a_len-1:
                # assert j==b_len-1
                break
            else:
                cum_a_prob+=a[i]
                i+=1
        elif cum_a_prob+a[i]>cum_b_prob+b[j]:
            if j==b_len-1:
                # assert i==a_len-1
                break
            else:
                cum_b_prob+=b[j]
                j+=1
        else:
            if i==a_len-1:
                # assert j==b_len-1
                break
            else:
                cum_a_prob+=a[i]
                i+=1
                cum_b_prob+=b[j]
                j+=1

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def quantized_gw(
        # A is an n x n distance matrix
        # np.ndarray[np.float64_t,ndim=2] A,
        # a is the probability distribution on points of A
        np.ndarray[np.float64_t,ndim=1] a,
        # A_s=A_sample is a sub_matrix of A, of size ns x ns
        np.ndarray[np.float64_t,ndim=2] A_s,
        # A_si = A_sample_indices
        # Indices for sampled points of A, of length ns.
        # Should satisfy A_s[x,y]=A[A_si[x],A_si[y]] for all x,y < ns
        np.ndarray[Py_ssize_t,ndim=1] A_si,
        # Probability distribution on sample points of A_s; of length ns
        np.ndarray[np.float64_t,ndim=1] a_s,
        # np.dot(np.multiply(A_s,A_s),a_s)
        np.ndarray[np.float64_t,ndim=1] As_As_as,
        # B is an mxm distance matrix
        # np.ndarray[np.float64_t,ndim=2] B,
        # b is the probability distribution on points of B
        np.ndarray[np.float64_t,ndim=1] b,
        # B_sample, size ms x ms
        np.ndarray[np.float64_t,ndim=2] B_s,
        # B_sample_indices, size ms
        np.ndarray[Py_ssize_t,ndim=1] B_si,
        # Probability distribution on sample points of B_s; of length ms
        np.ndarray[np.float64_t,ndim=1] b_s,
        # np.dot(np.multiply(B_s,B_s),b_s)
        np.ndarray[np.float64_t,ndim=1] Bs_Bs_bs,
):

    # Assumptions: The points of A are arranged in such a way that:
    # for all k, i,  A_si[k] <= i < A_si[k+1],
    # the point i of A belongs to the Voronoi cell determined by A_si[k];
    # moreover, within the region A_si[k] <= i < A_si[k+1], the points
    # are in sorted order, i..e, for A_si[k] <= i < j < A_si[k+1],
    # we have A[A_si[k],i]<=A[A_si[k],j]
    # And B should also satisfy these assumptions.
    cdef int n = a.shape[0]
    cdef int ns = A_s.shape[0]
    cdef int m = b.shape[0]
    cdef int ms = B_s.shape[0]
    cdef DTYPE_t gw_cost=0.0
    cdef DTYPE_t local_gw_cost=0.0
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef np.ndarray[np.float64_t,ndim=1] a_local
    cdef np.ndarray[np.float64_t,ndim=1] b_local
    cdef int a_local_len
    cdef int b_local_len
    cdef np.ndarray[np.float64_t,ndim=2] quantized_coupling # size ns x ms
    cdef np.ndarray[np.float64_t,ndim=2] T = np.zeros((n,m),dtype=DTYPE) # size n x m - the
    cdef DTYPE_t[:,:] T_local
    quantized_coupling, _,_ =gw_cython(A_s,B_s,a_s,b_s,As_As_as[:,np.newaxis],Bs_Bs_bs[np.newaxis,:])

    for i in range(ns):
        if (i+1<ns):
            a_local=a[A_si[i]:A_si[i+1]]/a_s[i]
            # assert( abs(np.sum(a_local)-1.0)<1.0e-7 )
            a_local_len=A_si[i+1]-A_si[i]
        else:
            # assert(i+1==ns)
            a_local=a[A_si[i]:]/a_s[i]
            # assert( abs(np.sum(a_local)-1.0)<1.0e-6 )
            a_local_len=n-A_si[i]
        for j in range(ms):
            if quantized_coupling[i,j] != 0.0:
                if (j+1<ms):
                    if(i+1<ns):
                        T_local= T[A_si[i]:A_si[i+1],:][:,B_si[j]:B_si[j+1]]
                    else:
                        # assert (i == ns-1)
                        T_local= T[A_si[i]:,:][:,B_si[j]:B_si[j+1]]
                    b_local=b[B_si[j]:B_si[j+1]]/b_s[j]
                    # assert( abs(np.sum(b_local)-1.0)<1.0e-7 )
                    b_local_len=B_si[j+1]-B_si[j]
                else:
                    # assert(j+1==ms)
                    if(i+1<ns):
                        T_local= T[A_si[i]:A_si[i+1],:][:,B_si[j]:]
                    else:
                        # assert (i == ns-1)
                        T_local= T[A_si[i]:,:][:,B_si[j]:]
                    b_local=b[B_si[j]:]/b_s[j]
                    # assert( abs(np.sum(b_local)-1.0)<1.0e-7 )
                    b_local_len=m-B_si[j]
                oneD_ot_gw(a_local, # 1dim
                           a_local_len, #int
                           b_local,#1dim
                           b_local_len, #int
                           T_local,# rectangle
                           quantized_coupling[i,j]) #float
    return T

# Turning off bounds checking doesn't improve performance on my end.
# Neither does turning 
def quantized_gw_2(
        # a is the probability distribution on points of A
        np.ndarray[np.float64_t,ndim=1] a,
        # A_s=A_sample is a sub_matrix of A, of size ns x ns
        np.ndarray[np.float64_t,ndim=2] A_s,
        # A_si = A_sample_indices
        # Indices for sampled points of A, of length ns+1
        # Should satisfy A_s[x,y]=A[A_si[x],A_si[y]] for all x,y < ns
        # should satisfy A_si[ns]=n
        np.ndarray[Py_ssize_t,ndim=1] A_si,
        # Probability distribution on sample points of A_s; of length ns
        np.ndarray[np.float64_t,ndim=1] a_s,
        np.ndarray[np.float64_t,ndim=1] A_s_a_s,
        DTYPE_t c_As,
        # b is the probability distribution on points of B
        np.ndarray[np.float64_t,ndim=1] b,
        # B_sample, size ms x ms
        np.ndarray[np.float64_t,ndim=2] B_s,
        # B_sample_indices, size ms+1
        np.ndarray[Py_ssize_t,ndim=1] B_si,
        # Probability distribution on sample points of B_s; of length ms
        np.ndarray[np.float64_t,ndim=1] b_s,
        # np.dot(np.multiply(B_s,B_s),b_s)
        np.ndarray[np.float64_t,ndim=1] B_s_b_s,
        DTYPE_t c_Bs,
):

    cdef int n = a.shape[0]
    cdef int ns = A_s.shape[0]
    cdef int m = b.shape[0]
    cdef int ms = B_s.shape[0]
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef int a_local_len
    cdef int b_local_len
    cdef np.ndarray[np.float64_t,ndim=2] quantized_coupling # size ns x ms

    quantized_coupling, _=gw_cython_core(
        A_s,a_s,A_s_a_s,c_As,
        B_s,b_s,B_s_b_s,c_Bs)

    # We can count, roughly, how many elements we'll need in the coupling matrix.
    cdef int num_elts =0
    for i in range(ns):
        for j in range(ms):
            if quantized_coupling[i,j]!=0.0:
                num_elts += (A_si[i+1]-A_si[i]) + (B_si[j+1]-B_si[j]) - 1

    cdef np.ndarray[int ,ndim=1,mode="c"] T_rows = np.zeros((num_elts,),dtype=np.int32)
    cdef np.ndarray[int ,ndim=1,mode="c"] T_cols = np.zeros((num_elts,),dtype=np.int32)
    cdef np.ndarray[DTYPE_t ,ndim=1,mode="c"] T_vals = np.zeros((num_elts,),dtype=DTYPE)
    cdef int k = 0
    for i in range(ns):
        a_local=a[A_si[i]:A_si[i+1]]/a_s[i]
        # assert( abs(np.sum(a_local)-1.0)<1.0e-7 )
        a_local_len=A_si[i+1]-A_si[i]
        for j in range(ms):
            if quantized_coupling[i,j] != 0.0:
                b_local=b[B_si[j]:B_si[j+1]]/b_s[j]
                # assert( abs(np.sum(b_local)-1.0)<1.0e-7 )
                b_local_len=B_si[j+1]-B_si[j]
                # print("i:" + str(i))
                # print("j:" + str(j))
                # print("k:" + str(k))
                # print("num_elts:"+str(num_elts))
                # print("A_si[i]:" + str(A_si[i]))
                # print("B_si[j]:" + str(B_si[j]))                
                sparse_oneD_OT_gw(
                    T_rows,
                    T_cols,
                    T_vals,
                    k,
                    A_si[i],
                    B_si[j],
                    a_local, # 1dim
                    a_local_len, #int
                    b_local,#1dim
                    b_local_len, #int
                    quantized_coupling[i,j])#float
                k+= (A_si[i+1]-A_si[i])+(B_si[j+1]-B_si[j])-1
    return (T_rows,T_cols,T_vals)

