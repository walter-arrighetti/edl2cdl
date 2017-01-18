##################################################
##  edl2cdl.py                                  ##
##______________________________________________##
##  Reads a CMX3600-like Edit Decision List     ##
##  (EDL) file, extracts all the CDLs in it,    ##
##  exports either  single Color Decision List  ##
##  (.cdl file extension), a single correction  ##
##  (.cc file extension), or a *Collection* of  ##
##  of color corrections (.ccc file extension)  ##
##  CDLs are then named or given IDs according  ##
##  to the EDL tapenames. Footage coming from   ##
##  ARRI, RED or similar cameras has tapenames  ##
##  like "A001[_]C009[...]" which this utility  ##
##  acknowledges to use "A001C001" as tapename  ##
##  in IDs within the CCC file (or as filename  ##
##  for individual CDLs/CCs within a folder.    ##
##______________________________________________##
##  Copyright (C) 2017 Walter Arrighetti, PhD   ##
##  All Rights Reserved.                        ##
##                                              ##
##################################################
#!/usr/bin/env python 
_version = "0.6"
import os
import re
import sys

print "EDL-to-CDL Conversion Utility version %s"%_version
print "Copyright (C) 2017 Walter Arrighetti PhD.\n"

useCCC = "CDL"
if len(sys.argv)==2 and sys.argv[1].lower() not in ["--cdl","--cc","--ccc"]:
	useCCC = "CCC"
	infile = os.path.abspath(sys.argv[1])
	basename = os.path.splitext(os.path.split(infile)[-1])[0]
	outfile = os.path.join(outpath,basename+".ccc")
elif len(sys.argv)==3 and (sys.argv[1].lower()=="--ccc" or sys.argv[2].lower()=="--ccc"):
	useCCC = "CCC"
	if sys.argv[2].lower()=="--ccc":
		infile = os.path.abspath(sys.argv[1])
		outpath = os.path.split(infile)[0]
	else:
		infile = os.path.abspath(sys.argv[2])
		outpath = os.path.split(infile)[0]
	basename = os.path.splitext(os.path.split(infile)[-1])[0]
	outfile = os.path.join(outpath,basename+".ccc")
if len(sys.argv)==3 and ((sys.argv[1].lower() not in ["--cdl","--cc","--ccc"]) or (sys.argv[3].lower() not in ["--cdl","-cc","--ccc"])):
	useCCC = "CCC"
	infile = os.path.abspath(sys.argv[1])
	basename = os.path.splitext(os.path.split(infile)[-1])[0]
	if os.path.isdir(sys.argv[2]):
		outfile = os.path.join(sys.argv[2],os.path.splitext(basename)[0]+".ccc")
	else:	outfile = os.path.abspath(sys.argv[2])
elif len(sys.argv)==4 and ((sys.argv[3].lower() in ["--cdl","--cc","--ccc"]) or (sys.argv[1].lower() in ["--cdl","--cc","--ccc"])):
	if sys.argv[3].lower() in ["--cdl","--cc","--ccc"]:
		infile = os.path.abspath(sys.argv[1])
		basename = os.path.splitext(os.path.split(infile)[-1])[0]
		if sys.argv[3].lower()=="--ccc":
			useCCC = "CCC"
			if os.path.isdir(sys.argv[2]):
				outfile = os.path.join(sys.argv[2],os.path.splitext(basename)[0]+".ccc")
			else:	outfile = os.path.abspath(sys.argv[2])
		else:
			if sys.argv[3].lower()=="--cdl":	useCCC = "CDL"
			else:	useCCC = "CC"
			outpath = os.path.abspath(sys.argv[2])
	else:
		infile = os.path.abspath(sys.argv[2])
		if sys.argv[1].lower()=="--ccc":
			useCCC = "CCC"
			if os.path.isdir(sys.argv[3]):
				outfile = os.path.join(sys.argv[3],os.path.splitext(basename)[0]+".ccc")
			else:	outfile = os.path.abspath(sys.argv[3])
		else:
			if sys.argv[1].lower()=="--cdl":	useCCC = "CDL"
			else:	useCCC = "CC"
			outpath = os.path.abspath(sys.argv[3])
