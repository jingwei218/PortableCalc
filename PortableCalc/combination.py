from itertools import *
from copy import deepcopy

class U:

    __atom_combinations = []
    __index_test = 0

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

        for k in range(self.nbr_of_mixin):
            for i in range(self.nbr_of_columns):
                for j in range(self.nbr_of_rows):
                    vendor = self.rawDataObjs[k].table[i][j][0] #the kth table, ith column, jth row, 1st item
                    name = self.rawDataObjs[k].table[i][j][1] #the kth table, ith column, jth row, 2nd item
                    value = self.rawDataObjs[k].table[i][j][2] #the kth table, ith column, jth row, 3rd item
                    id = j + 1 #self.rawDataObjs[k].table[i][j][3] #the kth table, ith column, jth row, 4th item
                    if name not in self.aggregations and name != "U" and value > 0: #aggregation not aggregated yet
                        self.aggregations.append(name)
                        self.atoms[vendor + "-" + name] = [vendor, name, value, [id]]
                    elif name in self.aggregations and name != "U" and value == 0: #aggregation aggregated
                        self.atoms[vendor + "-" + name][3].append(id)
                    elif name not in self.aggregations and name == "U" and value > 0: #single items
                        self.atoms[vendor + "-" + name + "-" + str(id)] = [vendor, name, value, [id]]

    def getInterimAtoms(self, filterby=[0], filterlist=None):
        '''get sorted interim atoms list
           filter by xth item in atom
           filterlist should map atom [[filterby0], [filterby1], ...]
        '''
        self.__atoms_interim = [] #sorted list of aggregations derived from atoms dict [[vendor name, aggregation name, value, aggregation], ...]
        for atom in self.atoms:
            _bfilter = True #boolean flag of filter
            for fb in filterby:
                _bfilter = _bfilter and self.atoms[atom][fb] in filterlist[fb] #item in atoms[atom][x] also in filterlist[x]
            if _bfilter:
                self.__atoms_interim.append(self.atoms[atom]) #add atoms to interim list
        self.__atoms_interim.sort(key=lambda x: x[3]) #sort by 4th item (aggregation)
        return self.__atoms_interim

    def removeRedundancy(self, atomsList, keepMax = False):
        '''remove duplicates and redundancy in atoms_interim'''
        coef = 1 if keepMax == False else -1 #coefficient used to compare Max or Min
        self.__atoms_no_duplicate = [] #take out redundancy leaving max or min value of same shapes
        tempAtom = atomsList[0] #initialise temp atom list
        for atom in atomsList:
            tempVal = atom[2] #value of atom
            tempAggregation = atom[3] #aggregation of atom
            tempName = atom[0] #vendor name
            if tempAggregation == tempAtom[3]: #if in same shape
                if coef*tempVal < coef*tempAtom[2]: #compare
                    tempAtom = atom
            else:
                self.__atoms_no_duplicate.append(tempAtom) #append atom of last aggregation
                tempAtom = atom #switch to new aggregation
        self.__atoms_no_duplicate.append(tempAtom) #append last atom
        
        self.__atoms_complete = deepcopy(self.__atoms_no_duplicate) #[vendor name, aggregation name, value, aggregation, [links], [[link indices]...]], ...]
        for atom in self.__atoms_complete:
            lastId = atom[3][len(atom[3]) - 1] #last id in aggregation
            atomIndex = self.__atoms_complete.index(atom) #index of atom in __atoms_complete
            atom.append(atomIndex) #atom[4]
            links = list(set(range(atom[3][0], lastId + 1)).difference(set(atom[3]))) #ids not continuous, ids in between become links
            if lastId < self.nbr_of_rows: #not last atom in column
                links.append(lastId + 1) #add additional link to links
            atom.append(links) #atom[5]
            #linkPoints = []
            #atomsAfter = self.__atoms_complete[atomIndex+1 : len(self.__atoms_complete)]
            #if links != []:
            #    for linkPoint in links:
            #        tempIndices = []
            #        for nextAtom in atomsAfter:
            #            if nextAtom[3][0] == linkPoint:
            #                linkIndex = self.__atoms_complete.index(nextAtom) #index of linkAtom in _atom_no_duplicate
            #                tempIndices.append(linkIndex) #indices of atoms that can link this atom
            #        linkPoints.append(tempIndices)
            #atom.append(linkPoints) #atom[6]
        return self.__atoms_complete

    #startAtoms = [x for x in atomList if x[3][0]==1]
    def getAllCombinations(self, atomList, startAtoms, startComboAtoms=[], startRedLines=[]):
        for atom in startAtoms:
            comboAtoms = deepcopy(startComboAtoms)
            redLines = deepcopy(startRedLines)
            comboAtoms.append(atom)
            if atom[5] != []:
                newStartAtoms = []
                for n in atom[5]:
                    newStartAtoms.append(atomList[n])
                self.getAllCombinations(atomList, newStartAtoms, comboAtoms)
            else:
                self.__atom_combinations.append(comboAtoms)
                startRedLines = []