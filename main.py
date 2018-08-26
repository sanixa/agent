import os
import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import veri_flow as flow
TEMPFILE = "temp.xml"
USERNAME = "admin"
PASSWORD = "admin"
ODL_HOST = "localhost"
########xml node id need check#######################
##########flow._verification new check###########

def xml(filename, col, content):
    ET.register_namespace('',"urn:opendaylight:flow:service")
    tree = ET.ElementTree(file=filename)
    for elem in tree.iter():
        if elem.tag == "{urn:opendaylight:flow:service}node":
            elem.attrib={"xmlns:inv":"urn:opendaylight:inventory"}
        if elem.tag == "{urn:opendaylight:flow:service}" + col:
            elem.text = content
    global TEMPFILE
    tree.write(TEMPFILE)
    with open(TEMPFILE, "r+") as f:
        content = f.read()
        f.seek(0,0)
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n" + content)

def xml2(filename, col1, col2, content):  #col1 out col2 in
    ET.register_namespace('',"urn:opendaylight:flow:service")
    tree = ET.ElementTree(file=filename)
    bo = 0
    for elem in tree.iter():
        if elem.tag == "{urn:opendaylight:flow:service}node":
            elem.attrib={"xmlns:inv":"urn:opendaylight:inventory"}
        if bo == 1 and elem.tag == "{urn:opendaylight:flow:service}" + col2:
            elem.text = content
            bo = 0
        if elem.tag == "{urn:opendaylight:flow:service}" + col1:
            bo = 1
    global TEMPFILE
    tree.write(TEMPFILE)
    with open(TEMPFILE, "r+") as f:
        content = f.read()
        f.seek(0,0)
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n" + content)

def modifity(key,action):
    xml("add.xml", key, action)
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
    fid = flow._flow_id(xdict, ftable, count)
    if fid == -1:
        print "error"
    result = flow._verification(xdict, ftable, fid)
    print result

def no_modifity(key,action):
    xml("add.xml", key, action)
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
    if ftable == "":
        print "correct"
    fid = flow._flow_id(xdict, ftable, count)
    if fid == -1:
        print "correct"
    else:
        print "error"

def modifity_2l(key1, key2, action):
    xml2("add.xml", key1, key2, action)
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
    fid = flow._flow_id(xdict, ftable, count)
    if fid == -1:
        print "error"
    result = flow._verification(xdict, ftable, fid)
    print result

def no_modifity_2l(key1, key2,action):
    xml2("add.xml", key1, key2, action)
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
    os.system(command)

    xdict = flow._xml2dict(TEMPFILE)
    ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
    if ftable == "":
        print "correct"
    fid = flow._flow_id(xdict, ftable, count)
    if fid == -1:
        print "correct"
    else:
        print "error"

def switch(arg):
    os.system("ovs-vsctl add-br my-br")
    s = "ovs-vsctl set bridge my-br other-config:datapath-id=" + str(arg)
    os.system(s)

    s = "ovs-vsctl show > temp"
    os.system(s)
    f = open('temp', 'r')
    for line in f:
        if line.find("my-br") != -1:
            return "y"
    return "n"

def no_switch(dpid):
    s = "ovs-vsctl del-br my-br"
    os.system(s)

    s = "ovs-vsctl show > temp"
    os.system(s)
    f = open('temp', 'r')
    for line in f:
        if line.find("my-br") != -1:
            return "n"
    return "y"

def active(act):
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    if act == "True": 
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
        fid = flow._flow_id(xdict, ftable, count)
        if fid == -1:
            print "error"
        result = flow._verification(xdict, ftable, fid)
        print result
    elif act == "False":
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
        if ftable == "":
            print "correct"
        fid = flow._flow_id(xdict, ftable, count)
        if fid == -1:
            print "correct"
        else:
            print "error"
    else:
        print("input error")

def no_active(act):
    global TEMPFILE,USERNAME,PASSWORD,ODL_HOST
    if act == "True":      
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:remove-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
        if ftable == "":
            print "correct"
        fid = flow._flow_id(xdict, ftable, count)
        if fid == -1:
            print "correct"
        else:
            print "error"        
    elif act == "False":
        command = "curl -X POST -H \"Content-Type: application/xml\" -d @" + TEMPFILE + " --user "+USERNAME+":"+PASSWORD+" http://" + ODL_HOST + ":8080/restconf/operations/sal-flow:add-flow"
        os.system(command)

        xdict = flow._xml2dict(TEMPFILE)
        ftable,count = flow._flow_data('ovs-ofctl dump-flows my-br')
        fid = flow._flow_id(xdict, ftable, count)
        if fid == -1:
            print "error"
        result = flow._verification(xdict, ftable, fid)
        print result
    else:
        print("input error")


def main():
    cmd = "dst-mac"
    arg = "12:34:56:65:43:21"
    if cmd == "switch":
        switch(arg)
    elif cmd == "no switch":
        no_switch(arg)
    elif cmd == "action":
        modifity("output-node-connector",arg)
    elif cmd == "no action":
        no_modifity("output-node-connector",arg)
    elif cmd == "active":
        active(arg)
    elif cmd == "no active":
        no_active(arg)
    elif cmd == "cookie":
        modifity("cookie",arg)
    elif cmd == "no cookie":
        no_modifity("cookie",arg)
    elif cmd == "dst-ip":
        modifity("ipv4-destination",arg)
    elif cmd == "no dst-ip":
        no_modifity("ipv4-destination",arg)
    elif cmd == "dst-mac":
        modifity_2l("ethernet-destination", "address",arg)
    elif cmd == "no dst-mac":
        no_modifity_2l("ethernet-destination", "address",arg)
    else:
        pass
if __name__ == "__main__":
    main()
