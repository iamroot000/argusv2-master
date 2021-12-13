def generateBulkInsertSQL2(table, fields, values, onDuplicates=None):
    #sql = 'INSERT INTO {0} {1} VALUES {2} '.format(table, fields, values)
    sql = ''
    updateSTR = ''
    flag = False
    for field in fields:
        if not flag:
            updateSTR = updateSTR + "`{0}`=VALUES({0})".format(field)
            flag = True
        else:
            updateSTR = updateSTR + ", `{0}`=VALUES({0})".format(field)


    fld = str(fields).replace("'", "`").replace("[","(").replace("]",")")

    if onDuplicates == 'UPDATE':
        update = 'ON DUPLICATE KEY UPDATE {0};'.format(updateSTR)

        sql = 'INSERT INTO {0} {1} VALUES {2} {3}'.format(table, fld, values,update)

    if onDuplicates == 'IGNORE':

        sql = 'INSERT IGNORE INTO {0} {1} VALUES {2}'.format(table, fld, values)

    return sql


def generateBulkInsertSQL(table,fields,values,onDuplicates = None):
    sql = ''
    updateSTR = ''
    flag = False
    for field in fields:
        if not flag:
            updateSTR = updateSTR + "`{0}`=VALUES({0})".format(field)
            flag = True
        else:
            updateSTR = updateSTR + ", `{0}`=VALUES({0})".format(field)

    fld = str(fields).replace("'", "`").replace("[", "(").replace("]", ")")


    if onDuplicates == 'UPDATE':
        update = 'ON DUPLICATE KEY UPDATE {0};'.format(updateSTR)

        sql = 'INSERT INTO {0} {1} VALUES {2} {3}'.format(table, fld, str(values).strip('[').strip(']'), update)

    if onDuplicates == 'IGNORE':
        sql = 'INSERT IGNORE INTO {0} {1} VALUES {2}'.format(table, fld, str(values).strip('[').strip(']'))

    return sql

def upsert(table,fields, values, onDuplicates='IGNORE'):

    base_sql = "INSERT IGNORE INTO %s (%s) VALUES " % (table, ",".join(fields))

    y = False
    for i in values:
        b=False

        p = "('"
        for val in i:
            if not b:
                p=p+val
                b=True
            else:
                p=p+"','"+val+""
        p = p +"')"
        if not y:
            base_sql = base_sql + p
            y=True
        else:
            base_sql = base_sql+"," + p

    return base_sql