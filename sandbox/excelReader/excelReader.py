import sys
import xlrd

book = xlrd.open_workbook('C:\\Users\\sernst\\Desktop\\spreadsheets\\Bdd_Sauro2013_05_17.xls')

sheetIndex = 0
while sheetIndex < book.nsheets:
    sh = book.sheet_by_index(sheetIndex)
    print 'SHEET: [NAME: %s] [ROWS: %s] [COLUMNS: %s]' % (sh.name, sh.nrows, sh.ncols)
    sheetIndex += 1

sys.exit()

rows     = []
col      = []
rowIndex = 0
colIndex = 0
for rowIndex in range(sh.nrows):
    for colIndex in range(sh.ncols):
        col.append(sh.cell_value(rowIndex, colIndex))
    rows.append(col)
    col = []

for r in rows:
    print r

#_______________________________________________________________________________
class CellParser(object):

#_______________________________________________________________________________
    def __init__(self, source, row =0, column =0):
        self._source = source
        self._row    = row
        self._column = column

#_______________________________________________________________________________
    @property
    def source(self):
        return self._source

#_______________________________________________________________________________
    @property
    def value(self):
        if self._row == -1 or self._column == -1:
            return None
        return self._source[self._row][self._column]

#_______________________________________________________________________________
    @property
    def row(self):
        return self._row
    @row.setter
    def row(self, value):
        self._row = value

#_______________________________________________________________________________
    @property
    def column(self):
        return self._column
    @column.setter
    def column(self, value):
        self._column = value

#_______________________________________________________________________________
    def find(self, keys, rowOffset =0, maxRow =None, colOffset =0, maxCol =None):
        row = 0
        col = 0

        if not isinstance(keys, list):
            keys = [keys]

        for r in self._source[rowOffset:maxRow]:
            for val in r[colOffset:maxCol]:
                if val in keys:
                    return CellParser(self._source, row, col)
                col += 1
            row += 1

        return CellParser(self._source, -1, -1)

#_______________________________________________________________________________
    def clone(self):
        return CellParser(self._source, self._row, self._column)

#_______________________________________________________________________________
    def nextRow(self):
        if self._row == -1:
            return
        self._row += 1

#_______________________________________________________________________________
    def getNextRow(self):
        out = self.clone()
        if self._row == -1:
            return out
        out.nextRow()
        return out

#_______________________________________________________________________________
    def nextColumn(self):
        if self._column == -1:
            return
        self._column += 1

#_______________________________________________________________________________
    def getNextColumn(self):
        out = self.clone()
        if self._column == -1:
            return out
        out.nextColumn()
        return out

#_______________________________________________________________________________
    def getValueBelow(self, key):
        out = self.find(key)
        if out.value is None:
            return out
        out.nextRow()
        return out

#_______________________________________________________________________________
    def __str__(self):
        return '<Cell (%s, %s) "%s">' % (str(self.row), str(self.column), str(self.value))

cell = CellParser(rows)
print 'Site:', cell.getValueBelow('site').value
print 'Layer:', int(cell.getValueBelow('couche').value)

trackID = cell.getValueBelow('piste')
if trackID.value:
    print 'ID:', str(trackID.value) + str(int(trackID.getNextColumn().value))
else:
    print 'ID:', 'NO ID FOUND!'

print 'Sector:', int(cell.getValueBelow('secteur').value)

#for item in dir(sh):
#    if item.startswith('_'):
#        continue
#
#    try:
#        print item, getattr(sh, item, 'UNKNOWN')
#    except Exception, err:
#        print item, 'FAILED'

