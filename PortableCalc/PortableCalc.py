from xlsx import *
from combination import *

#excel based
xldata = []
for col in first_columns:
    xldata.append(xlsxData(start_x=col))
u = U(xldata)

combo_of_vendors = combinations(u.vendors, nbr_of_selected)

#testing
for combo in combo_of_vendors:
    print(combo)
    ui = u.getInterimAtoms(filterlist=[combo])
    print('interim')
    print(ui)
    ur = u.removeRedundancy(ui)
    print('remove redundancy')
    print(ur)
    us = u.structureAtoms(ur)
    print('structured')
    print(us)
    start = [a for a in us if a[3][0]==1]
    u.getAllCombinations(us, start)

x = 1
print('======= start of combinations =========')
for item in u.getCombinationList():
    print(item)
    print('========= end of combo ' + str(x) + ' ============')
    x += 1