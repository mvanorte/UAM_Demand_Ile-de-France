import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import TripDis
import TripGen2 as TripGen

# Constants and Parameters

    # General
th_acdis = 38.4     # Average crowfly distance [km]
th_ai = TripGen.df3["income"].mean()       # Average income [Eur]
# print(th_ai) # average income

    # Cost
b_c = -0.126        # Cost parameter
l_dis_c = -0.400    # Distance/cost parameter
l_inc_c = -0.15     # Income/cost parameter

    # Car
CarAv = TripGen.df3['car_availability'].to_numpy()
CarDict = {'none':0, 'some':1, 'all':2}
h=[]
for i in CarAv:
    h.append(CarDict[i])
h=np.array(h)

a_car = []
for i in h:
    if i == 0:
        a_car.append(0)
    elif i == 1:
        a_car.append(0.827)
    elif i == 2:
        a_car.append(2 * 0.827)
a_car=np.array(a_car) # Inherent utility
# a_car = 0.827 # Inherent utility (kept for 1st iteration)
b_car = -0.067      # Travel time parameter [min**-1]

    # Public Transport
a_pt = 0.000        # Inherent utility
b_trv_pt = -0.019   # Travel time parameter [min**-1]
b_wait_pt = -0.038  # Waiting time parameter [min**-1]
b_trs_pt = -0.170   # Transfers parameter
b_egs_pt = -0.08      # Egress parameter

    # UAM
a_uam = 0           # Inherent utility
b_trv_uam = -0.019       # Travel time parameter
b_trs_uam = -0.017       # Transfers parameter

# Input variables Needed for Equations

    # Trip/Person
OrgVec = TripGen.df3['zone'].to_numpy(dtype='int32')
DestVec = TripGen.df3['workplace'].to_numpy(dtype='int32')

Dict = {77:0, 75:1, 78:2, 91:3, 92:4, 93:5, 94:6, 95:7} #z,y,x,w,v,u,t,s

e = []
for i in OrgVec:
    e.append(Dict[i])
e=np.array(e)
f = []
for j in DestVec:
    f.append(Dict[j])
f=np.array(f)

# Trip/Person
DistMat = TripDis.df1.to_numpy(dtype='float')
x_cdis = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    x_cdis[i] = DistMat[e[i],f[i]] # Crowfly distance [km]
x_inc = TripGen.df3['income'].to_numpy()  # Income [Eur]

    #Car
TcarMat = TripDis.df2.to_numpy(dtype='float')
x_trv_car = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    x_trv_car[i] = TcarMat[e[i],f[i]] # Travel time [min]

CcarMat = TripDis.df5.to_numpy(dtype='float')
c_car = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    c_car[i] = CcarMat[e[i], f[i]]      # Cost [Eur]

    #Public Transport
TptMat = TripDis.df3.to_numpy(dtype='float')
x_trv_pt = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    x_trv_pt[i] = TptMat[e[i],f[i]] # Travel time [min]
x_wait_pt = 5       # Waiting time [min]
x_trs_pt = 1        # Transfers
x_egs_pt = 10        # Egress time [min]

CptMat = TripDis.df6.to_numpy(dtype='float')
c_pt = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    c_pt[i] = CptMat[e[i], f[i]]      # Cost [Eur]

    #UAM
TuamMat = TripDis.df4.to_numpy(dtype='float')
x_trv_uam = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    x_trv_uam[i] = TuamMat[e[i],f[i]]   # Travel time [min]
x_trs_uam = 0       # Transfers
CuamMat = TripDis.df7.to_numpy(dtype='float')
c_uam = np.zeros(DestVec.shape)
for i in range(DestVec.shape[0]):
    c_uam[i] = CuamMat[e[i], f[i]]      # Cost [Eur]

        #Walking
a_wak = 0.631       # Inherent utility
b_wak = -0.141      # Travel time parameter [min**-1]
x_trv_wak = 10       # Travel time [min]

u_acsm = a_wak + b_wak * x_trv_wak  # Access mode utility
u_egsm = u_acsm     # Egress mode utility

#iterations
for i in range(1, 4):
    #b_c = 2 * i * -0.126  # Cost parameter
    l_dis_c = 2 * i * -0.100  # Distance/cost parameter
    #l_inc_c = 2 * i * -0.15  # Income/cost parameter
    # c_UAM = 6 CHF + 2 * i * 0.6 -> only valid for i in [1, 7]
