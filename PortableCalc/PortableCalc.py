from xlsx import *
from combination import *

xldata = []
for col in first_columns:
    xldata.append(xlsxData(start_x=col))
u = U(xldata)

#testing
ux=u.getInterimAtoms(filterlist=[["Schenker", "DHL"]])
ud=u.removeRedundancy(ux)
sp=[x for x in ud if x[3][0]==1]
#ul = u.getAllCombinations(ud, sp)