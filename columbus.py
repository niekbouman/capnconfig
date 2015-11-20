#! /usr/bin/env python

import locale
from dialog import Dialog

import sys
import capnp
#import configfile_capnp

import operator
# This is almost always a good thing to do at the beginning of your programs.
locale.setlocale(locale.LC_ALL, '')

# You may want to use 'autowidgetsize=True' here (requires pythondialog >= 3.1)
d = Dialog(dialog="dialog")
# Dialog.set_background_title() requires pythondialog 2.13 or later
d.set_background_title("Captain Config: Cap'n Proto Explorer")
# For older versions, you can use:
#   d.add_persistent_args(["--backtitle", "My little program"])

# In pythondialog 3.x, you can compare the return code to d.OK, Dialog.OK or
# "ok" (same object). In pythondialog 2.x, you have to use d.DIALOG_OK, which
# is deprecated since version 3.0.0.

floatTypes = ['float32','float64']
integralTypes = ['uint8','uint16','uint32','uint64','int8','int16','int32','int64']

'''
def descr(node):
    return {
        bool: lambda x: str(x),
        str:  lambda x: x,
        dict: lambda x: str(x),
        long: lambda x: str(x),
        type(None): lambda x: str(None)
            }[type(node)](node)
'''

def fieldTypeAsString(field):
    '''Determine the type of the field'''
    try:
        return field.schema.node.which()
    except (capnp.KjException,AttributeError) as e:
        return field.proto.slot.type.which() #to_dict().keys()[0]

'''
def doInit(node, fieldname):
    return
    ftype = fieldTypeAsString(node.schema.fields[fieldname])
    if ftype == 'text':
        getattr(node,fieldname)
    elif ftype == 'struct':
        getattr(node,'init')(fieldname)
'''

def abbreviate(obj):
    s = str(obj)
    if len(s) > 10:
       s = s[:10]+'...' 
    return s
     
def handlestruct(node):

    while True:

        # if named union
        if len(node.schema.non_union_fields) == 0:
            (code,tag) = d.radiolist('Union',choices = [(x,'',True if i==0 else False) for i,x in enumerate(node.schema.union_fields)])
            if code == Dialog.CANCEL:
                return 
                #if fieldTypeAsString(node.schema.fields[tag]) == 'void':
                #    setattr(node,tag,None)
                #getattr(node,'init')(tag)
            handletype(node,tag,setInit = False)
            return

        (code, tag) = d.menu('Traverse struct', ok_label='Modify',cancel_label='Exit',choices = [(name,abbreviate(getattr(node,name))) for name in node.schema.fieldnames])

        if code == Dialog.CANCEL:
            return 

        handletype(node,tag)



        #allItems = node.schema.fieldnames
        #initializedItems = node.to_dict().keys()

        #notyetInitialized = set(allItems).difference(set(initializedItems))
        #for fieldname in notyetInitialized:
        #    doInit(node,fieldname)


        #print node.schema.fieldnames
        #print node.to_dict()

        #choices = [(name,descr(node.to_dict()[a])) for name in node.schema.fieldnames])
def inputField(node,tag,datatype,setInit=True):
    stringRepr = str(datatype).split("'")[1]
    (code,inp) = d.inputbox('Set %s field' % stringRepr, init = str(getattr(node,tag) if setInit else ''))
    if code == Dialog.OK:
        try:
            setattr(node,tag, datatype(inp))
        except capnp.KjException:
            d.msgbox('Illegal value')
        except ValueError:
            d.msgbox('Please enter a %s value' % stringRepr)



def handletype(node,tag,setInit = True):
    field = node.schema.fields[tag] 

    fieldtype = fieldTypeAsString(field)

    if fieldtype == 'enum':

        sortedItems = sorted(field.schema.enumerants.items(),key=operator.itemgetter(1))

        (code,enumerant) = d.radiolist('Select enumerant', choices = [(x[0],'@'+str(x[1]),True if x[0] == getattr(node,tag) else False) for x in sortedItems])
        setattr(node,tag, enumerant)

    elif fieldtype == 'bool':
        (code,tf) = d.radiolist('Select boolean', choices = [(str(x),'',getattr(node,tag)==x) for x in [True,False]])
        val = True if tf == 'True' else False
        setattr(node,tag, val)

    elif fieldtype == 'text':
        (code,string) = d.inputbox('Set text field', init = getattr(node,tag))
        if code == Dialog.OK:
            setattr(node,tag, string)

    elif fieldtype == 'struct':
        handlestruct(getattr(node,tag))

    elif fieldtype in floatTypes:
        inputField(node,tag,float,setInit)

    elif fieldtype in integralTypes:
        inputField(node,tag,int,setInit)

    elif fieldtype == 'void':
        setattr(node,tag,None)

    elif fieldtype == 'list':
        print 'list'
        exit()

    else:
        print fieldtype
        exit()


    #print tmp
    #exit()
    #return configfile_capnp.Configuration.new_message(**tmp)
                
#(code, path) = d.fselect(sys.path[0] + '/')
#userschema = capnp.load(str(path))

#while True:


#userschema = capnp.load('configfile.capnp')
userschema = capnp.load('simple.capnp')
(code,root) = d.menu('Select root struct', choices = [(x.name,'') for x in userschema.schema.node.nestedNodes])

msg = getattr(userschema, root).new_message()

#dct = msg.to_dict()

#msg = getattr(userschema, root).new_message(**dct)

#msg = configfile_capnp.Configuration.new_message()
#msg = userschema.Configuration.new_message()

handlestruct(msg)

print msg.to_dict()
    #if code == Dialog.CANCEL:
    #    break

    #handletype(msg,tag)

#d.treeview('test',nodes =[(a,a,True if i==0 else False,1) for i,a in enumerate(configfile_capnp.Configuration.schema.fieldnames)])

#(code, tag) = d.menu('test',choices =[(a,str(msg.to_dict()[a]) if type(msg.to_dict()[a]) in [str,bool] else '') for i,a in enumerate(msg.schema.fieldnames)])





#configfile_capnp.Configuration.


exit() 

if d.yesno("Are you REALLY sure you want to see this?") == d.OK:
    d.msgbox("You have been warned...")

    # We could put non-empty items here (not only the tag for each entry)
    code, tags = d.checklist("What sandwich toppings do you like?",
                             choices=[("Catsup", "",             False),
                                      ("Mustard", "",            False),
                                      ("Pesto", "",              False),
                                      ("Mayonnaise", "",         True),
                                      ("Horse radish","",        True),
                                      ("Sun-dried tomatoes", "", True)],
                             title="Do you prefer ham or spam?",
                             backtitle="And now, for something "
                             "completely different...")
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        pass
else:
    code, tag = d.menu("OK, then you have two options:",
                       choices=[("(1)", "Leave this fascinating example"),
                                ("(2)", "Leave this fascinating example")])
    if code == d.OK:
        # 'tag' is now either "(1)" or "(2)"
        pass
