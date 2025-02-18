.. _python_upf_examples:


UPF in PyMAPDL
^^^^^^^^^^^^^^

The following Python UPF examples are available:

* `Python UserMat subroutine`_
* `Python UsrShift subroutine`_
* `Python UserHyper subroutine`_


Python ``UserMat`` subroutine
*****************************

This example simulates a block modeled with 3D elements. The
user material in the ``usermat.py`` file is equivalent to linear elastic.
The block is under uniaxial compression. The final deformation is compared
with the theoretical result.


Input data
++++++++++

.. code:: apdl

    /batch,list
    /title,upf-py1s, 'test usermat.py with 3D elements'

    /prep7
    /upf,'usermat.py'
    tb,user,1,,2
    tbdata,1,1e5, 0.3    ! E, Poisson

    et,1,185

    block,0,1,0,1,0,1
    esize,1
    mshape,0,3D
    vmesh,all
    elist

    nsel,s,loc,x,0
    d,all,ux

    nsel,s,loc,y,0
    d,all,uy

    nsel,s,loc,z,0
    d,all,uz,

    allsel,all
    finish

    /solu

    time,1
    deltime,0.1
    eresx,no
    nsel,s,loc,x,1
    !d,all,ux,-0.01
    sf,all,pres,1000        ! pressure on x-axis
    allsel,all

    outres,all,all

    solve			       			 

    finish
    /POST1
    set,last
    esel,s,elem,,1
    /output
    presol,s
    presol,epel
    /com, expected results: Sx=-1000, epel_x=-1e-2
    finish
    /exit,nosave



``usermat.py`` file
+++++++++++++++++++


