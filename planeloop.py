"""
 Title: planeloop.py
 Authors: Christopher-Lloyd Simon and Ben Stucky
 Description: Computes pinning sets of loops in the plane and sphere
 Github: https://github.com/ChristopherLloyd/LooPin

 Important info for other users:

 This program is intended to be loaded/run from within sage
 using the command:

 load( 'planeloop.py' )

 It will not work as a standalone python script,
 except from the python environment bundled with sage.
 to override this (for example if only using functions
 which use snappy), uncomment the line below."""

from sage.all import *

"""All imported python packages must be installed in the python environment
 that sage uses. For instance you need to run:

 sage -pip install snappy

 or

 sage -pip install snappy_15_knots  # Larger version of HTLinkExteriors

 to be able to use snappy.
 
 If you previously installed SnapPy into SageMath and want to upgrade SnapPy to the latest version, do:

 sage -pip install --upgrade snappy"""

# Get the needed imports

from random import *
import traceback #used for warnings/debugging
import warnings #used for warnings/debugging
import snappy #used for plotting knots and links
import os #used for removing temp files
import shutil #used for removing temp files
from subprocess import call #used for running external scripts
#import pylatex as p

# Currently unused imports:

#import lightrdf
#import gzip
#import rdflib
#import re
#from math import sqrt
#import timeit

# Global constants

ALPHABET = "abcdefghijklmnopqrstuvwxyz"*5 # generator alphabet, used for readable output only. Inverses are upper case

# SOME OF OUR FAVORITE LOOPS FOR TESTING

#8 crossing loop with no embedded monorbigons
link8 = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
        (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]

