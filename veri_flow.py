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
    flow = re.split(r", | |,", flow)
    
    flow_table = {}
    single_flow = {}
    count = 0       # flow#
    for elem in flow:
        if elem.find("=") == -1:
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


def _verification(xmldict, flow_table, count):
    attr = []
    try:
        address = xmldict['cookie']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['table_id']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['priority']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['vlan-match']['vlan-id']['vlan-id']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['vlan-pcp']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ethernet-match']['ethernet-source']['address']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ethernet-match']['ethernet-destination']['address']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ipv4-source']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ipv4-destination']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ip-match']['ip-dscp']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['ip-match']['ip-ecn']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['tcp-source-port']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    try:
        address = xmldict['match']['tcp-destination-port']
    except KeyError:
        attr.append(0)
    else:
        attr.append(1)
    for i in range(count):
        if attr[0] == 1:
            if flow_table[i]['cookie'] != hex(int(xmldict['cookie'])):
                continue
        if attr[1] == 1:
            if flow_table[i]['table'] != xmldict['table_id']:
                continue
        if attr[2] == 1:
            if flow_table[i]['priority'] != xmldict['priority']:
                continue
        if attr[3] == 1:
            if flow_table[i]['dl_vlan'] != xmldict['match']['vlan-match']['vlan-id']['vlan-id']:
                continue
        if attr[4] == 1:
            if flow_table[i]['dl_vlan_pcp'] != xmldict['match']['vlan-pcp']:
                continue
        if attr[5] == 1:
            if flow_table[i]['dl_src'] != xmldict['match']['ethernet-match']['ethernet-source']['address']:
                continue
        if attr[6] == 1:
            if flow_table[i]['dl_dst'] != xmldict['match']['ethernet-match']['ethernet-destination']['address']:
                continue
        if attr[7] == 1:
            address = xmldict['match']['ipv4-source']
            address = address[:address.find('/')]
            if flow_table[i]['nw_src'] != address:
                continue
        if attr[8] == 1:
            address = xmldict['match']['ipv4-destination']
            address = address[:address.find('/')]
            if flow_table[i]['nw_dst'] != address:
                continue
        if attr[9] == 1:
            a = int(flow_table[i]['nw_tos'])
            b = int(xmldict['match']['ip-match']['ip-dscp'])
            if  a != 4 * b:
                continue
        if attr[10] == 1:
            if flow_table[i]['nw_ecn'] != xmldict['match']['ip-match']['ip-ecn']:
                continue
        if attr[11] == 1:
            if flow_table[i]['tp_src'] != xmldict['match']['tcp-source-port']:
                continue
        if attr[12] == 1:
            if flow_table[i]['tp_dst'] != xmldict['match']['tcp-destination-port']:
                continue

        action = xmldict['instructions']['instruction']['apply-actions']['action']['output-action']['output-node-connector']
        try:
            t = int(action)
        except ValueError:
            if action == "INPORT":
                if flow_table[i]['actions'] != "IN_PORT":
                    continue
            else:
               if flow_table[i]['actions'] != action:
                    continue
        else:
            if flow_table[i]['actions'] != "output:" + str(t):
                continue
        return "correct"
    return "error"