else:
	print " * SYNTAX:  %s  infile.EDL  [outpathname]  [--cdl|cc|ccc]\n"%os.path.split(sys.argv[0])[-1]
	print "            A CMX3600-like EDL file is expected as input and a target folder as"
	print "            output. By default, single CCC (color correction collection, --ccc)"
	print "            file is created, otherwise a target folder is created with a single"
	print "            CDL (--cdl) or CC (--cc) file per every EDL event's color decision."
	print "            Color correction IDs (ccid) are assinged as the EDL event tapenames"
	sys.exit(1)

cam1re = re.compile(r"[*]\sFROM\sCLIP\sNAME:\s+(?P<name>[A-Z][0-9]{3}[_]C[0-9]{3})[_]")
cam2re = re.compile(r"[*]\sFROM\sCLIP\sNAME:\s+(?P<name>[A-Z][0-9]{3}C[0-9]{3})[_]")
input_desc, viewing_desc = None, "EDL2CDL script by Walter Arrighetti"
tapere = re.compile(r"[*]\sFROM\sCLIP\sNAME:\s+(?P<name>.{8,32})")
cdl1re = re.compile(r"[*]\sASC[_]SOP\s+[(]\s?(?P<sR>[-]?\d+[.]\d{4})\s+(?P<sG>[-]?\d+[.]\d{4})\s+(?P<sB>[-]?\d+[.]\d{4})\s?[)]\s?[(]\s?(?P<oR>[-]?\d+[.]\d{4})\s+(?P<oG>[-]?\d+[.]\d{4})\s+(?P<oB>[-]?\d+[.]\d{4})\s?[)]\s?[(]\s?(?P<pR>[-]?\d+[.]\d{4})\s+(?P<pG>[-]?\d+[.]\d{4})\s+(?P<pB>[-]?\d+[.]\d{4})\s?[)]\s?")
cdl2re = re.compile(r"[*]\sASC[_]SAT\s+(?P<sat>\d+[.]\d{4})")

ln = 0

CCC = []

def writeCDL(Id, SOPnode, SATnode):
	CCC.append( {
		'id': Id,
		'slope': SOPnode[0],
		'offset':SOPnode[1],
		'power': SOPnode[2],
		'SAT':   SATnode
	} )

if (useCCC in ["CDL","CC"]) and ((not os.path.exists(outpath)) or (not os.path.isdir(outpath))):
	try:	os.mkdir(outpath)
	except:
		print " * ERROR!: Unable to create output folder \"%s\"."%outpath
		sys.exit(2)
tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
for line in open(infile,"r"):
	if cam1re.match(line):
		CDLevent, L = True, cam1re.match(line)
		tapename = L.group("name")
		if CDLevent and thisCDL:
			writeCDL(tapename,thisCDL,thisSAT)
			tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
		thisCDL, thisSAT = None, 0
		continue
	if cam2re.match(line):
		CDLevent, L = True, cam2re.match(line)
		tapename = L.group("name")
		if CDLevent and thisCDL:
			writeCDL(tapename,thisCDL,thisSAT)
			tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
		thisCDL, thisSAT = None, 0
		continue
	elif tapere.match(line):
		CDLevent, L = True, tapere.match(line)
		tapename = L.group("name")
		if CDLevent and thisCDL:
			writeCDL(tapename,thisCDL,thisSAT)
			tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
		continue
	elif CDLevent and cdl1re.match(line):
		ids = [cc['id'].lower() for cc in CCC]
		if tapename.lower() in ids:
			ids = [id for id in ids if re.match(tapename+r"-\d{3}",id)]
			if not ids:	tapename = tapename+"-001"
			else:
				ids.sort()
				tapename = tapename + "-%03d"%( int(ids[-1][-3:])+1 )
		del ids
		L = cdl1re.match(line)
		thisCDL = ( tuple(map(float,(L.group("sR"),L.group("sG"),L.group("sB")))), tuple(map(float,(L.group("oR"),L.group("oG"),L.group("oB")))), tuple(map(float,(L.group("pR"),L.group("pG"),L.group("pB")))) ) 
		thisSAT = 0
		continue
	elif CDLevent and thisCDL and cdl2re.match(line):
		L = cdl2re.match(line)
		thisSAT = float(L.group("sat"))
		writeCDL(tapename,thisCDL,thisSAT)
		tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
if thisCDL:
	writeCDL(tapename,thisCDL,thisSAT)
	tapename, CDLevent, thisCDL, thisSAT = None, False, None, 0