# a 9 crossing example
link9 = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
        (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
        (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

#mona lisa loop:
monalisa = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
        (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
        (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
        (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]

# Main

def main():
    
    createCatalog()
    #plotLoopWithLabeledRegions( link8 )

"""def plotLoopWithLabeledRegions( link, adjDict, minPinSets ):

    # Create the loop drawing and tweak parameters
    drawnPD = plinkPD( link )
    print( "PD code:", drawnPD )
    G = SurfaceGraphFromPD( plinkPD( link ) )
    print( G )
    LE = snappy.Link( link ).view()
    LE.style_var.set('pl')
    LE.set_style()
    c = LE.canvas
    corners = {}
    crosses = {}
    LE.info_var.set(1)
    LE.update_info()

    # store coordinates of all crossings
    for crs in LE.Crossings:
        crs.locate()
        strandCount = len( LE.Crossings )*2
        hit1 = abs( crs.hit1 )
        hit2 = abs( crs.hit2 )
        next1 = (hit1-1)%strandCount
        if next1 == 0:
            next1 = strandCount
        next2 = (hit2-1)%strandCount
        if next2 == 0:
            next2 = strandCount

        regs = set()
        adjStrands = {hit1,hit2,next1,next2}
        
        for strand in adjStrands:
            regs.add( G.adjDict[strand][0] )
            regs.add( G.adjDict[strand][1] )

        crosses[(crs.x,crs.y)]={"strands":{hit1,hit2,next1,next2}, "segs":None, "regs":regs }
        #crossCoordDict[ abs( crs.hit1 ) ] = (crs.x, crs.y)
        #crossCoordDict[ abs( crs.hit2 ) ] = (crs.x, crs.y)

    # store coordinates of all corners and the segments that crosses and corners belong to
    for a in LE.Arrows:
        a.expose()
        segs = a.find_segments( LE.Crossings, include_overcrossings=True )
        toAdd = []
        for i in range( len( segs )-1 ):
            if (segs[i][2],segs[i][3]) != (segs[i+1][0],segs[i+1][1]):
                midx = (segs[i][2]+segs[i+1][0])/2
                midy = (segs[i][3]+segs[i+1][1])/2
                toAdd.append( [segs[i][2],segs[i][3],midx,midy] )
                toAdd.append( [midx,midy,segs[i+1][0],segs[i+1][1]] )
        segs += toAdd
            
        for seg in segs:
            closeData = closeTo(seg[0],seg[1],crosses)
            if not closeData[0]:
                if (seg[0],seg[1]) not in corners:
                    corners[(seg[0],seg[1])] = {0:seg,1:None,"strand":None,"regs":None}
                else:
                    corners[(seg[0],seg[1])][1]=seg
            else:
                if crosses[closeData[1]]["segs"] is None:
                    crosses[closeData[1]]["segs"] = [seg]
                else:
                    crosses[closeData[1]]["segs"].append( seg )
            closeData = closeTo(seg[2],seg[3],crosses)
            if not closeData[0]:
                if (seg[2],seg[3]) not in corners:
                    corners[(seg[2],seg[3])] = {0:seg,1:None,"strand":None,"regs":None}
                else:
                    corners[(seg[2],seg[3])][1]=seg
            else:
                if crosses[closeData[1]]["segs"] is None:
                    crosses[closeData[1]]["segs"] = [seg]
                else:
                    crosses[closeData[1]]["segs"].append( seg )


    # compute the strands adjacent to each cross and corner
    for (x,y) in crosses:
        #assert( len( crosses[(x,y)]['segs'] ) == 4 )       
        for segOut in crosses[(x,y)]['segs']:
            hitCorners = set()
            (curx, cury) = (x,y)
            curSeg = segOut
            if (segOut[0],segOut[1])==(curx,cury):
                (nextx,nexty) = (segOut[2],segOut[3])
            else:
                (nextx,nexty) = (segOut[0],segOut[1])
            if (nextx,nexty) not in corners or corners[(nextx,nexty)]['strand'] is not None:
                continue
            while True:
                closeData = closeTo(nextx,nexty,crosses)
                if closeData[0]:
                    (nextx,nexty)=closeData[1]
                    break
                hitCorners.add((nextx,nexty))
                seg1 = corners[(nextx,nexty)][0]
                seg2 = corners[(nextx,nexty)][1]
                inFirst = False
                if (curx,cury) == (seg1[0],seg1[1]) or (curx,cury) == (seg1[2],seg1[3]):
                    inFirst = True
                if inFirst:
                    curSeg = corners[(nextx,nexty)][1]
                else:
                    curSeg = corners[(nextx,nexty)][0]
                (curx,cury) = (nextx,nexty)
                if (curSeg[0],curSeg[1]) == (curx,cury):
                    (nextx,nexty) = (curSeg[2],curSeg[3])
                else:
                    (nextx,nexty) = (curSeg[0],curSeg[1])
            strandNum = None
            for label in crosses[(x,y)]['strands']:
                if label in crosses[(nextx,nexty)]['strands']:
                    strandNum = label
            for corner in hitCorners:
                corners[corner]['strand'] = strandNum
                corners[corner]['regs'] = set( G.adjDict[strandNum] )

        

    #for (x,y) in corners:        
    #    assert( corners[(x,y)][1] is not None )


    # associate boundary coordinates to regions
    regBoundaries = {}
    randomCorner = getKey(corners)
    minX = randomCorner[0]
    maxX = randomCorner[0]
    minY = randomCorner[1]
    maxY = randomCorner[1]
    for dct in [corners,crosses]:
        for coord in dct:
            for reg in dct[coord]['regs']:
                if reg not in regBoundaries:
                    regBoundaries[reg] = {"coords":[coord],"topLeft":None, "bottomLeft":None,"infRegion":False}
                else:
                    regBoundaries[reg]["coords"].append( coord )
            if coord[0] < minX:
                minX = coord[0]
            if coord[0] > maxX:
                maxX = coord[0]
            if coord[1] < minY:
                minY = coord[1]
            if coord[1] > maxY:
                maxY = coord[1]


    # compute anchor points for labels and label regions
    tolerance = 0.000001
    for reg in regBoundaries:
        debugReg = None            
        topLeft = regBoundaries[reg]["coords"][0]
        bottomLeft = regBoundaries[reg]["coords"][0]
        regMinX = topLeft[0]
        regMaxX = topLeft[0]
        regMinY = topLeft[1]
        regMaxY = topLeft[1]
        for point in regBoundaries[reg]["coords"]:
            if point[0] < regMinX:
                regMinX = point[0]
            if point[0] > regMaxX:
                regMaxX = point[0]
            if point[1] < regMinY:
                regMinY = point[1]
            if point[1] > regMaxY:
                regMaxY = point[1]
            #if reg == debugReg:
            #    c.create_text(point[0],point[1],text='o', fill="black", font=('Helvetica 15 bold'))
            if point[0] < topLeft[0] - tolerance or ( abs( point[0]-topLeft[0] ) < tolerance and point[1] < topLeft[1] ):
                
                topLeft = point

            if point[0] < bottomLeft[0] - tolerance or ( abs( point[0]-bottomLeft[0] ) < tolerance and point[1] > bottomLeft[1] ):
                
                bottomLeft = point
        regBoundaries[reg]["topLeft"] = [topLeft]
        regBoundaries[reg]["bottomLeft"] = [bottomLeft]        

        if abs( minX-regMinX ) < tolerance and abs( minY-regMinY ) < tolerance \
           and abs( maxX-regMaxX ) < tolerance and abs( maxY-regMaxY )<tolerance:
            regBoundaries[reg]["infRegion"] = True

        if not regBoundaries[reg]["infRegion"]:
            c.create_text(topLeft[0]+10,topLeft[1]+20,text=reg, fill="black", anchor="w", font=('Helvetica 10 bold'))
        else:
            c.create_text(bottomLeft[0]+10,bottomLeft[1]+20,text=reg, fill="black", anchor="w", font=('Helvetica 10 bold'))
        
    return
     
    
def closeTo( x0, y0, pointDict, tolerance = 0.00000001 ):
    point1 = getKey( pointDict )
    mindist = abs( x0 - point1[0] )+abs( y0 - point1[1] )
    closestPoint = (point1[0], point1[1])
    for point in pointDict:
        nextd = abs( x0 - point[0] )+abs( y0 - point[1] )
        if nextd < mindist:
            mindist = nextd
            closestPoint = (point[0], point[1])
    return mindist < tolerance, closestPoint"""
    

def makeTex( loopStrings, imageFilesToDelete ):
    filename = "tex/pinSets"
    try:
        os.remove(filename+".tex")
        os.remove(filename+".pdf")
    except FileNotFoundError:
        pass
    f = open( filename+".tex", 'w' )
    preamble = "\\documentclass{article}%\n"+\
               "\\usepackage[T1]{fontenc}%\n"+\
               "\\usepackage[utf8]{inputenc}%\n"+\
               "\\usepackage{lmodern}%\n"+\
               "\\usepackage{textcomp}%\n"+\
               "\\usepackage{lastpage}%\n"+\
               "\\usepackage{geometry}%\n"+\
               "\\usepackage{tikz}\n"+\
               "\\usepackage{tkz-graph}\n"+\
               "\\usepackage{tkz-berge}\n"+\
               "\\usetikzlibrary{arrows,shapes}\n"+\
               "\\usepackage[matrix,arrow,curve,cmtip]{xy}\n"+\
               "\\usepackage{svg}\n"+\
               "\\usepackage{multicol}\n"+\
               "\\usepackage{float}\n"+\
               "\\geometry{tmargin=1cm,lmargin=1cm}%\n"+\
               "%\n%\n%\n"
    doc = preamble + "\\begin{document}%\n\\small\n\n"#note the font size change
    
    for loopString in loopStrings:
        doc += loopString

    doc += "\n\\end{document}"
    f.write( doc )
    f.close()
    call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"])
    try:
        os.remove(filename+".aux")
        os.remove(filename+".log")
        for file in imageFilesToDelete:
            os.remove(file)
        shutil.rmtree( "svg-inkscape/" )
    except FileNotFoundError:
        pass
    return    

def texPinSet(col1, col2, plinkImg, posetImg):
    """Generating and viewing a TeX file illustrating pinning sets"""
    

    doc = "\\begin{multicols}{2}\n"
    doc += col1+"\n"
    doc += "\\columnbreak\n\n"
    doc += col2+"\n"
    doc += "\\end{multicols}\n\n"
    
    #from sage.misc.latex import latex_examples     
    #foo = latex_examples.diagram()
    #doc += "\n\n"+latex( foo )
    #doc += "\\begin{sdfj}" #deal with a compilation error
    #doc += "\\includesvg[width=30pt]{"+plinkImg+"}\n\n"

    doc += "\\begin{multicols}{2}\n"
    doc += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\includesvg[width=250pt]{"+plinkImg+"}\n"+\
           "\\caption{Snappy loop plot.}\n"+\
           "\\label{fig:"+plinkImg+"}\n\\end{figure}"
    doc += "\\columnbreak\n\n"
    doc += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\includegraphics[scale=1]{"+posetImg+"}\n"+\
           "\\caption{Minimal join semilattice of pinning sets.}\n"+\
           "\\label{fig:"+posetImg+"}\n\\end{figure}"
    doc += "\\end{multicols}\\newpage"

    return doc    
    
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
def posetPlot( sageObject, heights, colors, vertlabels, edgeColors ):
    """A workaround function for getting a sage object to show via matplotlib
    since sageObject.plot() does not produce visible output when run from script"""
    p = sageObject.plot( layout = "ranked",\
                         vertex_colors = colors, edge_thickness = 2,
                         edge_style = "-", heights = heights, vertex_labels = vertlabels,
                         edge_colors = edgeColors)
    filename = getUnusedFileName( "png" )
    p.save( filename )
    #img = mpimg.imread( filename )
    #plt.imshow(img)
    #plt.show()
    #os.remove(filename)
    return filename

def drawLattice( pinSets, minPinSets, fullRegSet ):
    elts = minJoinSemilatticeContaining( minPinSets )
    eltsDict = {}
    rels = []
    for subset in elts:
        eltsDict[elts.index( subset )] = subset
    for i in range( len( elts )-1):
        for j in range( i+1, len( elts ) ):
            if eltsDict[i].issubset( eltsDict[j] ):
                rels.append([i,j])
            if eltsDict[j].issubset( eltsDict[i] ):
                rels.append([j,i])

    M = JoinSemilattice((eltsDict, rels))
    print( M )

    heightsDict = {}
    for elt in M.list():
        try:
            heightsDict[len( eltsDict[elt] )].append( elt )
        except KeyError:
            heightsDict[len( eltsDict[elt] )] = [elt]
    minColor = (0,1,0)
    vertColorsDict = {minColor:[]}
    for elt in M.list():
        if eltsDict[elt] in minPinSets:
            vertColorsDict[minColor].append( elt )
    vertLabels = {}
    for elt in M.list():
        vertLabels[elt]=str( len( eltsDict[elt] ) )
    edgeColorsDict = {}
    for rel in rels:
        pass
    #print( M.hasse_diagram() )
    G = DiGraph( M.hasse_diagram() )

    edgeColors = {}
    #A dictionary specifying edge colors:
    #    each key is a color recognized by matplotlib, and each corresponding value is a list of edges.
    diffs = {0}
    
    for edge in G.edges():
        diff = len( eltsDict[edge[1]] )-len( eltsDict[edge[0]] )
        if diff not in diffs:
            diffs.add( diff )

    #print( diffs )

    maxdiff = max(diffs)

    for edge in G.edges():
        
        diff = len( eltsDict[edge[1]] )-len( eltsDict[edge[0]] )
        #print( edge, eltsDict[edge[1]], eltsDict[edge[0]], diff )
        #print( diff, maxdiff )
        try:
            edgeColors[(0,0,diff/maxdiff)].append( edge )
        except KeyError:
            edgeColors[(0,0,diff/maxdiff)] = [edge]
        
        
        #G.set_edge_label(edge[0], edge[1], "green")
        #edge = (edge[0], edge[1], "blue" )
        #edge[2] = "blue"

    #print( G.edges( labels=True) )

    G = Graph( G )
               
    return posetPlot( G, heightsDict, vertColorsDict, vertLabels, edgeColors )

    
    """
    subsets = {}
    pset1 = list( powerset( fullRegSet ) )
    pset = []
    for elt in pset1:
        pset.append( set( elt ) )
    rels = []
    for subset in pset:
        subsets[pset.index( subset )] = set( subset )
    for i in range( len( pset )-1):
        for j in range( i+1, len( pset ) ):
            if subsets[i].issubset( subsets[j] ):
                rels.append([i,j])
            if subsets[j].issubset( subsets[i] ):
                rels.append([j,i])

    L = LatticePoset((subsets, rels))
    #pinSetDict = {}
    minPinSetDict = {}
    #for elt in pinSets:
    #    pinSetDict[pset.index( elt )] = elt
    for elt in minPinSets:
        minPinSetDict[pset.index(elt)] = elt

    print( "Finished creating full subset lattice." )
    M = L.subjoinsemilattice(minPinSetDict)
    # A faster way to do this would be to compute unions manually
    # Then construct using JoinSemiLattice
    print( "Finished creating the smallest join semilattice containing the minimal pinning sets." )
    #P = L.sublattice(minPinSetDict) #sublattice is extremely slow for 9-crossing link
    #print( "Finished creating full sublattice generated by pinnings sets." )
    print( M )

    
    
    def printData( functions ):
        nonlocal M
        for function in functions:
            try:
                func = eval( "M."+function )
                print( str( func ).split()[2], func() )
            except AttributeError:
                print( traceback.print_exc() )
 
    functions = ["is_planar", "breadth", "is_join_pseudocomplemented",\
                "is_supersolvable", "skeleton",\
                "center", "vertical_decomposition", "subdirect_decomposition"]
    
    #printData( functions )
    #frattini_sublattice()

    #print( M.hasse_diagram )
    #print( M.list() )
    heightsDict = {}
    for elt in M.list():
        try:
            heightsDict[len( subsets[elt] )].append( elt )
        except KeyError:
            heightsDict[len( subsets[elt] )] = [elt]
    #print( heightsDict )
    colorsDict = {"green":[]}
    for elt in M.list():
        if subsets[elt] in minPinSets:
            colorsDict["green"].append( elt )
    vertLabels = {}
    for elt in M.list():
        vertLabels[elt]=str( len( subsets[elt] ) )
    posetPlot( Graph( M.hasse_diagram() ), heightsDict, colorsDict, vertLabels )
    

    
    return"""
    """
    # What's below was plotting the Join Semi Lattice from ALL pinning sets
        
    #elms = pinSets
    pinSetDict = {}
    minPinSetDict = {}
    # set of vertices needs to be hashable
    for elt in pinSets:
        pinSetDict[pset.index( elt )] = elt
    for elt in minPinSets:
        minPinSetDict[pset.index(elt)] = elt
    
    #print( pinSets )
    rels = []
    # it seems you have to give sage the relations between elements manually
    for i in range( len( pinSets )-1):
        for j in range( i+1, len( pinSets ) ):
            if pinSetDict[i].issubset( pinSetDict[j] ):
                rels.append([i,j])
            if pinSetDict[j].issubset( pinSetDict[i] ):
                rels.append([j,i])
    M = JoinSemilattice((pinSetDict, rels))
    #L = LatticePoset( M )
    
    #print( "M.is_planar():", L.is_planar() )
    #print( "M.join_matrix()", L.join_matrix() )
    
    sageplot( M )
    # Trying to get subjoinsemilattice generated by minimal pinning sets, having issues
    #L = M.subjoinsemilattice(minPinSetDict)
    #L = sage.combinat.posets.lattices.FiniteJoinSemilattice( M )
    #L = L.sublattice(minPinSetDict)
    #sageplot( L )"""

def minJoinSemilatticeContaining( subsets ):
    """This function takes a set of subsets and computes unions
    to find the minimal join semilattice containing it"""

    fullUnion = set()
    for elt in subsets:
        fullUnion = fullUnion.union( elt )
    #fullIntersection = fullUnion.copy()
    #for elt in subsets:
    #    fullIntersection = fullIntersection.intersection( elt )    

    #print( fullUnion )
    #print( fullIntersection )
    #rels = []

    #def downSets( sets, atoms ):
        #print( "downsets sets:", sets )
    #    if sets == [fullIntersection]:
    #        return None
    #    else:
    #        setsD = []
    #        for elt1 in sets:
    #            for elt2 in atoms:
    #                cap = elt1.intersection( elt2 )
    #                if cap not in setsD:
    #                    setsD.append( cap )
    #        if setsD == sets:
    #            return None
    #        else:
    #            return setsD

    def upSets( sets, atoms ):
        if sets == [fullUnion]:
            return None
        else:
            setsU = []
            for elt1 in sets:
                for elt2 in atoms:
                    cup = elt1.union( elt2 )
                    if cup not in setsU:
                        setsU.append( cup )
            if setsU == sets:
                return None
            else:
                return setsU

    allsets = subsets.copy()
    #nextD = subsets
    nextU = subsets
    while True:        
        #if not (nextD is None):            
        #    for elt in nextD:
        #        if not elt in allsets:
        #            allsets.append( elt )
        #    nextD = downSets( nextD, subsets )
        if not (nextU is None):            
            for elt in nextU:
                if not elt in allsets:
                    allsets.append( elt )
            nextU = upSets( nextU, subsets )
        else:
            break

    return allsets

def createCatalog():
    """Create the pdf catalog of loops, their minimal pinning sets, and their minimal join semilattice"""

    loops = ['8_3', '3_1', '4_1', '5_1', '8_3', '9_24', link8, link9, monalisa] # the loops to go in the catalog
    loopStrings = []
    toDelete = []
    for link in loops:
        drawnpd = plinkPD( link )
        optionaldollarsign = ""
        if type( link ) == str:
            optionaldollarsign = "$"
        col1 = "\\textbf{Input PD code or string to snappy (use to reproduce the drawing):}\n\n\t" \
             +optionaldollarsign + str( link )+optionaldollarsign+"\n\n"
        col1 += "\\textbf{Output PD code drawn by snappy:}\n\n\t"+str( drawnpd )+"\n\n\n"
        data = getPinSets( drawnpd, debug=False )
        col1 += "\\textbf{Arcs composing region <-----> Region key}\n\n"
        col1 += data["regInfo"]
        col2 = "\\textbf{Minimal pinning sets:}\n\n"
        minlen = len( data["minPinSets"] )
        for elt in data["minPinSets"]:
            col2 +=  "\\{"+str(elt) + "\\}\n\n"
            if len( elt ) < minlen:
                minlen = len( elt )
        col2 += "\n\n"
     
        col2 += "\\textbf{Number of minimal pinning sets:} "+str( len( data["minPinSets"] ) )+"\n\n"
        col2 += "\\textbf{Number of total pinning sets:} "+str( len( data["pinSets"] ) )+"\n\n"
        col2 += "\\textbf{Pinning number:} "+str( minlen )+"\n\n"
        tolerance = 0.0000001
        plinkFile = plinkImgFile( link, drawnpd, data["G"].adjDict, data["minPinSets"], tolerance )
        posetFile = drawLattice( data["pinSets"], data["minPinSets"], data["fullRegSet"] )
        toDelete.append( plinkFile )
        toDelete.append( posetFile )
        loopStrings.append( texPinSet(col1, col2, plinkFile, posetFile ) )

    makeTex( loopStrings, toDelete )
    #print( outputStr )
    #print( loopData )    

def getUnusedFileName( ext ):
    """Gets a filename in the current folder that is not in use with the extension str"""
    assert( type( ext ) == str )
    while True:
        filename = str( random() )+"temp."+ext
        try:
            f = open( filename, 'r' )
            f.close()
        except FileNotFoundError:
            break
    return filename    
    
####################### COMPUTING PINSETS ####################################
def testSi( link, pinSet, treeBase = 0, rewriteFrom = 0, verbose = False):
    """Returns si(gamma) relative to all pins, and si(gamma) relative to the pins in pinSet
    using a spanning tree from treeBase and rewriting rule from rewriteFrom"""
    if type( link ) == list:
        G = SurfaceGraphFromPD( link )
    else:
        G = SurfaceGraphFromPD( plinkPD( link ) )
    #print( set( G.wordDict.keys() ) )
    T = G.spanningTree( treeBase )
    T.createCyclicGenOrder()
    gamma = T.genProd()
    unPinSet = set( T.wordDict.copy().keys() ).difference( pinSet )
    rep, newRewriteFrom = T.reducedWordRep( gamma, unPinSet, source = rewriteFrom )
    return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
            "rep.si( T.orderDict )":rep.si( T.orderDict, verbose = verbose ), \
           "rep":rep, "newRewriteFrom":newRewriteFrom, \
            "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}

def getPinSets( link, minOnly = True, debug = False, treeBase = None, rewriteFrom = 0 ):
    """Returns the minimal pinning sets of a link"""
    if type( link ) == list:
        G = SurfaceGraphFromPD( link )
    else:
        G = SurfaceGraphFromPD( plinkPD( link ) )    
    
    T = G.spanningTree( baseRegion = treeBase )
    T.createCyclicGenOrder()
    gamma = T.genProd()
    #print( gamma )
    n = gamma.si( T.orderDict )

    #print( n )
    if debug:
        print( T )
        print()
    #plink( link )
    #print( T.wordDict )

    fullRegList = list( T.wordDict.copy().keys() )
    #fullRegList.sort()
    #fullRegDict = {}
    monorBigonSet = set()
    for key in T.wordDict:
        if len( G.wordDict[key] ) <= 2:
            monorBigonSet.add( key )
    #print( monorBigonSet )
    #return
    #i=0
    #for key in T.wordDict:
    #    fullRegDict[key]=i
    #    i+=1
    fullRegSet = set( fullRegList )
    numRegions = len( fullRegSet )
        
    #print( fullRegList )
    #print( type( fullRegSet ) )  

    def isPinning( regSet ):
        nonlocal rewriteFrom
        rep = T.reducedWordRep( gamma, fullRegSet.difference( regSet ), source = rewriteFrom )[0]
        return rep.si( T.orderDict ) == n        

    pinSets = []
    minPinSets = []
    #numPinSets = 0
    falseMins = {"superset":0,"subset":0 }

    def getPinSetsWithin( regSet, minIndex = 0):
        nonlocal pinSets
        nonlocal minPinSets
        #nonlocal numPinSets
        #nonlocal baseRegion
        #print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return False
        else:
            minimal = True
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                if fullRegList[i] in monorBigonSet:
                    continue
                nextSet.remove( fullRegList[i] )
                if getPinSetsWithin( nextSet, minIndex = i+1 ):
                    minimal = False
                nextSet.add( fullRegList[i] )
            if minimal:
                superset = False
                #subsetIndices = set()
                newPinsets = []
                for i in range( len( pinSets ) ):
                    if pinSets[i].issubset( nextSet ):
                        superset = True
                        falseMins["superset"] += 1 #just for benchmarking purposes
                        break
                    if debug:
                        #experimentally, this is not needed:
                        if not nextSet.issubset( pinSets[i] ):
                            newPinsets.append( pinSets[i] )

                #experimentally, this is not needed:
                if debug:
                    if len( newPinsets ) != len( pinSets ) and not superset:
                        falseMins["subset"] += 1 #just for benchmarking purposes
                        pinSets = newPinsets                
                
                if not superset:# or not minOnly:
                    #print( "Adding", nextSet )
                    minPinSets.append( nextSet )
            pinSets.append( nextSet )
            #numPinSets += 1
            return True

    """def getPinSetsWithinOld( regSet, minOnly = True, minIndex = 0):
        #print( "hi" )
        print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return set()
        else:
            minsWithin = []
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                nextSet.remove( fullRegList[i] )
                curmin = getPinSetsWithin( nextSet, minOnly = minOnly, minIndex = i+1 )
                nextSet.add( fullRegList[i] )
                if not curmin:
                    continue

                
                #print( "curmin:", curmin )
                #print()
                
                minimal = True
                for elt in minsWithin:
                    if elt.issubset( curmin ):
                        print( elt, curmin )
                        minimal = False
                if minimal:
                    #print( "Adding", curmin )
                    minsWithin.append( curmin )

                #print( "HELLLOOOO", minsWithin )

            if minsWithin == []:
                print( "regSet", regSet, "is minimal" )
                pinSets.append( nextSet )
                return regSet
            else:
                return minsWithin[0]"""

    def powerSetCheck( powerset ):
        nonlocal rewriteFrom
        """Naive O(exp) function for debugging purposes"""
        pinsets = []
        
        i = 0
        for subset in powerset( fullRegSet ):
            s = set( subset )
            if s == fullRegSet:
                continue
            rep = T.reducedWordRep( gamma, s, source = rewriteFrom )[0]
            if s != fullRegSet and rep.si( T.orderDict ) == n:
                pinsets.append( fullRegSet.difference( s ) )
            i+=1
        #print( "Total number of subsets:", i )
        return pinsets

    getPinSetsWithin( fullRegSet )#, minOnly = minOnly )

    naivePinSets = None

    if debug:# and not minOnly:
        #getPinSetsWithin( fullRegSet, minOnly = False )
        naivePinSets = powerSetCheck( powerset )
        print( "naivePinSets:", len( naivePinSets ) )
        print( "recursivePinsets:", len( pinSets ) )
        print( "#Naive\\Recursive=", len( difference( naivePinSets, pinSets ) ) )
        print( "#Recursive\\Naive=", len( difference( pinSets, naivePinSets ) ) )
        
        for elt in naivePinSets:        
            assert( elt in pinSets )
        for elt in pinSets:
            assert( elt in naivePinSets )
        assert( fullRegSet in pinSets )
    #if debug and minOnly:
        print( "Minimal Pinsets:", len( minPinSets ) )
        for i in range( len( minPinSets ) ):
            for j in range( len( minPinSets ) ):
                if i != j:
                    assert( not minPinSets[i].issubset( minPinSets[j] ) )
        #getPinSetsWithin( fullRegSet, minOnly = minOnly )
        #print( "minPinsets:", len( pinSets ) )

    #print( pinSets )
    #print( "False minimals sets:", falseMins )  
            
    #print( pinSets )
    #print()
    #print( naivePinSets )
    #if debug:# and not minOnly:
    #    return pinSets, naivePinSets, minPinSets

    return {"pinSets":pinSets, "naivePinSets":naivePinSets,\
            "minPinSets":minPinSets, "fullRegSet":fullRegSet,\
            "regInfo":G.regionInfo(), "G":G }
    

####################### DATA STRUCTURES ####################################

class SurfaceGraph:
    """Encodes a local embedding of an ideal graph in a punctured surface S
    via local order of edges around each puncture.
    Methods expect that the graph's edges connect punctures in S
    and that the complement is a disk."""
    
    
    def __init__( self, wordDict, adjDict = None ):
        """Assumes wordDict is dict of integers that can be cast to Words.
        Each Word specifies a cyclic order
        of edge labels encountered around the vertex (key) 
        In case wordDict data comes from a spanning tree of a dual graph to a loop in the plane,
        Raises an assertion error if the there are any isolated vertices.
        If wordDict is a list, will create a dictionary with keys corresponding to list
        indices."""

        # if wordDict is a list, cast to dictionary
        if type( wordDict ) == list:
            wordDict = listToDict( wordDict )
            
        # Create dictionary whose keys are positive indices corresponding to edge labels
        # and values are vertex labels [left, right] encountered when crossing this
        # edge in the positive direction (for orientable surfaces, left is index 0 and right is index 1)
        # For nonorientable surface, this choice is not well-defined, but adjDict still contains the
        # adjacency information

        if adjDict is None:
            self.adjDict = {}
        else:
            self.adjDict = adjDict        
        
        self.wordDict = {}        

        for key in wordDict:
            w = Word( wordDict[ key ] )
            w.cycReduce() # Cyclically reducing all words
            assert( len( w ) > 0 ) # Ruling out isolated vertices
            if adjDict is None:
                for letter in w.seq:
                    try:
                        self.adjDict[ abs( letter ) ] # check if key error
                    except KeyError:
                        self.adjDict[ abs( letter ) ] = [ None, None ]
                    finally:

                        # if this is a new label, put this vertex on left or right according to sign
                        if self.adjDict[ abs( letter ) ] == [ None, None ]:                        
                            self.adjDict[ abs( letter ) ][ not (sign( 0, letter)+1)//2  ] = key

                            # otherwise put it in the left over slot
                        elif self.adjDict[ abs( letter ) ][0] is None:
                            self.adjDict[ abs( letter ) ][0] = key
                        elif self.adjDict[ abs( letter ) ][1] is None:
                            self.adjDict[ abs( letter ) ][1] = key

                            # unless you've seen it twice already
                        else:
                            raise( "An edge label occured more than twice" )
                    
            self.wordDict[key]= w

        # Make sure the adjDict has no remaining None labels:
        for key in self.adjDict:
            assert( self.adjDict[key][0] is not None and self.adjDict[key][1] is not None ) # otherwise you've got hanging edges

        # These attributes are used to store a global cyclic order on generators and their inverses
        # How this is calculated depends on the topology of the graph
        self.order = None
        self.orderDict = None

    def spanningTree( self, baseRegion = None ):
        """Returns a new SurfaceGraph formed from a spanning tree of self.
        Computes tree via dfs from baseRegion"""
       
        if baseRegion is None:
            baseRegion = getKey( self.wordDict )

        #print( baseRegion )

        edgesToKeep = {}

        for edge, vert in self.dfs( curVert = baseRegion, spanningTree = True ):
            edgesToKeep[edge]=None

        adjDict = {}
        for key in self.adjDict:
            try:
                edgesToKeep[key]
                adjDict[key]=self.adjDict[key]
            except KeyError:
                pass

        wordDict = {}
        for key in self.wordDict:
            newWord = []
            for letter in self.wordDict[key].seq:
                try:
                    edgesToKeep[abs(letter)]
                    newWord.append( letter )
                except KeyError:
                    pass
            wordDict[key] = newWord

        return SurfaceGraph( wordDict, adjDict = adjDict )

    def genProd( self ):
        """Returns the word which is the product of all generators
        in the order they are stored in self.adjDict"""
        return Word( list( self.adjDict.keys() ) )       

    def createCyclicGenOrder( self ):
        """This function computes a consistent cyclic order on the set
        of generators and their inverses, if possible.
        Right now it only works as expected in case the graph is a tree
        with a planar embedding whose cyclic orientations at each vertex are consistent with the data given
        (all clockwise or all anticlockwise; else we risk value error or other unexpected behavior at (*) )
        And in this case the cyclic order is found by 'walking around the tree and reading edge labels' """

        order = []
        startVert = getKey( self.wordDict )
        curVert = startVert
        curEdge = self.wordDict[ curVert ].seq[0]
        while True:
            order.append( curEdge )
            curVert = self.adjDict[ abs( curEdge )  ][ (sign( 0, curEdge )+1)//2 ]
            curWord = self.wordDict[ curVert ].seq
            curEdge = curWord[ ( curWord.index( -curEdge ) + 1 ) % len( curWord ) ] # (*)
            if curVert == startVert:
                break

        # Check that we hit every edge twice to know if we are in a tree
        # If graph is disconnected or contains cycles, this is false
        assert( len( order ) == len( self.adjDict )*2 ) # Otherwise this isn't a tree

        #order.reverse() # walking around the tree clockwise vs anticlockwise shouldn't change si
        self.order = order
                
        # to optimize cross function, we create a dictionary that allows us to get the index
        # of an edge or its inverse in O(1) (the information we need to pass to the cross function)
        orderDict = {}
        for i in range( len( self.order ) ):
            orderDict[order[i]]=i
            
        self.orderDict = orderDict

    def reducedWordRep( self, w, filledPunctures, source = 0 ):
        """Given a word w representing a loop in the punctured surface S carrying self
        (so that w is a "cutting sequence" of edges), this method computes a canonical
        reduced representative of w relative to a vertex source in the surface
        with all punctures in the set filledPunctures filled in. The vertex source must not be an element
        of filledPunctures and is taken to be a random such vertex by default.
        Each filled-in puncture gives rise to a simple rewriting rule which eliminates
        one generator (the one corresponding to the edge which is 'upstream' from the vertex
        relative to the source), and the reduced representative is unique up to this choice."""

        assert( type( w ) == Word )
        assert( type( source ) == int )
        #assert( source >= 0 )
        #assert( source < len( self.wordList ) )
        assert( type( filledPunctures ) == set )
        #fillDict = {}
        for puncture in filledPunctures:
            assert( type( puncture ) == int )
            #assert( puncture >= 0 )
            #assert( puncture < len( self.wordList ) )
            #assert( w.seq != puncture )
            #fillDict[ puncture ] = None

        # make sure the source is a key in wordDict
        # but is not in filledPunctures
        choices = set( self.wordDict.keys() ).difference( filledPunctures )
        assert( choices != set() )
        if source not in choices:
            source = getKey( choices )

        #print( "Searching from:", source )
        
        #try:
        #    self.wordDict[source]
        #    print( "0 is a vertex" )
        #except KeyError:
        #    choices = set( self.wordDict.keys() ).difference( filledPunctures )
        #    assert( choices != set() )
        #    source = getKey( choices )
        #print( "hi" )
            

        copyword = w.copy()
        
        for edge, vert in self.dfs( curVert = source ):
            
            if vert in filledPunctures:
                #filledPunctures[ vert ] # skip if KeyError; puncture unfilled
                currWord = self.wordDict[ vert ]           
            
                currInv = ~currWord
                try:
                    ind = currWord.seq.index( edge )
                    word = currWord
                except ValueError:
                    ind = currInv.seq.index( edge )
                    word = currInv

                replWord = ~word.wslice( 0,ind ) / word.wslice( ind+1, len(word) )

                copyword = copyword.simpleRewrite( edge, replWord )
               
            #except KeyError:
            #    pass

        copyword.freeReduce()
        return copyword, source
    
    def dfs( self, curVert=0, spanningTree = True ):
        """Recursively generates a list of (edge, downsteam vertex) pairs via depth first search from a source vertex,
        where downstream vertex is the endpoint farther from the source,
        visited is a dictionary whose keys are edges that have already been visited, and values
        are terminal vertices to search from. curVert is the current vertex to search from.
        All edges in the resulting list are positive
        Unless spanningTree is set to to False, only returns pairs with edges
        from a spanningTree"""
    
        pairList = []

        try:
            self.wordDict[curVert]
        except KeyError:
            curvert = getKey( self.wordDict )

        def dfsHelper( data, curVert, visitedV, visitedE, spanningTree ):                
            for edge in data.wordDict[ curVert ].seq:
                try:
                    e = abs( edge )
                    visitedE[ e ]
                    # If you made it here, you have seen this edge already
                    # so do nothing
                    continue
                except KeyError:
                    # get the other vertex of e:         
                    otherVert = data.adjDict[ e ][ not data.adjDict[ e ].index( curVert ) ]
                    # if in spanningTree mode, only add the pair
                    # and make a recursive call if the other vertex isn't seen
                    if spanningTree:
                        try:
                            visitedV[ otherVert ]
                            # if you made it here, add this edge
                            # to prevent infinite loop and go next
                            # no recursive call
                            visitedE[ e ] =  None
                            continue                            
                        except KeyError:
                            visitedV[ otherVert ] = None
                            pairList.append(( e, otherVert))
                    else: # otherwise, add the pair unconditionally
                        visitedE[ e ] =  None
                        visitedV[ otherVert ] = None
                        pairList.append(( e, otherVert))
                    # make a recursive call if appropriate
                    dfsHelper( data, otherVert, visitedV, visitedE, spanningTree )
        dfsHelper( self, curVert, {curVert:None}, {}, spanningTree )

        return pairList

    def regionInfo( self ):
        toRet = ""
        for key in self.wordDict:
            toRet += "\\{"+str( binSet(key) )+ "\\} <-----> "+str(key)+"\n\n"
        return toRet
        

    def __str__( self ):
        
        toRet = "Local words around each vertex: \n"
        for key in self.wordDict:
            toRet += str( binSet(key) ) + " ("+str(key)+"): "\
                     + str( self.wordDict[ key ] ) + "\n"
        

        toRet += "\nEdge to [left,right] vertices: {"
        for key in self.adjDict:
            toRet += str( ALPHABET[ key - 1] )+ ": [" \
                + str( binSet( self.adjDict[ key ][0] ) )+", " \
                + str( binSet( self.adjDict[ key ][1] ) )+"], "
        toRet = toRet[:-2]+"}\n\nGlobal cyclic edge order: "
        if self.order is not None:
            toRet += str(Word( self.order ) )
            return toRet
        return toRet + "None computed"             

class Word:
    def __init__( self, seq ):
        """seq is a list nonzero integers.
        The absolute value is the index of the generator and the sign indicates
        \\pm 1 in the exponent"""
        # I feel like it might be better to use a linked list when we make the app
        # Depends on whether list slicing/gluing/shifting is O(1)
        assert( type( seq ) == list )
        for elt in seq:
            assert( type( elt ) == int )
            assert( elt != 0 )
        self.seq = seq

    def freeReduce( self ):
        """Find first reduction, remove it, and restart
        from the beginning of the word until reduced.
        Could be made more efficient by propogating
        outward before restarting. Complexity = O(n)
        Modifies self."""
        # I would like to rewrite this to use shifts and cycReduce
        reduced = False
        while not reduced:
            madeReduction = False
            for i in range( len( self.seq ) - 1 ):
                cur = self.seq[i]
                nxt = self.seq[i+1]
                if cur+nxt != 0:
                    #no reduction
                    continue
                else:
                    #reduce by slice and glue
                    self.seq = self.seq[:i]+self.seq[i+2:]
                    madeReduction = True
                    break
            if not madeReduction:
                reduced = True

    def cycReduce( self ):
        """Performs cyclic reduction by chopping off ends until cyclically reduced.
        Modifies self."""
        self.freeReduce()
        if len( self.seq ) == 0:
            return
        while True:
            if self.seq[0]+self.seq[-1] != 0:
                #no reduction
                break
            else:
                #chop off ends
                self.seq = self.seq[1:-1]

    def __mul__( self, other ):
        """Returns the product of two words as a new word. Call with self*other"""
        return Word( self.seq+other.seq )

    def __truediv__( self, other ):
        """Multiply self by other's inverse. Call with self/other"""
        return self*~other

    def __invert__( self ):
        """Returns the inverse word (call with ~self)"""
        revseq = []
        for i in range( len( self.seq ) - 1, -1, -1 ):
            revseq.append( -self.seq[i] )
        return Word( revseq ) 

    def __pow__( self, n):
        """Returns self**n"""
        assert( type( n ) == int )
        seq = []
        for i in range( abs( n ) ):
            if n > 0:
                seq += self.seq
            else:
                seq += ~self.seq
        return Word( seq )            

    def wslice( self, i, j, wrap = False ):
        """Returns a new word which is the subword which is the slice of self
        from i (inclusive) to j (exclusive).
        If wrap is False it behaves like list slice (empty if i>=j)
        If wrap is True and i >= j we slice cyclically
        In fact we obtain the ith shift with i=j"""
        assert( i >= 0 )
        assert( j >= 0 )
        assert( i <= len( self ) )
        assert( j <= len( self ) )
        if not wrap or i<j:
            return Word( self.seq[i:j] )
        else:
            return Word( self.seq[i:]+self.seq[:j] )

    def shift( self, i ):
        """Returns the cyclically shifted word conjugate to self whose first letter is
        the one at index i in w. Returns a new word and does not modify w"""
        return self.wslice( i, i, wrap = True )
    
    def naivePrimitiveRoot( self ):
        """Returns the pair (w, n) such that self = w^n AS FREE WORDS and n is maximal.
        In particular will not find the root of gw^ng^(-1) for nontrivial g"""
        for i in range( 1, len( self )//2+1 ):
            if len( self )%i == 0:
                seg = self.wslice(0,i)
                power = len( self )//i
                if pow( seg, power )==self:
                    return seg, power
        return self.copy(), 1
    
    def si( self, order, bypassCycReduce = False, verbose = False ):
        """Counts self intersections of self with respect to a global cylic order
        EXPECTS INPUT TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""
        rootself, powself = self.naivePrimitiveRoot()
        I = rootself.I( rootself, order, bypassCycReduce = bypassCycReduce, assumePrimitive = False, verbose = verbose )
        return powself**2*I//2+powself-1
    
    def I( self, other, order, bypassCycReduce = False, assumePrimitive = False, verbose = False ):
        """ Computes the geometric self intersection between self and other relative to
        a global cyclic order on generators and their inverses occuring in the word
        EXPECTS WORDS TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""        
        # could stand to add more preconditions
        assert( type( order) == dict )
        
        if not bypassCycReduce:
            self.cycReduce()
            other.cycReduce()
        else:
            warnings.warn( "WARNING: input may not be cyclically reduced")

        # compute primitive roots by default
        if not assumePrimitive:            
            rootself, powself = self.naivePrimitiveRoot()
            rootother, powother = other.naivePrimitiveRoot()
        else:
            rootself, powself = self, 1
            rootother, powother = other, 1

        if verbose:
            print( "Computing cross/val for each shift of", self, "along", other )
            print( "(powself=", powself, ", powother=", powother, ")" )
            print()
        
        # count intersections of primitive roots
        # can make this faster by skipping ahead if fellow travel is encountered
        # crossValDict = {}
        #indexDict = {}
        primCrossCount = 0
        shiftCount = 0
        i = 0
        while i < len( rootself ):
            j=0
            while j < len( rootother ):
                cross, valplus, valminus = rootself.crossval( rootother, order, i=i, j=j, verbose = verbose)
                val = abs( valplus ) + abs( valminus )
                #indexDict[(i,j)]={"cross":abs(cross),"valplus":abs(valplus),"valminus":abs(valminus)}
                #crossValDict[((i-abs(valminus))%len(rootself),(j-abs(valminus))%len(rootother),\
                #              (i+abs(valplus))%len(rootself),(j+abs(valplus))%len(rootother))] = abs( cross )
                if verbose:
                    print( " cross:", cross, "val:", val )
                    print()
                shiftCount += 1
                primCrossCount += abs( cross )/(1 + val)
                j+= 1#abs( val ) + 1
            i+=1

        if verbose:
            print( "Number of shifts for this computation:", shiftCount )
            print( "primCrossCount=", primCrossCount )
            print()
                
        return round( primCrossCount )*powself*powother

        # Experimenting with skipping ahead to avoid relying on
        # floating point division and get a speedup. It's not working so far.
        # I really don't understand why the crossValDict method here doesn't work
        #count = 0
        #for key in crossValDict:
        #    count += crossValDict[key]

        #return count*powself*powother

        #a smarter attempt (This one should actually be faster, but it's also not working):
            
        for key in indexDict.copy():
            if key in indexDict:
                for i in range( 1, indexDict[key]["valminus"]+1 ):
                    try:
                        del indexDict[((key[0]-i)%len(rootself),(key[1]-i)%len(rootother))]
                    except KeyError:
                        break #continue
                for i in range( 1, indexDict[key]["valplus"]+1 ):
                    try:
                        del indexDict[((key[0]+i)%len(rootself),(key[1]+i)%len(rootother))]
                    except KeyError:
                        break #continue
                if indexDict[key]["cross"] == 0:
                    del indexDict[key]

        count = 0
        for key in indexDict:
            count += indexDict[key]["cross"]

        #return count*powself*powother
        #return len( indexDict.keys() )*powself*powother

        #indexSet = {}
        #for i in range( len( rootself ) ):
        #    for j in range( len( rootother ) ):
        #        try:
                    
        #        indexSet[ (i,j) ] = None       
    
    def crossval( self, other, order, i=0, j=0, verbose = False ):
        """ Words must be cyclically reduced and positive length
        WORDS MUST BE CYCLICALLY REDUCED
        returns (cross, valplus, valminus) triple where cross is -1,0 or 1 (right hand rule from self+ to other+)
        and valplus, valminus are signed lengths of fellow traveling in forward/backward directions
        for convenience, (valplus,valminus) is set to (0,0) if periodisations are identical up to inverses """
        
        assert( len( self ) > 0 and len( other ) > 0 )
        
        # could make this marginally faster by not slicing unless i, j != 0?
        w1plus = self.shift( i )
        w1minus = ~w1plus

        w2plus = other.shift( j )
        w2minus = ~w2plus
        
        # define letters that are relevant to consider, p for positive and n for negative
        p1 = w1plus.seq[0]
        p2 = w2plus.seq[0]
        n1 = w1minus.seq[0]
        n2 = w2minus.seq[0]

        if verbose:
            print( "w1plus:", w1plus, "w1minus:", w1minus )
            print( "w2plus:", w2plus, "w2minus:", w2minus )        

        assert( p1 != n1 and p2 != n2 ) # this would contradict cyclic reduction
        
        initcross1 = cord( order[n1], order[n2], order[p1] )
        initcross2 = cord( order[n1], order[p2], order[p1] )
        initcross = initcross2 - initcross1
        
        if abs( initcross ) == 2: #cross is \pm 1; no fellow traveling
            return sign( 0, initcross ), 0, 0
        
        # otherwise check for fellow traveling
        if p1 == p2 or n1 == n2: # val>0
            plusdata = w1plus.initinfo( w2plus )
            minusdata = w1minus.initinfo( w2minus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #equal periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return int( initcross1 == initcross2 ), plusdata[0], minusdata[0]
        if p1==n2 or p2==n1:
        #else: # p1==n2 or p2==n1 #val <0
            plusdata = w1plus.initinfo( w2minus )
            minusdata = w1minus.initinfo( w2plus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #inverse periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return -int( initcross1 == initcross2 ), -plusdata[0], -minusdata[0]

        # if here, there is no fellow traveling, and they don't cross
        return 0, 0, 0        
            
    def initinfo( self, other ):
        """given two words, returns data about common initial segments of their periodisations
        as a quadruple (dist, letter1, letter2, letterprev)"""
        
        assert( len( self ) > 0 and len( other ) > 0 ) 
        
        threshold = len( self )+len( other )
        letter1 = self.seq[0]
        letter2 = other.seq[0]
        letterprev = -self.seq[-1] #ensures you return the right thing from crossval
        # if there is no fellow traveling in this direction, but there is in the opposite direction
        length = 0
        
        while letter1 == letter2:
            letterprev = -letter1
            letter1 = self.seq[ (length+1)%len( self ) ]
            letter2 = other.seq[ (length+1)%len( other ) ]
            length += 1
            if length > threshold: # These words share a root, 
                break # letter1 and letter2 will be equal so cross will be 0
        
        return length, letterprev, letter1, letter2

    def simpleRewrite( self, gen, repl ):
        """Iterates over self once, replacing each instance of gen with the Word repl
        and each instance of -gen with the inverse of repl.
        gen may be positive or negative
        Returns the new representative; does not modify self"""
        assert( type( repl ) == Word )
        assert( type( gen ) == int )
        assert( abs( gen ) > 0 )

        invRepl = ~repl

        wseq = []
        for letter in self.seq:
            if abs( letter )!= abs( gen ):
                wseq.append( letter )
            elif letter == gen:
                wseq += repl.seq
            else:
                wseq += invRepl.seq
        return Word( wseq )

    def copy( self ):
        """Returns a copy of self"""
        return Word( self.seq )

    def __eq__( self, other ):
        return self.seq == other.seq

    def __len__( self ):
        return len( self.seq )

    #def isTrivial():
    #    self.cycReduce()
    #    return len( self ) == 0

    def __str__( self ): #passing alphabet as kwarg is pointless
        if self.seq == []:
            return "{}"
        s = ""
        for elt in self.seq:
            try:
                letter = ALPHABET[ abs(elt) - 1 ]
            except IndexError as e:
                traceback.print_exc()
                raise Exception( e ) # bad alphabet
            assert ( letter.lower() != letter.upper() ) # bad alphabet
            if elt > 0:
                s += letter.lower()
            else:
                s += letter.upper()
        return s

####################### SNAPPY PD CODE WORKAROUNDS ####################################

# These functions are failing to capture the general behavior of how snappy messes with PD codes
# I can't figure out the exact relationship between input PD and output PD
def rawPDtoPlinkPD( link ):
    """Gets the PD code for a snappy link that is displayed when
    drawing the link using snappy.plink.
    Input can be a string or a list"""
    #assert( type( link ) == str )
    pd_in = snappy.Link( link ).PD_code()
    edgeLength = len(pd_in)*2
    pd_out = []
    for i in range( len( pd_in ) ):
        cycle = []
        for j in pd_in[i]:
            if j == 1:
                cycle.append( edgeLength )
            else:
                cycle.append( (j-1)%edgeLength )
        pd_out.append( cycle )
    return pd_out

def plinkPDtoRawPD( link ):
    """Gets the raw PD code associated to a plink PD (inverse of function above)"""
    #pd_in = snappy.Link( link ).PD_code()
    assert( type( link ) == list )
    edgeLength = len( link )*2
    pd_out = []
    for i in range( len( link ) ):
        cycle = []
        for j in link[i]:
            if j == edgeLength - 2:
                cycle.append( edgeLength )
            else:
                cycle.append( (j+2)%edgeLength )
        pd_out.append( cycle )
    return pd_out

def plinkPD( link ):
    """This function is a workaround to get the output PD code when plotting links
    with snappy from an input PD code. The reason it does external scripting
    and file I/O is a workaround for a known multithreading issue with snappy."""
    filename = getUnusedFileName( "txt" )
    call(['python3', 'plinkpd.py', str(link), filename])
    f = open( filename, 'r' ) # can wait here if plinkpd.py doesn't have enough time to write to file
    code = eval( f.read() )
    f.close()
    os.remove( filename )
    return code

# The functions below experiment with multithreading rather than subprocess.call
# to deal with the snappy multithreading issue
#from threading import Thread
#from queue import Queue
def plinkPDOld( link ):
    que = Queue()
    thread = Thread( target=lambda q, arg1: q.put( plinkPDHelper( arg1 ) ), args=(que, link ))
    thread.start()
    thread.join()
    code = que.get()
    return code
    #LE = snappy.Link( link ).view()
    #code = LE.PD_code()
    #LE.done()
    #return code

def plinkPDHelper( link ):
    LE = snappy.Link( link ).view()
    code = LE.PD_code()
    #LE.done()
    return code

def plinkFromStr( link ):
    assert( type( link ) == str )
    snappy.Link( link ).view()

def plinkFromPD( link ):
    assert( type( link ) == list )
    snappy.Link( link ).view()

def plinkImgFile( link, drawnpd, adjDict, minPinSets, tolerance ):
    filename = getUnusedFileName( "svg" )
    call(['python3', 'saveLoop.py', str(link), str(drawnpd), str(adjDict), str(minPinSets), str(tolerance), filename])
    return filename    

# Experimenting with drawing a loop and getting a PD code
# Silly multithreading nonsense makes what's below not work as intended
# Could still experiment with outsourcing to a separate script
#
def drawLoop():
    M = snappy.Manifold()
    #while str( M ) == "Empty Triangulation":
    input( "Draw loop and send to snappy. Press any key when finished." )
    # M.getPDcode() only works in Ben's custom snappy install (modified source code)
    return M.getPDcode()

####################### DATABASE/TRANSLATION FUNCTIONS ####################################

def SurfaceGraphFromPD( pd ):
    sigma = pd
    coordsDict = {}
    for i in range( len( sigma ) ):
        for j in range( len( sigma[i] ) ):
            try:
                coordsDict[ sigma[i][j] ].append( [i,j] )
            except KeyError:
                coordsDict[ sigma[i][j] ] = []
                coordsDict[ sigma[i][j] ].append( [i,j] )

    def regionFromCoords( coords ):
        startEdge = sigma[coords[0]][coords[1]]
        reg = [startEdge]
        #print( sigma[coords[0]][coords[1]] )
        while True:
            # depending on PD code convention, may need to
            # subtract or add from index here
            # to match clockwise/counterclockwise convention
            nextEdge = sigma[coords[0]][(coords[1]-1)%4 ]
            if nextEdge == startEdge:
                break
            reg.append( nextEdge )
            for cordChoice in coordsDict[nextEdge]:
                if coords[0] != cordChoice[0]:
                    coords = cordChoice
                    break
        return reg   

    #create dual graph 
    edgeDict = {}

    #print( pd )
    #print() 
    #print( coordsDict )

    # define left and right relative to the first segment
    # you want to start at the cycle containing 1 but not containing 2

    if coordsDict[1][0][0] == coordsDict[2][0][0] or coordsDict[1][0][0] == coordsDict[2][1][0]:
        curLeftCoords = coordsDict[1][0] 
        curRightCoords = coordsDict[1][1]
    else:
        curLeftCoords = coordsDict[1][1] 
        curRightCoords = coordsDict[1][0]   
    
    regDict = {}
    indexDict = {}

    for i in range( 1, len( sigma )*2+1 ): # this is the number of segments in the loop
        # we must check whether regions on left and right of this edge exist yet
        # make a choice for left and right based on the previous

        curLeftRegion = regionFromCoords( curLeftCoords )
        curRightRegion = regionFromCoords( curRightCoords )

        leftkey = binHash( curLeftRegion )
        rightkey = binHash( curRightRegion )
        
        try:
            regDict[leftkey]
        except KeyError:
            eltToIndex = {}
            for j in range( len(curLeftRegion) ):
                eltToIndex[curLeftRegion[j]] = j
            regDict[leftkey] = curLeftRegion
            indexDict[leftkey] = eltToIndex

        try:
            regDict[rightkey][indexDict[rightkey][i]] *= -1 # right region sees this edge negative
        except KeyError:
            eltToIndex = {}
            for j in range( len(curRightRegion) ):
                eltToIndex[curRightRegion[j]] = j
            regDict[rightkey] = curRightRegion
            indexDict[rightkey] = eltToIndex
            regDict[rightkey][indexDict[rightkey][i]] *= -1
        edgeDict[i] = [ leftkey , rightkey ]

        if i == len( sigma )* 2:
            break
        
        if sigma[curLeftCoords[0]] == sigma[ coordsDict[i+1][1][0] ] or sigma[curRightCoords[0]] == sigma[ coordsDict[i+1][0][0] ]:
            curLeftCoords, curRightCoords = coordsDict[i+1][0], coordsDict[i+1][1]
        else:
            curLeftCoords, curRightCoords = coordsDict[i+1][1], coordsDict[i+1][0]

    return SurfaceGraph( regDict, adjDict = edgeDict )
    
def readPlanarDiagram( knot ):
    """returns the planar diagram presentation of a knot with
    at most 11 crossings from Rolfsen/Hoste/Thistlethwaite tables.
    Knots under eleven crossings should be of the form 'x_y' for integers x
    and y. Knots with eleven crossings should be of the form 'Kxay' or Kxny'
    where the n or a stands for alternating or non-alternating."""
    
    assert( type( knot ) == str )
    notfound = "Knot '"+knot+"' not found in database."
    if ( len( knot ) < 3 ): #could pattern match here to save more time
        warnings.warn( notfound )
        return None 
    try:
        firstLetter = int( knot[0] )
    except ValueError:
        firstLetter = knot[0]
        if firstLetter != 'K': #could pattern match here to save more time
            warnings.warn( notfound )
            return None

    if type( firstLetter ) == int:
        file = 'knotdata/Rolfsen.rdf'
    else:
        file = 'knotdata/Knots11.rdf'

    f = open( file, 'r' )
    key = "<knot:"+knot+">"
    for line in f.readlines():
        data = line.split()[:2]
        if data[0]==key and data[1] == "<invariant:PD_Presentation>":
            f.close()
            data = line.split( "\"")[1].split("sub")
            sigma = []
            for i in range( 1, len( data ), 2 ):
                data[i] = data[i][1:-2]
                if "," in data[i]:
                    toAdd = []
                    for elt in data[i].split( "," ): 
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
                else:
                    toAdd = []
                    for elt in data[i]:
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
            
            return sigma
    f.close()
    warnings.warn( notfound )
    return None

####################### OTHER GENERALLY USEFUL FUNCTIONS ####################################

def randomWord( n, m, s = None ):
    """Returns a random (unreduced) word of length n on m generators. s is random seed"""
    a = []
    if s is not None:
        seed( a=s )
    for i in range( n ):
        a.append( (randint( 0,1 )*2-1)*randint( 1, m ) )
    return Word( a )

def sign(i,j):
    """Returns 1 if i<j, 0 if i=j, -1 if i>j"""
    return int(i!=j)*(int(i<j)*2-1)

def cord(i,j,k):
    """returns 1, -1, or 0 according to the cyclic order of i,j, and k in (-inf,inf)
    e.g. cord(-1,2,3)=cord(3,1,2)=1, cord(2,1,3)=-1, cord(2,2,3)=cord(3,3,3)=0
    works for any data types with '=' and '<' operators"""
    return sign(i,j)*sign(j,k)*sign(i,k)

def binHash( distinctNatList ):
    """Given a list A of distinct nonnegative integers, computes a large integer
    which encodes the elements present and serves as a hash key for the
    corresponding set of naturals+0
    WILL NOT WORK PROPERLY IF GIVEN LISTS OF NONDISTINCT INTEGERS."""

    hashkey = 0
    for elt in distinctNatList:
        hashkey += 2**elt
    return hashkey

def binSet( num ):
    """Returns set of indices where a binary number is nonzero"""
    indexSet = set()
    i = 0
    while num != 0:
        if num%2 != 0:
            indexSet.add( i )
        i += 1
        num >>= 1
    return indexSet    

def listToDict( a ):
    """Converts list to dictionary"""
    toRet = {}
    for i in range( len( a ) ):
        toRet[i] = a[i]
    return toRet

def getKey( a ):
    """Returns some key from a dictionary/set, or None if the dict/set is empty"""
    for key in a:
        return key
    return None

####################### FUNCTIONS WHICH SHOULD ONLY BE USED FOR DEBUGGING ####################################

def intersection( list1, list2 ):
    """Returns a list of all elements from list1 and list2"""
    toReturn = []
    for elt in list1:
        if elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def union( list1, list2 ):
    """Returns a list of elements from list1 or list2"""
    toReturn = []
    for elt in list1:
        if not elt in toReturn:
            toReturn.append( elt )
    for elt in list2:
        if not elt in toReturn:
            toReturn.append( elt )
    return toReturn
    

def difference( list1, list2 ):
    """Returns a list of all elements in list1 and not in list2"""
    toReturn = []
    for elt in list1:
        if not elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def isSubset( list1, list2 ):
    """Returns True if and only if every element of list1 is in list2"""
    return len( difference( list2, list1 ) ) == len( list2 ) - len( list1 )

from itertools import chain, combinations
def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    stolen from https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
    for a 'naive check' of the pinset function
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

####################### OLD/COMPLETED TESTS ####################################
def test10():
    """Another function to compute pinning sets of drawn loops"""

    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    #link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
    #        (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    #link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
    #        (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
    #        (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

    drawnpd = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( offset ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )

    minOnly = True
    debug = True
    pinsets = pinSets( drawnpd, debug = debug, minOnly = minOnly )
    if minOnly:
        print( "Minimal pinning sets:" )
    minlen = len( pinsets[0] )
    for elt in pinsets[0]:
        if minOnly or debug:
            print( elt )
        if len( elt ) < minlen:
            minlen = len( elt )
    #print( "MinOnly:", minOnly )
    print()
    if minOnly:
        print( "Number of minimal pinning sets:", len( pinsets[0] ) )
    print( "Number of total pinning sets:", pinsets[1] )
    print( "Pinning number:", minlen )
    print()
    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )
    #plinkFromPD( link )

def test9():
    """Debugging the 9-crossing loop having different behavior for different spanning trees"""
    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]
    drawnpd = plinkPD( link )

    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    base1 = 16898
    base2 = 270864
    # base2 is the infinite region, so we always try to rewrite from there
    # however the answer should not depend on spanning tree (specified by treeBase)
    print( "All pinsets rel treeBase=", base1, ":" )
    allpinsets1, naive1 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base1, rewriteFrom = base2 )
    print()
    
    print( "All pinsets rel treeBase=", base2, ":" )
    allpinsets2, naive2 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base2, rewriteFrom = base2 )
    print()
    
    print( "Min pinsets rel treeBase=", base1, ":" )
    minpinsets1 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base1, rewriteFrom = base2 )[0]
    print()
    
    print( "Min pinsets rel treeBase=", base2, ":" )
    minpinsets2 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base2, rewriteFrom = base2 )[0]
    print()

    print( "Min1 is subset All1?", isSubset( minpinsets1, allpinsets1 ) )
    print( "Min2 is subset All2?", isSubset( minpinsets2, allpinsets2 ) )
    print( "All1 is subset Naive1?", isSubset( allpinsets1, naive1 ) )
    print( "All2 is subset Naive2?", isSubset( allpinsets2, naive2 ) )
    print( "All1 cap Min2 is a subset of Min1", isSubset( intersection( allpinsets1, minpinsets2), minpinsets1 ) )
    print( "#Naive1\\(Min2 cup All1)", len( difference( naive1, union( minpinsets2, allpinsets1 ) ) ) )
    print( "#All1\\Naive1", len( difference( allpinsets1, naive1 ) ) )
    print( "#Naive1\\All1", len( difference( naive1, allpinsets1 ) ) )
    print( "#Min1\\#Min2:", len( difference( minpinsets1, minpinsets2 ) ) )
    print( "#Min2\\#Min1:", len( difference( minpinsets2, minpinsets1 ) ) )
    print( "#Min2\\#All1:", len( difference( minpinsets2, allpinsets1 ) ) )
    print( "#Min2\\#Naive1:", len( difference( minpinsets2, naive1 ) ) ) 

    print( "Discrepancies follow..." )
    print()

    badcount = 0
    for elt in naive2:
        # base2 is the infinite region, so we always try to rewrite from there
        dataBase1 = testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2 )
        dataBase2 = testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2 )
        #return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
        #    "rep.si( T.orderDict )":rep.si( T.orderDict ), \
        #   "rep":rep, "newRewriteFrom":newRewriteFrom, \
        #    "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}
        if dataBase1["gamma.si( T.orderDict )"] != dataBase1["rep.si( T.orderDict )"]\
           or dataBase2["gamma.si( T.orderDict )"] != dataBase2["rep.si( T.orderDict )"]:
            testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2, verbose = True )
            testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2, verbose = True )

            
            print( "Considering pinset:", elt, "(size", len(elt), ")" )
            print()
            print( "  Relative to treeBase=", base1, " and rewriteFrom=", dataBase1["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase1["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase1["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase1["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase1["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase1["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase1["T.order"]) )
            
            if base2 != dataBase1["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
    
            print()
            print( "  Relative to treeBase=", base2, " and rewriteFrom=", dataBase2["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase2["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase2["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase2["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase2["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase2["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase2["T.order"]) )
            if base2 != dataBase2["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
            
            print()
            badcount += 1
       
        #if :
        #    print( "Considering pinset:", elt )
            
        #    print()
        #    badcount += 1
    print( "Total discrepancies:", badcount )
    #print( "\nPinning sets in second not in first:" )
    #for elt in difference( pinsets2, pinsets1 ):
    #    print( "Considering pinset:", elt )
    #    print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
    #    print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
    #    print()

    return
    
    print( "Pinning sets in first not in second:" )
    for elt in difference( pinsets1, pinsets2 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()
    print( "\nPinning sets in second not in first:" )
    for elt in difference( pinsets2, pinsets1 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()

    # grab the pinset of size 4 that pins loop 2 but not loop 1
    #special = difference( pinsets2, pinsets1 )[1]
    #print(  )

    # double check that it doesnt pin loop1

def test8():
    """Demonstrates/tests for PD code discrepancy (originally with the Mona Lisa loop and 9 crossing loop.)
    Also illustrates 'correct' use of which PD to feed to snappy
    vs our algorithm"""


    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
            (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]
    # The algorithm is finding a consistent pinning poset for this loop
    #link= rawPDtoPlinkPD( link )

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

    
   
    drawnpd = plinkPD( link )
    #link.sort()
    #print( "original:", link )
    #print()

    #link1 = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( 2 ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )
        
        #link.sort()
        #print( i, ":", link )
    #   print()
       
    #return
    #print( rawPDtoPlinkPD( plinkPDtoRawPD( link ) ) )
    #print( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) )
    #print( plinkPDtoRawPD( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) ) )
    #print( rawPDtoPlinkPD( link ) )
    #print( rawPDtoPlinkPD( link ) )
    #plinkFromPD( link )
    #print( hackyPD( link ) )
    #plink( link1 )
    #return
    #link = '6_1'
    
    # the tests below all go faster than before
    #link = 'K14n1'
    #link = '10_24' # not showing minimal pinsets only? is computing ALL pinsets correctly by naive check
    #link = 'K11a340' #takes about 30 seconds to run
    #link = 'K11n100' #takes about a minute to run
    #pinSets( link, debug = True )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    
        pinsets = pinSets( drawnpd, debug = False )[0]#, treeBase = 270864 )#, rewriteFrom = 270864 )
        #print( pinsets )
        pinSetDict = {}
        minlen = len( pinsets[0] )
        print( "Minimal pinning sets:" )
        for elt in pinsets:
            try:
                pinSetDict[len(elt)]+=1
            except KeyError:
                pinSetDict[len(elt)] = 1
            print( elt )
            if len( elt ) < minlen:
                minlen = len( elt )
        print()
        print( "Number of minimal pinning sets:", len( pinsets ) )
        print( "Pinning number:", minlen )
        keys = list( pinSetDict.keys() )
        keys.sort()
        print( "Minimal pining sets by size:" )
        for key in keys:
           print( " Number of minimal pinning sets of size", key, ":", pinSetDict[key] )
        print()
        print( "PD_code offset:", i )
        print( "Input PD:", link )
        print( "Drawn PD:", drawnpd )
        print()

    #plinkFromPD( link )

def test7():
    link = '9_24'
    link = 'K11a340'
    G = SurfaceGraphFromPD( plinkPD( link ) )
    print()
    #print( G )
    T = G.spanningTree()
    T.createCyclicGenOrder()
    print( T )
    print()

    loop = T.genProd()

    print( "gamma", loop )
    print( "si(gamma):", loop.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564] )
    
    print( "gamma_{2564}", loop1) 
    print( "si(gamma_{2564}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754] )    
    print( "gamma_{2564,18754}", loop1) 
    print( "si(gamma_{2564,18754}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152] )    
    print( "gamma_{2564,18754,70152}", loop1) 
    print( "si(gamma_{2564,18754,70152}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138] )    
    print( "gamma_{2564,18754,70152,132138}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120] )    
    print( "gamma_{2564,18754,70152,132138,37120}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120,41088] )    
    print( "gamma_{2564,18754,70152,132138,37120,41088}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120,41088}):", loop1.si( T.orderDict ) )
    print()
    
    #snappy.Link( link ).exterior().plink()
    plink( link )
    print(  "PD code from the hacky function:", plinkPD( link ) )
    print()
    print( "PD code that snappy returns:", snappy.Link( link ).PD_code() )
    print()
    print( "PD code from rolfsen tables:", readPlanarDiagram( link ) )

def test6():
    #snappy sample usage
    #draw link from PD code (note that the PD code generated by snappy is different from this one)
    #M = snappy.Link( [[4, 2, 5, 1], [8, 3, 9, 4], [10, 6, 11, 5], [14, 7, 15, 8],
    #                  [2, 9, 3, 10], [16, 12, 17, 11], [20, 14, 21, 13], [6, 15, 7, 16],
    #                  [22, 18, 1, 17], [12, 20, 13, 19], [18, 22, 19, 21]] ).exterior().plink()
    #draw link from standard identifier string

    
    # get link from standard identifier string
    L = snappy.Link( '8_3' )

    # draw link ( can be annotated with PD code )    
    M = L.exterior()
    M.plink()
    
    #store and print PD_code
    pd = L.PD_code()
    print( pd )

    # can convert from manifold to link as follows:
    L1 = M.exterior_to_link()
    



def test5():
    

    diagram = readPlanarDiagram( "0_1" )
    print( diagram )
    diagram = readPlanarDiagram( "3_1" )
    print( diagram )
    diagram = readPlanarDiagram( "K11a1")
    PlaneTreeFromPlanarDiagram( diagram )
    return
    print( diagram )
    diagram = readPlanarDiagram( "8_3")
    print( diagram )
    PlaneTreeFromPlanarDiagram( diagram )
    return
    diagram = readPlanarDiagram( "K11a368" )
    print( diagram )


def test4():
    
    trefoil = SurfaceGraph( [[-1],[-3,1],[4,3,2],[-2],[-4]] )
    trefoil.createCyclicGenOrder()
    print( trefoil )
    w=Word( [1,2,3,4] ) #represents the trefoil loop
    w2 = Word( list( range( 1, 25 ))*3 )
    print( w2.naivePrimitiveRoot()[0], w2.naivePrimitiveRoot()[1] )
    #return
    w1 = trefoil.reducedWordRep( w, [] )
    print( pow(w1,4).I(pow( w1, 4 ),trefoil.orderDict ) )
    print( pow(w1,4).si( trefoil.orderDict ) )
    return
    w = Word( [1,4])
    v = Word( [3,1])
    
    print( w.crossval(v,trefoil.orderDict) )
                           

def test3():
    #G = SurfaceGraph( [[-1], [-3, 1], [3, 2, 4], [-2],[-4]] )
    #print( "\nEdge to [left,right] vertices:", G.adjDict, "}\nGlobal cyclic edge order: ", G.order )
    #G.createCyclicGenOrder()
    #print( "\n\nMore human readable: \n" )
    #print( G )

    G = SurfaceGraph( [[2],[6,5,4,3],[-9,-5],[1,-3,-2],[-6,-8,-7],[-10],[12,11],[10,-11,9],[-12],[7],[8],[-1],[-4]] )
    G.createCyclicGenOrder()
    print()
    print( G )

    print( "DFS from v0: " )
    for edge, vert in G.dfs():
        print( "edge: ", ALPHABET[ edge-1 ],"     downstream vert: ", vert )

    def testReducedWordRep( graph, word, fill ):
        print( "\nOriginal word: ", word )
        print( "Punctures filled: ", fill )
        print( "Reduced word after filling: ", graph.reducedWordRep( word, fill ) )
        print()

    testReducedWordRep( G, Word( [3,6,5,4,-3] ), [1] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [1] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [11] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2, 7] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2,7,5,6,8,4,12,3] ) 
    
    
        
    #print( G.reducedWordRep(  ) ) #OK
    #print( G.reducedWordRep( Word( [3,6,5,4] ), [11] ) )#OK
    #print( G.reducedWordRep( Word( [3,6,5,4] ), [2] ) )#OK
    
    #print( G.reducedWordRep( Word( [3,6,5,4] ),  ) ) #OK

    #print( "hi " )
    #for edge in G.dfs( curVert = 11 ):
    #    print( "hi" )
    #    print( edge )

def test2():
    print( cord(1,2,3) )
    print( cord(2,0,0.5) )
    print( cord(2,0,3) )
    print( cord( "a", "b", "c" ) )
    print( cord( "b", "a", "c" ) ) 

def test1():    
 
    e = Word( [] )
    e.freeReduce()
    e.cycReduce()
    #print( e )    
    w = randomWord( 20, 2, s="hit7t4yyy" )
    print()
    print( "w=\t\t",w.seq )
    w.freeReduce()
    print( "reduced, w=\t", w.seq)
    w.cycReduce()
    print( "cyc reduced, w=\t", w.seq )
    print()
    for i in range( len( w )+1 ):
        print() 
        print( w.wslice( 3, 0 ) )
        print( w.shift( i ) )

    w = randomWord( 10, 5, s="hit7t4yyy" )
    print( "w= ", w )
    print( "w( a-->BCdc )",w.simpleRewrite( 1, Word( [-2, -3, 4, 3 ] ) ) )
    print( "w( A-->BCdc )",w.simpleRewrite( -1, Word( [-2, -3, 4, 3 ] ) ) )

####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()
