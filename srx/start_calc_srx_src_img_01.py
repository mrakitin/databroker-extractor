import os

gap = 6.715 #7.193 #[mm]
ePh = 8000 #12398.4 #[eV]
ePhIntRange = 0 #10. #[eV]
branchBL = 7

sNamePyScript = 'SRWLIB_VirtBL_SRX_01.py'

minProc = 8
#maxProc = 31

enInt = 1
if(ePhIntRange <= 0.): enInt = 0

sPathPyScript = os.path.join(os.getcwd(), sNamePyScript)

#sArgsPyScript = ' --ws'
sArgsPyScript = ' --wm'

sArgsPyScript += ' --wm_fni=res_int_pr_me_hfm_imperf_off.dat'

sArgsPyScript += ' --und_g=' + repr(gap) + ' --w_mag=2'

sArgsPyScript += ' --w_e=' + repr(ePh - 0.5*ePhIntRange) + ' --w_ef=' + repr(ePh + 0.5*ePhIntRange) + ' --wm_ei=' + repr(enInt) + ' --op_DCM_e=' + repr(ePh)

sArgsPyScript += ' --w_smpf=0.1' #0.065'

sArgsPyScript += ' --w_rx=2.5e-03 --w_ry=2.e-03'

sArgsPyScript += ' --op_BL=' + repr(branchBL)

sArgsPyScript += ' --op_S0_dx=2.5e-03 --op_S0_dy=2.e-03'

sArgsPyScript += ' --op_HFM_r=20000' #12573.9'

#sArgsPyScript += ' --op_HFM_r=12349.5'
sArgsPyScript += ' --op_HFM_f=0.'
#sArgsPyScript += ' --op_HFM_ifn=  '

sArgsPyScript += ' --op_fin=HFM_SMP'

sArgsPyScript += ' --op_S0_pp=[0,0,1,0,0,1.0,3.0,1.2,1.0,0,0,0]'
sArgsPyScript += ' --op_fin_pp=[0,0,1,0,0,1.0,1.0,1.0,1.0,0,0,0]'

s2exe = 'mpiexec -n ' + repr(minProc) + ' python ' + sPathPyScript + sArgsPyScript
#s2exe = 'python ' + sPathPyScript + sArgsPyScript

#print(s2exe)

os.system(s2exe)