# for i in range(5):
#     b_c = 0.5 * -0.126  # Cost parameter
#     l_dis_c = 0.5 * i * -0.400  # Distance/cost parameter
#     l_inc_c = 0.5 * i * -0.15  # Income/cost parameter
#     c_UAM = 6 CHF + 2 * i * 0.6 -> only valid for i in [1, 7]
#     # end of iterations
    # Equations
    u_car = a_car + b_car * x_trv_car + b_c * ((x_cdis / th_acdis) ** l_dis_c) * ((x_inc / th_ai) ** l_inc_c) * c_car

    u_pt = a_pt + b_trv_pt * x_trv_pt + b_egs_pt * x_egs_pt + b_wait_pt * x_wait_pt + b_trs_pt * x_trs_pt + b_c * (
                (x_cdis / th_acdis) ** l_dis_c) * ((x_inc / th_ai) ** l_inc_c) * c_pt

    u_uam = a_uam + b_trv_uam * x_trv_uam + b_c * ((x_cdis / th_acdis) ** l_dis_c) * (
                (x_inc / th_ai) ** l_inc_c) * c_uam + b_trs_uam * x_trs_uam + u_acsm + u_egsm

    # Mode choice

    beta = 1
    usum = np.exp(beta * u_car) + np.exp(beta * u_pt) + np.exp(beta * u_uam)
    # Car
    P_car = np.exp(beta * u_car) / usum
    print(P_car)
    N_car = np.sum(P_car)
    print(N_car)

    # Public Transport
    P_pt = np.exp(beta * u_pt) / usum
    print(P_pt)
    N_pt = np.sum(P_pt)
    print(N_pt)

    # UAM
    P_uam = np.exp(beta * u_uam) / usum
    print(P_uam)
    N_uam = np.sum(P_uam)
    print(N_uam)

    # Total
    P_tot = P_car + P_pt + P_uam

    # Graphs
    labels = 'UAM', 'Car', 'PT'
    N_size = [N_uam, N_car, N_pt]
    explode = (0.1, 0, 0)
    fig1, ax1 = plt.subplots()
    ax1.pie(N_size, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()





# O-D UAM Trips Table
# Dict = {77:0, 75:1, 78:2, 91:3, 92:4, 93:5, 94:6, 95:7} #z,y,x,w,v,u,t,s
# z
# zy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 75:
#             zy.append(1)
# from77to75 = sum(zy)
# print(from77to75)
#
# zx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 78:
#             zx.append(1)
# from77to78 = sum(zx)
# print(from77to78)
#
# zw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 91:
#             zw.append(1)
# from77to91 = sum(zw)
# print(from77to91)
#
# zv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 92:
#             zv.append(1)
# from77to92 = sum(zv)
# print(from77to92)
#
# zu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 93:
#             zu.append(1)
# from77to93 = sum(zu)
# print(from77to93)
#
# zt = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 94:
#             zt.append(1)
# from77to94 = sum(zt)
# print(from77to94)
#
# zs = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 77 and j == 95:
#             zs.append(1)
# from77to95 = sum(zs)
# print(from77to95)
#
# # y
# yz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 77:
#             yz.append(1)
# from75to77 = sum(yz)
# print(from75to77)
#
# yx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 78:
#             yx.append(1)
# from75to78 = sum(yx)
# print(from75to78)
#
# yw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 91:
#             yw.append(1)
# from75to91 = sum(yw)
# print(from75to91)
#
# yv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 92:
#             yv.append(1)
# from75to92 = sum(yv)
# print(from75to92)
#
# yu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 93:
#             yu.append(1)
# from75to93 = sum(yu)
# print(from75to93)
#
# yt = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 94:
#             yt.append(1)
# from75to94 = sum(yt)
# print(from75to94)
#
# ys = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 75 and j == 95:
#             ys.append(1)
# from75to95 = sum(ys)
# print(from75to95)
#
# # x
# xz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 77:
#             xz.append(1)
# from78to77 = sum(xz)
# print(from78to77)
#
# xy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 75:
#             xy.append(1)
# from78to75 = sum(xy)
# print(from78to75)
#
# xw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 91:
#             xw.append(1)
# from78to91 = sum(xw)
# print(from78to91)
#
# xv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 92:
#             xv.append(1)
# from78to92 = sum(xv)
# print(from78to92)
#
# xu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 93:
#             xu.append(1)
# from78to93 = sum(xu)
# print(from78to93)
#
# xt = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 94:
#             xt.append(1)
# from78to94 = sum(xt)
# print(from78to94)
#
# xs = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 78 and j == 95:
#             xs.append(1)
# from78to95 = sum(xs)
# print(from78to95)
#
# # w
# wz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 77:
#             wz.append(1)
# from91to77 = sum(wz)
# print(from91to77)
#
# wy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 75:
#             wy.append(1)
# from91to75 = sum(wy)
# print(from91to75)
#
# wx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 78:
#             wx.append(1)
# from91to78 = sum(wx)
# print(from91to78)
#
# wv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 92:
#             wv.append(1)
# from91to92 = sum(wv)
# print(from91to92)
#
# wu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 93:
#             wu.append(1)
# from91to93 = sum(wu)
# print(from91to93)
#
# wt = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 94:
#             wt.append(1)
# from91to94 = sum(wt)
# print(from91to94)
#
# ws = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 91 and j == 95:
#             ws.append(1)
# from91to95 = sum(ws)
# print(from91to95)
#
# # v
# vz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 77:
#             vz.append(1)
# from92to77 = sum(vz)
# print(from92to77)
#
# vy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 75:
#             vy.append(1)
# from92to75 = sum(vy)
# print(from92to75)
#
# vx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 78:
#             vx.append(1)
# from92to78 = sum(vx)
# print(from92to78)
#
# vw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 91:
#             vw.append(1)
# from92to91 = sum(vw)
# print(from92to91)
#
# vu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 93:
#             vu.append(1)
# from92to93 = sum(vu)
# print(from92to93)
#
# vt = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 94:
#             vt.append(1)
# from92to94 = sum(vt)
# print(from92to94)
#
# vs = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 92 and j == 95:
#             vs.append(1)
# from92to95 = sum(vs)
# print(from92to95)
#
# # u
# uz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 77:
#             uz.append(1)
# from93to77 = sum(uz)
# print(from93to77)
#
# uy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 75:
#             uy.append(1)
# from93to75 = sum(uy)
# print(from93to75)
#
# ux = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 78:
#             ux.append(1)
# from93to78 = sum(ux)
# print(from93to78)
#
# uw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 91:
#             uw.append(1)
# from93to91 = sum(uw)
# print(from93to91)
#
# uv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 92:
#             uv.append(1)
# from93to92 = sum(uv)
# print(from93to92)
#
# ut = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 94:
#             ut.append(1)
# from93to94 = sum(ut)
# print(from93to94)
#
# us = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 93 and j == 95:
#             us.append(1)
# from93to95 = sum(us)
# print(from93to95)
#
# # t
# tz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 77:
#             tz.append(1)
# from94to77 = sum(tz)
# print(from94to77)
#
# ty = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 75:
#             ty.append(1)
# from94to75 = sum(ty)
# print(from94to75)
#
# tx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 78:
#             tx.append(1)
# from94to78 = sum(tx)
# print(from94to78)
#
# tw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 91:
#             tw.append(1)
# from94to91 = sum(tw)
# print(from94to91)
#
# tv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 92:
#             tv.append(1)
# from94to92 = sum(tv)
# print(from94to92)
#
# tu = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 93:
#             tu.append(1)
# from94to93 = sum(tu)
# print(from94to93)
#
# ts = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 94 and j == 95:
#             ts.append(1)
# from94to95 = sum(ts)
# print(from94to95)
#
# # s
# sz = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 77:
#             sz.append(1)
# from95to77 = sum(sz)
# print(from95to77)
#
# sy = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 75:
#             sy.append(1)
# from95to75 = sum(sy)
# print(from95to75)
#
# sx = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 78:
#             sx.append(1)
# from95to78 = sum(sx)
# print(from95to78)
#
# sw = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 91:
#             sw.append(1)
# from95to91 = sum(sw)
# print(from95to91)
#
# sv = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 92:
#             sv.append(1)
# from95to92 = sum(sv)
# print(from95to92)
#
# su = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 93:
#             su.append(1)
# from95to93 = sum(su)
# print(from95to93)
#
# st = []
# for i in OrgVec:
#     for j in DestVec:
#         if i == 95 and j == 94:
#             st.append(1)
# from95to94 = sum(st)
# print(from95to94)
#
# tot = []
# for i in OrgVec:
#     for j in DestVec:
#         tot.append(1)
# tottrip = sum(tot)
# print(tottrip)