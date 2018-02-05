#!/usr/bin/python3

#
# Purpose: Read SPEC files and generate a .DOT file that describes dependencies among them.
#          IMPORTANT: requires Python3
# Author: fmontorsi
# Creation: June 2017
#


from pyrpm.spec import Spec, replace_macros
import getopt, sys, os


version_indicator=[ '=', '>=', '>', '<', '<=' ]

def before(value, a):
    # Find first part and return slice before it.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    return value[0:pos_a]

def clean_require_field( str ):
    for verind in version_indicator:
        if verind in str:
            str = before(str, verind)
            
    str = str.replace("(x86-32)","")
    str = str.replace("-","_")
    str = str.replace("(","")
    str = str.replace(")","")
    str = str.replace(".","")
    str = str.replace(",","")
    str = str.replace("%{","")
    str = str.replace("}","")
    return str.strip()


def process_all_specs( specfiles ):
    """Parses given list of RPM spec files and generates a list in the form
         [
           [ a, b ]
           [ b, c ]
           ...
         ]
       indicating that RPM "a" depends from RPM "b". RPM "b" depends from "c" etc.
    """
    
    output_digraph = []
    
    for specfilename in specfiles:
        print('Processing spec file: ' + specfilename)
        spec = Spec.from_file(specfilename)
 
        all_cleaned_reqs = []
        for req in spec.requires:
            cleaned_req = []
            for pkgname in req.split(','):
                cleaned_req.append(clean_require_field(pkgname))
            #print('req tranformed [{}] -> [{}]'.format(req, cleaned_req))
            all_cleaned_reqs = all_cleaned_reqs + cleaned_req

        #print('All requirements are: {}'.format(all_cleaned_reqs))
        for req in all_cleaned_reqs:
            output_digraph.append([ clean_require_field(spec.name), req ])

    return output_digraph


def generate_dot_file(outputfile, digraph):
    print('Generating DOT file: {}'.format(outputfile))
    of = open(outputfile,'w')
    of.write("digraph Dependencies {\n")
    for pair in output_digraph:
        of.write( pair[0] + " -> " + pair[1] + "\n")
    of.write("}\n")
        
def usage():
    print('Usage: %s [--help] --output=somefile.dot <spec files> ...' % sys.argv[0])
    print('  [-h] --help            (this help)')
    sys.exit(os.EX_USAGE)
    
def parse_command_line():
    """Parses the command line
    """
    try:
        opts, remaining_args = getopt.getopt(sys.argv[1:], "ho", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(os.EX_USAGE)

    outputdot = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-o", "--output"):
            outputdot = a
        else:
            assert False, "unhandled option"

    if outputdot == "":
        print("Please provide --output option")
        sys.exit(os.EX_USAGE)

    return {'spec_files': remaining_args, 
            'outputdot' : outputdot }


##
## MAIN
##

if __name__ == "__main__":
    config = parse_command_line()
    output_digraph = process_all_specs(config['spec_files'])
    generate_dot_file(config['outputdot'], output_digraph)