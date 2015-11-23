#! /usr/bin/env python

import locale
from dialog import Dialog

import sys
import capnp
import operator
import glob
import os

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")
d.set_background_title("Captain Config: Cap'n Proto Explorer")

floatTypes = ['float32','float64']
integralTypes = ['uint8','uint16','uint32','uint64','int8','int16','int32','int64']
modLen = 'Modify list length'


def fieldTypeAsString(field):
    '''Determine the type of the field'''

    try:
        return field.schema.node.which()
    except capnp.KjException:
        return field.proto.slot.type.which()
    except AttributeError:
        return field.proto.slot.type.which()

def abbreviate(obj):
    '''Stringify object and, if necessary, abbreviate and append ellipsis'''
    s = str(obj)
    if len(s) > 20:
       s = s[:20]+'...' 
    return s

def unionDialog(node):
    (code,selectedField) = d.radiolist('Union',
        choices = [(x,'',True if x==node.which() else False) for x in node.schema.union_fields])

    if code == Dialog.CANCEL:
        return 

    #initialize if necessary
    if node.schema.fields[selectedField].proto.slot.type.which() == 'struct':
        getattr(node,'init')(selectedField)

    handleField(node,selectedField,setInit=False)

def getValueDialog(getter,setter,datatype,setInit=True):
    stringRepr = str(datatype).split("'")[1]
    (code,inp) = d.inputbox('Set %s field' % stringRepr, init = str(getter() if setInit else ''))
    if code == Dialog.OK:
        try:
            setter(datatype(inp))
        except capnp.KjException:
            d.msgbox('Illegal value')
        except ValueError:
            d.msgbox("Please enter a value of type '%s'" % stringRepr)

def isNamedUnion(node):
    return len(node.schema.non_union_fields) == 0

def handleStruct(node,skipUnionCheck=False):
    while True:
        if not skipUnionCheck and isNamedUnion(node):
            unionDialog(node)
            return

        visibleFields = node.schema.non_union_fields

        if len( node.schema.union_fields)>0:
            # in case of an unnamed union: 
            # add the active union field to the list of visible fields
            visibleFields += (node.which(),)

        (code, tag) = d.menu('Traverse struct', ok_label='Modify',cancel_label='Exit' if node.is_root else 'Back',choices = [(name,abbreviate(getattr(node,name))) for name in visibleFields])

        if code == Dialog.CANCEL:
            return 

        if len(node.schema.union_fields)>0 and tag == node.which():
            # the user has selected the field 
            # that corresponds to the unnamed union
            unionDialog(node)

        else:    
            handleField(node,tag)

def listLenDialog():
    while True:
        (code,inp) = d.inputbox('Choose list size')
        if code == Dialog.CANCEL:
            return
        length = int(inp)
        if length > 0:
            node.init(tag,int(inp))
            break
        d.msgbox('Invalid list length')

def handleField(parentNode, fieldName, fieldSchema = None, fieldType = None, getter = None, 
setter = None, setInit = True):
        '''
        The 'setInit' option can be used to prevent fields from displaying the current value.
        (trying to get() a union member which is not currently initialized gives a KjException)
        '''
    
        if getter is None:
            getter = lambda : getattr(parentNode,fieldName) 
        if setter is None:
            setter = lambda x : setattr(parentNode,fieldName,x) 
        if fieldSchema is None:
            fieldSchema  = parentNode.schema.fields[fieldName]
        if fieldType is None:
            fieldType = fieldTypeAsString(fieldSchema) 
    
        if fieldType == 'enum':
    
            sortedItems = sorted(parentNode.schema.fields[fieldName].schema.enumerants.items(),key=operator.itemgetter(1))
            (code,enumerant) = d.radiolist('Select enumerant', choices = [(x[0],'',True if x[0] == getter() else False) for x in sortedItems])
            if code == Dialog.CANCEL:
                return

            setter(enumerant)
    
        elif fieldType == 'bool':
            (code,tf) = d.radiolist('Select boolean', choices = [(str(x),'',getter()==x) for x in [True,False]])
            if code == Dialog.CANCEL:
                return

            val = True if tf == 'True' else False
            setter(val)
    
        elif fieldType in  ['text','str']:
            (code,string) = d.inputbox('Set text field', init = getter() if setInit else '')
            if code == Dialog.CANCEL:
                return

            setter(string)
    
        elif fieldType == 'struct':
            handleStruct(getattr(parentNode,fieldName)) 
    
        elif fieldType in floatTypes:
            getValueDialog(getter,setter,float,setInit)
    
        elif fieldType in integralTypes:
            getValueDialog(getter,setter,int,setInit)
    
        elif fieldType == 'void':
            setter(None)
    
        elif fieldType == 'list':

            if len(getattr(parentNode,fieldName)) == 0:
                while True:
                    (code,inp) = d.inputbox('Choose list size')
                    if code == Dialog.CANCEL:
                        return
                    length = int(inp)
                    if length > 0:
                        parentNode.init(fieldName,int(inp))
                        break
                    d.msgbox('Invalid list length')

            while True:

                menuItems = [(str(i),str(entry)) for i,entry in enumerate(getattr(parentNode,fieldName))]

                (code, selection) = d.menu('Edit list', ok_label='Modify',cancel_label='Back',choices = menuItems + [(modLen,'')] )
                if code == Dialog.CANCEL:
                    return

                if selection == modLen:
                    parentNode.init(fieldName,0)
                    return handleField(parentNode,fieldName) #,field, getter,setter)
                else:
                    gttr = lambda: getattr(parentNode,fieldName)[int(selection)]
                    sttr = lambda x: getattr(getattr(parentNode,fieldName),'__setitem__')(int(selection),x)

                    listElemType = parentNode.schema.fields[fieldName].proto.slot.type.list.elementType.which()

                    if listElemType == 'struct':
                        handleStruct(gttr(),skipUnionCheck = True)
                    else:
                        handleField(parentNode,fieldName, fieldType = listElemType,getter=gttr,setter=sttr)
    
        else:
            print 'Not implemented yet:', fieldType
            exit()
   
class Chdir:         
      def __init__( self ):  
        self.savedPath = os.getcwd()

      def changeDir(self  , newPath ):
        os.chdir(newPath)

      def __del__( self ):
        os.chdir( self.savedPath )

def main():

    dirMngr = Chdir()

    currPath = os.getcwd()
    wildcard = '*.capnp'
 
    chWildcard = 'Change schema wildcard'
    chDir = 'Change directory'

    while True:

        schemaFiles = [(x,'') for x in glob.glob(wildcard)]
        code, tag = d.menu('Schema selection',
                           choices=schemaFiles+[
                               (chDir, '('+os.getcwd()+')'),
                               (chWildcard, '('+wildcard+')')])
    
        if code == Dialog.CANCEL:
            return
    
        if tag == chWildcard:
            code, tag = d.inputbox('Wildcard',init = wildcard)
            if code == Dialog.OK:
                wildcard = tag
            continue
    
        if tag == chDir:
            code, tag = d.dselect(os.getcwd())
            if code == Dialog.OK:
                dirMngr.changeDir(tag)

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