.. code:: python

    import grpc
    import sys
    import math
    import numpy as np
    from mapdl import *


    class MapdlUserService(MapdlUser_pb2_grpc.MapdlUserServiceServicer):
        #   #################################################################
        def UserMat(self, request, context):
            ncomp = request.ncomp
            nDirect = request.nDirect

            response = MapdlUser_pb2.UserMatResponse()

            response.stress[:] = request.stress[:]
            response.ustatev[:] = request.ustatev[:]
            response.sedEl = request.sedEl
            response.sedPl = request.sedPl
            response.epseq = request.epseq
            response.epsPl[:] = request.epsPl[:]
            response.var0 = request.var0
            response.var3 = request.var3
            response.var4 = request.var4
            response.var5 = request.var5
            response.var6 = request.var6
            response.var7 = request.var7

            if ncomp > 4:  # ***    3d, plane strain and axisymmetric example
                usermat3d(request, context, response)
            elif nDirect == 2 and ncomp == 3:  # ***    plane stress example
                usermatps(request, context, response)
            elif ncomp == 3:  # ***    3d beam example
                usermatbm(request, context, response)
            elif ncomp == 1:  # ***    1d beam example
                usermat1d(request, context, response)

            return response


    def usermat3d(request, context, response):
        ZERO = 0.0
        HALF = 0.5
        THIRD = 1.0 / 3.0
        ONE = 1.0
        TWO = 2.0
        SMALL = 1.0e-08
        sqTiny = 1.0e-20
        ONEDM02 = 1.0e-02
        ONEDM05 = 1.0e-05
        ONEHALF = 1.5
        TWOTHIRD = 2.0 / 3.0
        mcomp = 6

        G = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]

        db.start()  # Connect to the MAPDL DB gRPC Server
        ncomp = request.ncomp

        # *** get Young's modulus and Poisson's ratio
        young = request.prop[0]
        posn = request.prop[1]
        twoG = young / (ONE + posn)
        elast1 = young * posn / ((1.0 + posn) * (1.0 - TWO * posn))
        elast2 = HALF * twoG

        #
        # *** calculate elastic stiffness matrix (3d)
        #
        dsdeEl = np.zeros((6, 6))

        dsdeEl[0, 0] = (elast1 + TWO * elast2) * G[0] * G[0]
        dsdeEl[0, 1] = elast1 * G[0] * G[1] + elast2 * TWO * G[3] * G[3]
        dsdeEl[0, 2] = elast1 * G[0] * G[2] + elast2 * TWO * G[4] * G[4]
        dsdeEl[0, 3] = elast1 * G[0] * G[3] + elast2 * TWO * G[0] * G[3]
        dsdeEl[0, 4] = elast1 * G[0] * G[4] + elast2 * TWO * G[0] * G[4]
        dsdeEl[0, 5] = elast1 * G[0] * G[5] + elast2 * TWO * G[3] * G[4]

        dsdeEl[1, 1] = (elast1 + TWO * elast2) * G[1] * G[1]
        dsdeEl[1, 2] = elast1 * G[1] * G[2] + elast2 * TWO * G[5] * G[5]
        dsdeEl[1, 3] = elast1 * G[1] * G[3] + elast2 * TWO * G[0] * G[3]
        dsdeEl[1, 4] = elast1 * G[1] * G[4] + elast2 * TWO * G[0] * G[4]
        dsdeEl[1, 5] = elast1 * G[1] * G[5] + elast2 * TWO * G[1] * G[5]

        dsdeEl[2, 2] = (elast1 + TWO * elast2) * G[2] * G[2]
        dsdeEl[2, 3] = elast1 * G[2] * G[3] + elast2 * TWO * G[4] * G[5]
        dsdeEl[2, 4] = elast1 * G[2] * G[4] + elast2 * TWO * G[4] * G[2]
        dsdeEl[2, 5] = elast1 * G[2] * G[5] + elast2 * TWO * G[5] * G[2]

        dsdeEl[3, 3] = elast1 * G[3] * G[3] + elast2 * (G[0] * G[1] + G[3] * G[3])
        dsdeEl[3, 4] = elast1 * G[3] * G[4] + elast2 * (G[0] * G[5] + G[4] * G[3])
        dsdeEl[3, 5] = elast1 * G[3] * G[5] + elast2 * (G[3] * G[5] + G[4] * G[1])

        dsdeEl[4, 4] = elast1 * G[4] * G[4] + elast2 * (G[0] * G[2] + G[4] * G[4])
        dsdeEl[4, 5] = elast1 * G[4] * G[5] + elast2 * (G[3] * G[2] + G[4] * G[5])

        dsdeEl[5, 5] = elast1 * G[5] * G[5] + elast2 * (G[1] * G[2] + G[5] * G[5])

        for i in range(0, 5):
            for j in range(i + 1, 6):
                dsdeEl[j, i] = dsdeEl[i, j]

        Strain = np.zeros(ncomp)
        Strain[0:ncomp] = request.Strain[0:ncomp]
        dStrain = np.zeros(ncomp)
        dStrain[0:ncomp] = request.dStrain[0:ncomp]

        #
        # *** calculate the stress and
        #     copy elastic moduli dsdeEl to material Jacobian matrix

        strainEl = np.copy(Strain)  # strainEl = Strain
        strainEl = np.add(strainEl, dStrain)  # strainEl += dStrain

        dsdePl = np.copy(dsdeEl)
        sigElp = np.zeros(ncomp)
        sigElp = dsdeEl.dot(strainEl)

        response.stress[:] = sigElp
        dsdePl.shape = 6 * 6
        response.dsdePl[:] = dsdePl

        return response


    if __name__ == "__main__":
        upf.launch(sys.argv[0])



Python ``UsrShift`` subroutine
******************************

This example describes a block of Prony viscoplastic material with a user-defined
shift function following a Tool-Narayanaswamy shift function. Uniaxial tension is
applied on one end and held for 15 seconds with a constant 280 K uniform
temperature. The final stress is obtained to verify stress relaxation.



Input data
++++++++++


