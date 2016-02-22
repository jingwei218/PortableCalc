from itertools import *
from copy import deepcopy

#class of calculation table
class U:

    __atom_combinations = []
    __atom_combinations__ = {}

    def __init__(self, rawDataObjs=None):
        '''rawDataObjs: a sequence of raw data objects (only include tables to be mixed)
               format as follows:
               [[column 1], [column 2], ... [column n]]
               in each column:
               [row 1], [row 2], ... [row m]
               in each row:
               [Name], [Aggregation], [Value], [Id]
        '''
        self.rawDataObjs = rawDataObjs
        self.nbr_of_mixin = len(rawDataObjs) #number of tables
        self.nbr_of_columns = len(rawDataObjs[0].table) #number of columns in tables, all rows of tables should contain the same number of columns
        self.nbr_of_rows = len(rawDataObjs[0].table[0]) #number of rows in tables, all tables should contain the same number of rows
        self.atoms = {} #dict {vendor-aggregation: [aggregation_name, aggregation_value, [ids]]}
        self.aggregations = [] #aggregation names
        self.vendors = [] #vendor names

        for k in range(self.nbr_of_mixin):
            for i in range(self.nbr_of_columns):
                for j in range(self.nbr_of_rows):
                    vendor = self.rawDataObjs[k].table[i][j][0] #the kth table, ith column, jth row, 1st item
                    name = self.rawDataObjs[k].table[i][j][1] #the kth table, ith column, jth row, 2nd item
                    value = self.rawDataObjs[k].table[i][j][2] #the kth table, ith column, jth row, 3rd item
                    id = j + 1 #self.rawDataObjs[k].table[i][j][3] #the kth table, ith column, jth row, 4th item
                    if name not in self.aggregations and name != "U" and value > 0: #aggregation not aggregated yet
                        self.aggregations.append(name)
                        self.atoms[vendor + "-" + name] = [vendor, name, value, [id]] #atom[0][1][2][3]
                    elif name in self.aggregations and name != "U" and value == 0: #aggregation aggregated
                        self.atoms[vendor + "-" + name][3].append(id)
                    elif name not in self.aggregations and name == "U" and value > 0: #single items
                        self.atoms[vendor + "-" + name + "-" + str(id)] = [vendor, name, value, [id]]
                    if vendor not in self.vendors:
                        self.vendors.append(vendor)

    def getInterimAtoms(self, filterby=[0], filterlist=None):
        '''get sorted interim atoms list
           filter by xth item in atom
           filterlist should map [[filterby0], [filterby1], ...]
        '''
        self.filterList = filterlist
        self.__atom_combinations__[tuple(self.filterList)] = []
        _atoms_interim = [] #sorted list of aggregations derived from atoms dict [[vendor name, aggregation name, value, aggregation], ...]
        for atom in self.atoms:
            _bfilter = True #boolean flag of filter
            for fb in filterby:
                _bfilter = _bfilter and self.atoms[atom][fb] in filterlist[fb] #item in atoms[atom][x] also in filterlist[x]
            if _bfilter:
                _atoms_interim.append(self.atoms[atom]) #add atoms to interim list
        _atoms_interim.sort(key=lambda x: x[3]) #sort by 4th item (aggregation)
        return _atoms_interim

    def removeRedundancy(self, atomList, keepMax = False):
        '''remove duplicates and redundancy in atoms_interim'''
        coef = 1 if keepMax == False else -1 #coefficient used to compare Max or Min
        _atoms_no_duplicate = [] #take out redundancy leaving max or min value of same shapes
        tempAtom = atomList[0] #initialise temp atom
        for atom in atomList:
            tempVal = atom[2] #value of atom
            tempAggregation = atom[3] #aggregation of atom
            if tempAggregation == tempAtom[3]: #if in same shape
                if coef*tempVal < coef*tempAtom[2]: #compare
                    tempAtom = atom
            else:
                _atoms_no_duplicate.append(tempAtom) #append atom of last aggregation before current one
                tempAtom = atom #switch to new aggregation
        _atoms_no_duplicate.append(tempAtom) #append last atom
        return _atoms_no_duplicate

    def structureAtoms(self, atomList): #[vendor name, aggregation name, value, aggregation, [links], [[link indices],...]], ...]
        _atoms_structured = deepcopy(atomList)
        for atom in _atoms_structured:
            lastId = atom[3][len(atom[3]) - 1] #last id in aggregation
            atomIndex = _atoms_structured.index(atom) #index of atom in _atoms_structured
            atomsAfter = _atoms_structured[atomIndex+1 : len(_atoms_structured)]
            atom.append(atomIndex) #atom[4]
            nextAtomIds = list(set(range(atom[3][0], lastId + 1)).difference(set(atom[3]))) #ids not continuous, ids in between become links
            if lastId < self.nbr_of_rows: #not last atom in column
                nextAtomIds.append(lastId + 1) #add additional link after lastId to links
            atom.append(nextAtomIds) #atom[5] atom ids
            if nextAtomIds != []: #there is one or more next atoms
                nextAtomIndices = findNextAtomIndices(atomList, nextAtomIds) #list of nextAtom indices
            else:
                nextAtomIndices = []
            atom.append(nextAtomIndices) #atom[6] atom indices
        return _atoms_structured

    #startAtoms = [x for x in atomList if x[3][0]==1]
    def getAllCombinations(self, atomList, startAtoms, startComboAtoms=[], startRedLines=[], startExtraAtoms=[]):
        for atom in startAtoms:
            bTouchRedLine = False
            comboAtoms = deepcopy(startComboAtoms)
            redLines = deepcopy(startRedLines)
            extraAtoms = deepcopy(startExtraAtoms)
            for aggregation in atom[3]: #go through atom's aggregation
                if aggregation in redLines:
                    bTouchRedLine = True #touch red line
                    break #stop for loop if touch red line
                else:
                    redLines.append(aggregation)
            if bTouchRedLine == True:
                continue #skip this atom
            else:
                comboAtoms.append(atom)
            if atom[5] != []: #not the last in column, has next atom to connect
                newStartAtoms = [] #new startAtoms for next iteration
                for m in atom[6]: #go through indices of nextAtoms
                    newStartAtoms.append(atomList[m])
                for ea in extraAtoms:
                    if ea[3] in redLines:
                        extraAtoms.remove(ea)
                    if ea not in newStartAtoms:
                        newStartAtoms.append(ea)
                if len(atom[5]) > 1:
                    extraStartIds = atom[5][1:len(atom[5])+1]
                    for n in findNextAtomIndices(atomList, extraStartIds):
                        if atomList[n] not in extraAtoms:
                            extraAtoms.append(atomList[n])
                self.getAllCombinations(atomList, newStartAtoms, comboAtoms, redLines, extraAtoms)
            else:
                if isValidCombination(comboAtoms, list(range(1, self.nbr_of_rows+1))):
                    self.__atom_combinations.append(comboAtoms)
                    self.__atom_combinations__[tuple(self.filterList)].append(comboAtoms)

    def getCombinationList(self):
        return self.__atom_combinations

    def getCombinationDict(self, key=None):
        if key == None:
            return self.__atom_combinations__
        else:
            return self.__atom_combinations__[key]

def findNextAtomIndices(atomList, startIds):
    _foundAtomIndices = []
    for atom in atomList:
        if atom[3][0] in startIds:
            _foundAtomIndices.append(atomList.index(atom))
    return _foundAtomIndices

def isValidCombination(atomList, idList):
    _idList = []
    for atom in atomList:
        for id in atom[3]:
            _idList.append(id)
    diff = list(set(idList).difference(set(_idList)))
    if diff == []:
        return True
    else:
        return False