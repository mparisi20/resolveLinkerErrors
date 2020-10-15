# resolveLinkerErrors.py rewrite using grep, find, and sed
# github.com/mparisi20

# usage: resolveLinkerErrors.py <error_file> <asm_dir>


import argparse
import subprocess

# remove any one of the provided prefixes from str
def remove_prefix(str, *prefixes):
    for pf in prefixes:
        if str.startswith(pf):
            return str[len(pf):]
    return str

parser = argparse.ArgumentParser()
parser.add_argument("error_file", 
                    help="path to text file containing the mwldeppc.exe error output")
parser.add_argument("asm_dir", 
                    help="path to directory containing the .s assembly files to be searched to resolve the linker errors")
args = parser.parse_args()

addrs = set()

with open(args.error_file, "r") as f:
    error_lines = f.readlines()
    for line in error_lines:
        if "undefined:" in line:
            addrs.add(remove_prefix(line.split()[-1].strip("\'"), "lbl_", "func_"))

for addr in addrs:
    grep_cmd = "egrep -r \(lbl\|func\)_" + addr + ": " + args.asm_dir
    replace_func_cmd = "find " + args.asm_dir + " -type f -exec sed -i 's/\(func_\|lbl_\)" + addr + ":/\\n.global \\1" + addr + "\\n\\1" + addr + ":/g' {} \\;"
    add_func_cmd = "find " + args.asm_dir + " -type f -exec sed -i 's/\/\* " + addr + "/\\n.global func_" + addr + "\\nfunc_" + addr + ":\\n\/\*" + addr + "/g' {} \\;"
 
    result = subprocess.run(grep_cmd, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
    if result == '':
        print("add func_" + addr)
        subprocess.run(add_func_cmd, shell=True)
    else:
        print("replace (lbl_|func_)" + addr)
        subprocess.run(replace_func_cmd, shell=True)