.. code:: apdl

    /batch,list
    /title,upf-py10s, 'test usrshift.py'

    /prep7 
    /upf,'usrshift.py'

    n1=60 
    n2=n1*10 
    n3=n1 
    dy = 0.0045 
    fact=2 
    t1end=30.0/fact 
    alpha = 0.5 
    tau = 2.0 
    a1 = alpha          ! participating factor for el182, 183 
    t1 = tau 
    c1 = a1/a1          ! participating factor for el88 

    tr = 0 
    theta = 280 
    toffst,273 
    tunif, theta 
    tref,0 
    b1 = log(fact)*(273+tr)*(273+theta)/(theta-tr) 
    b2 = 1 
    b11=b1/273/273 

    young = 20e5 
    poiss = 0.3 
    G0 = young/2/(1+poiss) 
    K0 = young/3/(1-2*poiss) 

    ! material 1                ! rate-dependent vpl
    mp,ex,1,young 
    mp,nuxy,1,0.3 
    tb,prony,1,,1,shear         ! define viscousity parameters 
    tbdata,1,a1,t1 
    tb,prony,1,,1,bulk          ! define viscousity parameters 
    tbdata,1,a1,t1 
    tb,shift,1,,2,100           ! Tool-Narayanaswamy shift function 
    tbdata,1,tr,b11, 

    ! FE model and mesh 

    et,1,186 
    mat,1 
    block,0,1,0,1,0,1 
    esize,1 
    vmesh,1 

    nall 
    nsel,s,loc,x 
    d,all,ux 
    nall 
    nsel,s,loc,y 
    d,all,uy 
    nall 
    nsel,s,loc,z 
    d,all,uz 

    /solu 
    nlgeom,on 
    cnvtol,u,,1.0e-8 
    cnvtol,f,,1.0e-6 
    nsel,s,loc,y,1.000 
    d,all,uy,dy 
    nall 
    time,1.0e-8 
    nsubst,1,1,1 
    outres,all,-10 
    solve

    nsel,s,loc,y,1.000 
    time,t1end 
    d,all,uy,dy 
    nall 
    nsubst,n1,n2,n3 
    outres,all,-10 
    outpr,all,last 
    solve

    finish 

    /post1 
    set,last 
    /output
    presol,s 

    /com, expected results   Sy=4490.0 

    finish 
    /exit,nosave


``usrshift.py`` file
++++++++++++++++++++


.. code:: python

    import grpc
    import sys
    import math
    from mapdl import *


    class MapdlUserService(MapdlUser_pb2_grpc.MapdlUserServiceServicer):
        #   #################################################################

        def UsrShift(self, request, context):
            response = MapdlUser_pb2.UsrShiftResponse()
            one = 1.0
            half = 0.5
            quart = 0.25

            tref = request.propsh[0]
            temp = request.temp
            timinc = request.timinc
            dtemp = request.dtemp
            nTerms = request.nTerms

            thalf = temp - dtemp * half - tref
            t3quart = temp - dtemp * quart - tref

            c1 = 0.0
            c2 = 0.0

            for i in range(nTerms - 1):
                c1 = c1 + request.propsh[i + 1] * thalf ** (i + 1)
                c2 = c2 + request.propsh[i + 1] * t3quart ** (i + 1)

            dxi = math.exp(c1) * timinc
            dxihalf = math.exp(c2) * timinc * half

            response.dxi = dxi
            response.dxihalf = dxihalf

            return response


    if __name__ == "__main__":
        upf.launch(sys.argv[0])



Python ``UserHyper`` subroutine
*******************************

This example models a block under simple uniaxial tension. The block is made of a
user-defined hyper material that is identical to Arruda-Boyce hyperelasticity. Large
deformation effects are included. The final stress is printed for comparison against
the reference.


Input data
++++++++++