if not CCC:
	print "No Color Decision(s) found in EDL file \"%s\". Quitting."%os.path.split(infile)[1]
	sys.exit(0)
print " * %d Color Decision(s) found in EDL file \"%s\"."%(len(CCC),os.path.split(infile)[1])

if useCCC=="CCC":
	try:	CCCout = open(outfile,"w")
	except:
		print " * ERROR!: Unable to create output CCC file \"%s\"."%outfile
		sys.exit(3)
	buf = []
	buf.append('<?xml version="1.0" encoding="UTF-8"?>')
	buf.append('<ColorCorrectionCollection xmlns="urn:ASC:CDL:v1.2">')
	if input_desc:	buf.append('\t<InputDescription>%s</InputDescription>'%input_desc)
	if viewing_desc:	buf.append('\t<ViewingDescription>%s</ViewingDescription>'%viewing_desc)
	for n in range(len(CCC)):
		buf.append('\t<ColorCorrection id="%s">'%CCC[n]['id'])
		buf.append('\t\t<SOPNode>')
		buf.append('\t\t\t<Slope>%.05f %.05f %.05f</Slope>'%CCC[n]['slope'])
		buf.append('\t\t\t<Offset>%.05f %.05f %.05f</Offset>'%CCC[n]['offset'])
		buf.append('\t\t\t<Power>%.05f %.05f %.05f</Power>'%CCC[n]['power'])
		buf.append('\t\t</SOPNode>')
		buf.append('\t\t<SatNode>')
		buf.append('\t\t\t<Saturation>%.05f</Saturation>'%CCC[n]['SAT'])
		buf.append('\t\t</SatNode>')
		buf.append('\t</ColorCorrection>')
	buf.append('</ColorCorrectionCollection>')
	CCCout.write('\n'.join(buf))
	CCCout.close()
	print " * %d CDL(s) written in CCC file \"%s\""%(len(CCC),os.path.split(outfile)[1])
elif useCCC in ["CC","CDL"]:
	for n in range(len(CCC)):
		outfile = os.path.join(outpath,CCC[n]['id'])
		if useCCC=="CDL":	outfile += ".cdl"
		else:	outfile += ".cc"
		try:	CDLout = open(outfile,"w")
		except:
			print " * ERROR!: Unable to create output CDL file \"%s\"."%outfile
		buf = []
		if useCCC=="CDL":
			buf.append('<?xml version="1.0" encoding="UTF-8"?>')
			buf.append('<ColorDecisionList xmlns="urn:ASC:CDL:v1.2">')
			if input_desc:	buf.append('\t<InputDescription>%s</InputDescription>'%input_desc)
			if viewing_desc:	buf.append('\t<ViewingDescription>%s</ViewingDescription>'%viewing_desc)
			tab = '\t'
		else:	tab = ''
		buf.append(tab+'<ColorCorrection id="%s">'%CCC[n]['id'])
			if useCCC=="CC" and input_desc:	buf.append('\t<InputDescription>%s</InputDescription>'%input_desc)
			if useCCC=="CC" and viewing_desc:	buf.append('\t<ViewingDescription>%s</ViewingDescription>'%viewing_desc)
		buf.append(tab+'\t<SOPNode>')
		buf.append(tab+'\t\t<Slope>%.05f %.05f %.05f</Slope>'%CCC[n]['slope'])
		buf.append(tab+'\t\t<Offset>%.05f %.05f %.05f</Offset>'%CCC[n]['offset'])
		buf.append(tab+'\t\t<Power>%.05f %.05f %.05f</Power>'%CCC[n]['power'])
		buf.append(tab+'\t</SOPNode>')
		buf.append(tab+'\t<SatNode>')
		buf.append(tab+'\t\t<Saturation>%.05f</Saturation>'%CCC[n]['SAT'])
		buf.append(tab+'\t</SatNode>')
		buf.append(tab+'</ColorCorrection>')
		if useCCC=="CDL":
			buf.append('</ColorDecisionList>')
		CDLout.write('\n'.join(buf))
		CDLout.close()
	print " * %d individual %s(s) written in folder \"%s\"."%(len(CCC),useCCC,outpath)
else:
	print " * ERROR!: Invalid Color Decision List mode '%s'; quitting."%useCCC
	sys.exit(9)
sys.exit(0)
