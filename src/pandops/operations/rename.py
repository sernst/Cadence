
import six

#_______________________________________________________________________________
def column(dataFrame, oldName, newName):
    result = dataFrame.columns + []
    for value in dataFrame.columns:
        result.append(
            newName
            if value == oldName else
            value)
    dataFrame.columns = result
    return result

#_______________________________________________________________________________
def columns(dataFrame, values = None, **kwargs):
    if not values and not kwargs:
        return dataFrame.columns

    renames = {}
    for source in [values, kwargs]:
        if not source:
            continue

        for n, v in six.iteritems(source):
            renames[n] = v

    result = []
    for value in dataFrame.columns:
        result.append(
            renames[value]
            if value in renames else
            value)
    dataFrame.columns = result
    return result

