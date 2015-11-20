#! /usr/bin/env python

import locale
from dialog import Dialog

import sys
import capnp
import operator
import glob

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")
d.set_background_title("Captain Config: Cap'n Proto Explorer")

floatTypes = ['float32','float64']
integralTypes = ['uint8','uint16','uint32','uint64','int8','int16','int32','int64']

def fieldTypeAsString(field):
    '''Determine the type of the field'''
    try:
        return field.schema.node.which()
    except (capnp.KjException,AttributeError) as e:
        return field.proto.slot.type.which() #to_dict().keys()[0]

def abbreviate(obj):
    '''Stringify object and, if necessary, abbreviate and append ellipsis'''
    s = str(obj)
    if len(s) > 10:
       s = s[:10]+'...' 
    return s

def unionDialog(node):
    (code,selectedField) = d.radiolist('Union',
        choices = [(x,'',True if x==node.which() else False) for x in node.schema.union_fields])

    if code == Dialog.CANCEL:
        return 

    handleField(node,selectedField)
    return

def getValueDialog(node,tag,datatype,setInit=True):
    stringRepr = str(datatype).split("'")[1]
    (code,inp) = d.inputbox('Set %s field' % stringRepr, init = str(getattr(node,tag) if setInit else ''))
    if code == Dialog.OK:
        try:
            setattr(node,tag, datatype(inp))
        except capnp.KjException:
            d.msgbox('Illegal value')
        except ValueError:
            d.msgbox("Please enter a value of type '%s'" % stringRepr)

def isNamedUnion(node):
    return len(node.schema.non_union_fields) == 0

def handleStruct(node):
    while True:
        if isNamedUnion(node):
            unionDialog(node)
            return

        visibleFields = node.schema.non_union_fields

        if len( node.schema.union_fields)>0:
            # in case of an unnamed union: 
            # add the active union field to the list of visible fields
            visibleFields += (node.which(),)

        (code, tag) = d.menu('Traverse struct', ok_label='Modify',cancel_label='Exit',choices = [(name,abbreviate(getattr(node,name))) for name in visibleFields])

        if code == Dialog.CANCEL:
            return 

        if len(node.schema.union_fields)>0 and tag == node.which():
            # the user has selected the field 
            # that corresponds to the unnamed union
            unionDialog(node)

        else:    
            handleField(node,tag)



def handleField(node,tag,setInit = True):
    '''
    The 'setInit' option can be used to prevent fields from displaying the current value.
    I.e., trying to get() a union member which is not currently initialized gives a KjException,
    which we use here in the following way: we try to display the current value (setInit = True), 
    if this results in an exception we retry with 'setInit = False'
    '''
    try:
        field = node.schema.fields[tag] 
    
        fieldtype = fieldTypeAsString(field)
    
        if fieldtype == 'enum':
    
            sortedItems = sorted(field.schema.enumerants.items(),key=operator.itemgetter(1))
    
            (code,enumerant) = d.radiolist('Select enumerant', choices = [(x[0],'',True if x[0] == getattr(node,tag) else False) for x in sortedItems])
            setattr(node,tag, enumerant)
    
        elif fieldtype == 'bool':
            (code,tf) = d.radiolist('Select boolean', choices = [(str(x),'',getattr(node,tag)==x) for x in [True,False]])
            val = True if tf == 'True' else False
            setattr(node,tag, val)
    
        elif fieldtype == 'text':
            (code,string) = d.inputbox('Set text field', init = getattr(node,tag) if setInit else '')
            if code == Dialog.OK:
                setattr(node,tag, string)
    
        elif fieldtype == 'struct':
            handleStruct(getattr(node,tag))
    
        elif fieldtype in floatTypes:
            getValueDialog(node,tag,float,setInit)
    
        elif fieldtype in integralTypes:
            getValueDialog(node,tag,int,setInit)
    
        elif fieldtype == 'void':
            setattr(node,tag,None)
    
        elif fieldtype == 'list':
            print 'list'
            exit()
    
        else:
            print fieldtype
            exit()
    except capnp.KjException:
          return handleField(node,tag, False)
    
def main():

    currPath = sys.path[0]
    wildcard = '*.capnp'
 
    chWildcard = 'Change schema wildcard'
    chDir = 'Change directory'

    while True:

        schemaFiles = [(x,'') for x in glob.glob(wildcard)]
        code, tag = d.menu('Schema selection',
                           choices=schemaFiles+[
                               (chDir, '('+currPath+')'),
                               (chWildcard, '('+wildcard+')')])
    
        if code == Dialog.CANCEL:
            return
    
        if tag == chWildcard:
            code, tag = d.inputbox('Wildcard',init = wildcard)
            if code == Dialog.OK:
                wildcard = tag
            continue
    
        if tag == chDir:
            code, tag = d.dselect(currPath)
            if code == Dialog.OK:
                currPath = tag

        else:
            break
    
    userSchema = capnp.load(str(tag))

    (code,rootStruct) = d.menu('Select root struct', 
                         choices = [(x.name,'') for x in userSchema.schema.node.nestedNodes])

    msg = getattr(userSchema, rootStruct).new_message()

    handleStruct(msg)

    print msg.to_dict()


if __name__ == "__main__":
    main()