.. code:: apdl

    /BATCH,LIST 
    /title, upf-py16s, 'test UserHyper.py with MAPDL'
    /com, displacement-controlled uniaxial tension test for Boyce material model  

    /prep7 

    /upf,'userhyper.py'
    tb,hyper,1,,,user 
    tbdata,1,2/100,0.2,2.8284 

    et,1,185 

    block,0,1,0,1,0,1 
    esize,1 
    vmesh,1 

    nsel,s,loc,x 
    d,all,ux 
    nsel,s,loc,y 
    d,all,uy 
    nsel,s,loc,z 
    d,all,uz 
    nall 

    nsel,s,loc,x,1.0 
    d,all,ux,0.3 

    nall 

    /solu 

    nlgeom,on 
    time,1 
    nsubst,5,20,5 

    /out,scratch 
    solve 

    /post1 
    /output

    set,1,last 
    presol,s,x 

    /com, 'expected results from equivalent userhyper.F'
    /com,    NODE     SX           SY           SZ           SXY          SYZ 
    /com,       2  0.20118      0.32054E-003 0.32054E-003 0.13752E-015 0.67903E-017 
    /com,       4  0.20118      0.32054E-003 0.32054E-003 0.13776E-015 0.40293E-017 
    /com,       3  0.20118      0.32054E-003 0.32054E-003 0.50933E-015-0.10653E-014 
    /com,       1  0.20118      0.32054E-003 0.32054E-003 0.50909E-015-0.54682E-015 
    /com,       5  0.20118      0.32054E-003 0.32054E-003-0.15222E-015 0.58245E-015 
    /com,       6  0.20118      0.32054E-003 0.32054E-003-0.15313E-015 0.10856E-014 
    /com,       7  0.20118      0.32054E-003 0.32054E-003-0.55356E-015 0.17421E-016 
    /com,       8  0.20118      0.32054E-003 0.32054E-003-0.55265E-015 0.28848E-016 

    finish 
    /exit,nosave 



``userhyper.py`` file
+++++++++++++++++++++


.. code:: python

    import grpc
    import sys
    from mapdl import *
    import math
    import numpy as np

    firstcall = 1


    class MapdlUserService(MapdlUser_pb2_grpc.MapdlUserServiceServicer):
        #   #################################################################
        def UserHyper(self, request, context):
            global firstcall
            if firstcall == 1:
                print(">> Using Python UserHyper function\n")
                firstcall = 0

            prophy = np.copy(request.prophy)
            invar = np.copy(request.invar)

            response = MapdlUser_pb2.UserHyperResponse()

            ZERO = 0.0
            ONE = 1.0
            HALF = 0.5
            TWO = 2.0
            THREE = 3.0
            TOLER = 1.0e-12

            ci = (
                0.5,
                0.05,
                0.104761904761905e-01,
                0.271428571428571e-02,
                0.770315398886827e-03,
            )

            i1 = invar[0]
            jj = invar[2]
            mu = prophy[1]
            lm = prophy[2]
            oD1 = prophy[0]
            i1i = ONE
            im1 = ONE / i1
            t3i = ONE
            potential = ZERO
            pInvDer = np.zeros(9)

            for i in range(5):
                ia = i + 1
                t3i = t3i * THREE
                i1i = i1i * i1
                i1i1 = i1i * im1
                i1i2 = i1i1 * im1
                lm2 = ci[i] / (lm ** (TWO * (ia - ONE)))
                potential = potential + lm2 * (i1i - t3i)
                pInvDer[0] = pInvDer[0] + lm2 * ia * i1i1
                pInvDer[2] = pInvDer[2] + lm2 * ia * (ia - ONE) * i1i2

            potential = potential * mu
            pInvDer[0] = pInvDer[0] * mu
            pInvDer[2] = pInvDer[2] * mu

            j1 = ONE / jj
            pInvDer[7] = ZERO
            pInvDer[8] = ZERO

            if oD1 > TOLER:
                oD1 = ONE / oD1
                incomp = False
                potential = potential + oD1 * ((jj * jj - ONE) * HALF - math.log(jj))
                pInvDer[7] = oD1 * (jj - j1)
                pInvDer[8] = oD1 * (ONE + j1 * j1)

            response.potential = potential
            response.incomp = incomp
            response.pInvDer[:] = pInvDer[:]

            return response


    if __name__ == "__main__":
        upf.launch(sys.argv[0])

