# collect addr of every 
# 
# stwu r1, ... 
# mflr r0
#
# That is not already prepended by an address label

# python3 ./collectFuncs.py <file>


import argparse
import subprocess

# remove any one of the provided prefixes from str
def remove_prefix(str, *prefixes):
    for pf in prefixes:
        if str.startswith(pf):
            return str[len(pf):]
    return str

# locate a function prologue
def is_stwu(instr):
    return instr[0] == "94" and instr[1] == "21"
def is_mflr(instr):
    return instr[0] == "7C" and instr[1] == "08" and instr[2] == "02" and instr[3] == "A6"
    
parser = argparse.ArgumentParser()
parser.add_argument("file", 
                help="path to .s assembly file to be searched for missing function declarations")
args = parser.parse_args()

# list of {addr, code} where code is 'a' for add label or 'r' for replace label.
addrs = []
stwu_addr = ""
is_labeled = False
found_stwu = False
label = ""

with open(args.file, "r") as f:
    for line in f:
        if ":" in line:
            label = line.split(":")[0]
            is_labeled = True # next instruction is already labeled
        elif "/*" in line:
            instruc = line.split()[3:7]
            if is_stwu(instruc):
                found_stwu = True
                stwu_addr = line.split()[1]
            elif is_mflr(instruc):
                if found_stwu:
                    if is_labeled and label.startswith("lbl_"):
                        addrs.append({'addr':stwu_addr, 'code':'r'})
                    elif not is_labeled:
                        addrs.append({'addr':stwu_addr, 'code':'a'})
            else:
                is_labeled = False
                found_stwu = False
  
for a in addrs:
    addr = a['addr']
    cd = a['code']
    replace_func_cmd = "sed -i '0,/lbl_" + addr + ":/{s/lbl_" + addr + ":/\\n.global func_" + addr + "\\nfunc_" + addr + ":/}' " + args.file
    add_func_cmd = "sed -i '0,/\/\* " + addr + "/{s/\/\* " + addr + "/\\n.global func_" + addr + "\\nfunc_" + addr + ":\\n\/\* " + addr + "/}' " + args.file
    if cd == 'a':
        print("add func_" + addr)
        subprocess.run(add_func_cmd, shell=True)
    elif cd == 'r':
        print("replace lbl_" + addr)
        subprocess.run(replace_func_cmd, shell=True)
