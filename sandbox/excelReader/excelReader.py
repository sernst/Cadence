import xlrd

book = xlrd.open_workbook('C:\\Users\\scott\\Desktop\\A16\\TCH_S_1000.xls')

print book.nsheets
print book.sheet_names()

sh = book.sheet_by_index(0)
print sh.name, sh.nrows, sh.ncols

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

#___________________________________________________________________________________________________ CellParser
class CellParser(object):

#___________________________________________________________________________________________________ __init__
    def __init__(self, source, row =0, column =0):
        self._source = source
        self._row    = row
        self._column = column

#___________________________________________________________________________________________________ GS: source
    @property
    def source(self):
        return self._source

#___________________________________________________________________________________________________ GS: value
    @property
    def value(self):
        if self._row == -1 or self._column == -1:
            return None
        return self._source[self._row][self._column]

#___________________________________________________________________________________________________ GS: row
    @property
    def row(self):
        return self._row
    @row.setter
    def row(self, value):
        self._row = value

#___________________________________________________________________________________________________ GS: column
    @property
    def column(self):
        return self._column
    @column.setter
    def column(self, value):
        self._column = value

#___________________________________________________________________________________________________ find
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

#___________________________________________________________________________________________________ nextRow
    def clone(self):
        return CellParser(self._source, self._row, self._column)

#___________________________________________________________________________________________________ nextRow
    def nextRow(self):
        if self._row == -1:
            return
        self._row += 1

#___________________________________________________________________________________________________ getNextRow
    def getNextRow(self):
        out = self.clone()
        if self._row == -1:
            return out
        out.nextRow()
        return out

#___________________________________________________________________________________________________ nextColumn
    def nextColumn(self):
        if self._column == -1:
            return
        self._column += 1

#___________________________________________________________________________________________________ getNextColumn
    def getNextColumn(self):
        out = self.clone()
        if self._column == -1:
            return out
        out.nextColumn()
        return out

#___________________________________________________________________________________________________ getValueBelow
    def getValueBelow(self, key):
        out = self.find(key)
        if out.value is None:
            return out
        out.nextRow()
        return out

#___________________________________________________________________________________________________ __str__
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

