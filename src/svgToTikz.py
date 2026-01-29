# A python utility for using svg2tikz in the way we want
# Usage: Add the current directory to $PYTHONPATH
# run the script on a file:
# python3 -m svgToTikz <filename>
# output is a file with .tex extension in .

import svg2tikz
import sys
import re

# options for the command line https://xyz2tex.github.io/svg2tikz/cmdlineguide.html
# options for editing text size and style throughout file https://stackoverflow.com/questions/2237979/how-to-control-font-sizes-in-pgf-tikz-graphics-in-latex

filename = sys.argv[1]

fontsize = None
#try:
#    fontsize = int( sys.argv[2] )
#except IndexError:
#    pass
# gadget_attempt_3.svg: 72 for the edge gadget figure
# reduction_supporting_figs.svg: 32 
# monorbigon_cases.svg: 42
# perm_rep_example.svg and perm_rep_local.svg: 10 #but I did it manually afterward, first I set it to None
# lifts_crossing_domain3.svg: 10
# 8^3_2labels_degree.svg and the other 5: 30
# gadgets_around_graph_2.svg: 50
# gadget_segments... :16
# opts.svg, subopts.svg: 18 #and other snappy ones on the order of that example
# opts_numeric.svg: 20
# front_page_lattice: 16
# tricky_subcase.svg: 50
# milnordoodle.svg: 25
# unicorn_annulus.svg: 35
# dualbouquet_v2.svg: 12
# torus1, torus2, torus3: 20
# torus0: 30
# torus_half: 30


#simplepin figs
# graph_reduction.svg: 12
# 12_56^3: 20
# main_reduction_example: 18
# edge_gadget_bundle.svg: 18
# triloopbigon.svg: 18
# tooth.svg: 30
# all plumbing figures: 16
# edge_gadgets: 36
# triloopsinkandsource, trilooptographexample: 18

#print( filename, type( filename ) )

#print( fontsize , "hI")

f = open( filename, 'r')
toConvert = "<svg"+f.read().split( "<svg", 1)[1]

#print( toConvert)
f.close()
f = open( filename.split(".")[0]+".tex", 'w')
#codeoutput="figonly" gives the tikz picture only
#codeoutput="standalone" gives a standalone file
toWrite = svg2tikz.convert_svg(toConvert, ids=['1', '2', 'id2'], verbose=True, codeoutput="figonly", t="math")

#print( "yo")
#print( "writing", toWrite )

#bold all the text in the tikz
#splt = toWrite.split( "\\begin{tikzpicture}[",1)
#toWrite = splt[0]+"\\begin{tikzpicture}[font=\\bf,"+splt[1]

# hack it to proper math mode since the convert function isn't doing it correctly
toWrite = re.sub( "\\\\\$", "$", toWrite ) #fix escaped dollar signs
toWrite = re.sub( "\\\\\{", "{", toWrite ) #fix escaped curly brackets
toWrite = re.sub( "\\\\\}", "}", toWrite ) #fix escaped curly brackets
toWrite = re.sub( "\{\}", "", toWrite ) #kill empty curly brackets
toWrite = re.sub( "\\\\\_", "_", toWrite ) #fix escaped underscores
toWrite = re.sub( "\\\\\^", "^", toWrite ) #fix escaped tildes
toWrite = re.sub( "\$\\\\backslash\$", "\\\\", toWrite ) #fix this annoying thing

#print( toWrite )

# all text must be on its own layer or this won't work. or maybe it will anyway idk
# also don't group the text

fontsize = 18
if fontsize is not None:
    insert = "\\tikzstyle{{every node}}=[font=\\fontsize{{{}}}{{{}}}\\selectfont]".format( fontsize, fontsize )
else:
    insert = ""
splt = toWrite.split("%text",1)
if len( splt ) > 1:
    toWrite = splt[0]+insert+"\n%text"+splt[1]

f.write( toWrite )
f.close()