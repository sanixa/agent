import subprocess
import os
import json
import types
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from xml2dic import XmlDictConfig

def _xml2dict(filename):
    tree = ET.ElementTree(file=filename)
    for elem in tree.iter():
        elem.tag = elem.tag[31:]
        if isinstance(elem.tag,str):
            elem.tag = elem.tag.decode('utf-8')
        if isinstance(elem.text,str):
            elem.text = elem.text.decode('utf-8')
    root = tree.getroot()
    xmldict = XmlDictConfig(root)
    return xmldict
    


def _flow_data(cmd):
    flow = os.popen(cmd).read() #"ovs-ofctl dump-flows s1"
    if flow.find("cookie") == -1:
        return "",0
    flow = flow[flow.find("cookie"):]
    flow = flow[:len(flow)-1]
    temp = flow.splitlines()
    length = 0
    for i in temp:
        s = i[i.find("actions"):len(i)]
        s = s.replace(",","|")
        flow = flow[:i.find("actions") + length] + s + flow[len(i) + length + 1:]
        length += len(i)
    flow = flow.replace("\n",",")
    flow = flow.replace(",ip,",",")
    flow = flow.replace("send_flow_rem","")
    flow = re.split(r", | |,", flow)
    
    flow_table = {}
    single_flow = {}
    count = 0       # flow#
    for elem in flow:
        if elem == "":
            continue
        temp = elem.split("=")
        if temp[0] == "actions":
            single_flow.update({temp[0]:temp[1]})
            flow_table.update({count:single_flow})
            count += 1
            single_flow = {}
        else:
            single_flow.update({temp[0]:temp[1]})
    return flow_table,count

def _flow_id(xmldict, flow_table, count):
    fid = -1        
    for i in range(count):
        temp_l = []
        flow_l = [flow_table[i]['cookie'],flow_table[i]['priority'],flow_table[i]['table']]
        if 'cookie' in xmldict:
            temp_l.append(hex(int(xmldict['cookie'])))
        else:
            temp_l.append(hex(0))
        if 'priority' in xmldict:
            temp_l.append(xmldict['priority'])
        else:
            temp_l.append(int(0))
        if 'table_id' in xmldict:
            temp_l.append(xmldict['table_id'])
        else:
            temp_l.append(int(0))
        if temp_l == flow_l:
            fid = i
        temp_l = []
    return fid

def _flow_id_u(xmldict, flow_table, count):
    fid = -1        
    for i in range(count):
        temp_l = []
        flow_l = [flow_table[i]['cookie'],flow_table[i]['priority'],flow_table[i]['table']]
        if 'cookie' in xmldict['updated-flow']:
            temp_l.append(hex(int(xmldict['updated-flow']['cookie'])))
        else:
            temp_l.append(hex(0))
        if 'priority' in xmldict['updated-flow']:
            temp_l.append(xmldict['updated-flow']['priority'])
        else:
            temp_l.append(int(0))
        if 'table_id' in xmldict['updated-flow']:
            temp_l.append(xmldict['updated-flow']['table_id'])
        else:
            temp_l.append(int(0))
        if temp_l == flow_l:
            fid = i
        temp_l = []
    return fid

def _verification(xmldict, flow_table, fid):
    result = "correct"
    action = xmldict['instructions']['instruction']['apply-actions']['action']['output-action']['output-node-connector']
    try:
        address = xmldict['match']['ethernet-match']['ethernet-source']['address']
    except KeyError:
        pass
    else:
        if address != flow_table[fid]['dl_src']:
            result = "error"
    
    try:
        address = xmldict['match']['ethernet-match']['ethernet-destination']['address']
    except KeyError:
        pass
    else:
        if address != flow_table[fid]['dl_dst']:
            result = "error"
    
    try:
        address = xmldict['match']['ipv4-source']
    except KeyError:
        pass
    else:
        if address.find('/') != -1:
            address = address[:address.find('/')]
        if address != flow_table[fid]['nw_src']:
            result = "error"

    try:
        address = xmldict['match']['ipv4-destination']
    except KeyError:
        pass
    else:
        if address.find('/') != -1:
            address = address[:address.find('/')]
        if address != flow_table[fid]['nw_dst']:
            result = "error"

    try:
        i = int(action)
    except ValueError:
        if action == "INPORT":
            if flow_table[fid]['actions'] != "IN_PORT":
                result = "error"
        else:
           if flow_table[fid]['actions'] != action:
                result = "error"
    else:
        if flow_table[fid]['actions'] != "output:" + str(i):
            result = "error"

    return result

def _verification_u(xmldict, flow_table, fid):
    result = "correct"
    action = xmldict['updated-flow']['instructions']['instruction']['apply-actions']['action']['output-action']['output-node-connector']
    try:
        address = xmldict['updated-flow']['match']['ethernet-match']['ethernet-source']['address']
    except KeyError:
        pass
    else:
        if address != flow_table[fid]['dl_src']:
            result = "error"
    
    try:
        address = xmldict['updated-flow']['match']['ethernet-match']['ethernet-destination']['address']
    except KeyError:
        pass
    else:
        if address != flow_table[fid]['dl_dst']:
            result = "error"
    
    try:
        address = xmldict['updated-flow']['match']['ipv4-source']
    except KeyError:
        pass
    else:
        if address.find('/') != -1:
            address = address[:address.find('/')]
        if address != flow_table[fid]['nw_src']:
            result = "error"

    try:
        address = xmldict['updated-flow']['match']['ipv4-destination']
    except KeyError:
        pass
    else:
        if address.find('/') != -1:
            address = address[:address.find('/')]
        if address != flow_table[fid]['nw_dst']:
            result = "error"

    try:
        i = int(action)
    except ValueError:
        if action == "INPORT":
            if flow_table[fid]['actions'] != "IN_PORT":
                result = "error"
        else:
           if flow_table[fid]['actions'] != action:
                result = "error"
    else:
        if flow_table[fid]['actions'] != "output:" + str(i):
            result = "error"

    return result


