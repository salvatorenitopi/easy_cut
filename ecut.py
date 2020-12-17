#!/usr/bin/env python

# https://docs.python.org/3.8/library/getopt.html
# FIX: Standardize input name and output name

import os
import sys
import shutil
import getopt
import requests
from datetime import datetime


FFMPEG_SAFE = "" # " -safe 1"	" -safe 0"
FFMPEG_LOG =  " -loglevel error -stats"

# FIX: must be able to work with upper level file ../file.mp4

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - 

def usage():
	print ("\nUsage: " + sys.argv[0] + " [parameter] [argument]\n")
	print ("\t-s\t--start\t\t[hh:mm:ss]\t\tTime to start the cut")
	print ("\t-e\t--end\t\t[hh:mm:ss]\t\tTime to finish the cut")
	print ("\t-a\t--advanced\t[advanced_expression]\t*see below")
	print ("\t-j\t--join\t\t\"file1.mp4 file2.mp4\"\tList of files to join")
	print ("\t-f\t--fix\t\t\"file.mp4\"\t\tFile to fix")
	print ("\t-d\t--download\t[url]\t\t\tURL to master.m3u")
	print ("\t-i\t--input\t\t\"input.mp4\"\t\tPATH to the input file")
	print ("\t-o\t--output\t\"output.mp4\"\t\tPATH to the output file")
	print ("\t-h\t--help")
	print ("\n\tAdvanced expression:\t\"[stat_1]-[end_1] [start_2]-[end_2]\"")
	print ("\tExample (adv_ex):\t\"00:00:10-00:02:20 00:02:50-01:00:20\"\n")


# 00:01:10 -> 70 sec
def from_time_to_sec (t):
	digits = t.split(":")
	thours = 0
	tmin = 0
	tsec = 0

	if len(digits) == 0:	return 0
	if len(digits) > 0:		tsec = int(digits[-1])
	if len(digits) > 1:		tmin = int(digits[-2])
	if len(digits) > 2:		thours = int(digits[-3])

	#print (thours, tmin, tsec)
	return (tsec + (tmin * 60) + (thours * 60 * 60))


def path_fn_ext (pppp):
	#path = os.path.dirname(os.path.abspath(pppp))
	path = os.path.dirname(pppp)
	base = os.path.basename(pppp)
	fname = os.path.splitext(base)[0]
	ext = os.path.splitext(base)[1]

	if len(path) > 0:
		return path, fname, ext

	else:
		return '.', fname, ext


# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - 


try:
	# opts, args = getopt.getopt(sys.argv[1:], 's:e:a:j:f:d:c:i:o:h:', ['start=', 'end=', 'advanced=', 'join=', 'fix=', 'download=', 'input=', 'output=', 'help'])
	opts, args = getopt.gnu_getopt(sys.argv[1:], 's:e:a:j:f:d:c:i:o:h:', ['start=', 'end=', 'advanced=', 'join=', 'fix=', 'download=', 'input=', 'output=', 'help'])

except getopt.GetoptError:
	usage()
	sys.exit(2)


opt_start = opt_end = opt_advanced = opt_join = opt_fix = opt_input = opt_output = opt_download = None
MODE = None


for opt, arg in opts:
	if opt in ('-h', '--help'):
		usage()
		sys.exit(2)

	elif opt in ('-s', '--start'):
		opt_start = arg
		MODE = "cut"

	elif opt in ('-e', '--end'):
		opt_end = arg
		MODE = "cut"

	elif opt in ('-a', '--advanced'):
		opt_advanced = arg
		MODE = "advanced"

	elif opt in ('-j', '--join'):
		opt_join = arg
		MODE = "join"

	elif opt in ('-f', '--fix'):			# ffmpeg -err_detect ignore_err -i input.mp4 -c copy input_fixed.mp4 -v quiet -stats
		opt_fix = arg
		MODE = "fix"

	elif opt in ('-d', '--download'):		# ffmpeg -i "https://path/to/master.m3u" -c copy output.mp4
		opt_download = arg
		MODE = "download"

	elif opt in ('-i', '--input'):
		opt_input = arg

	elif opt in ('-o', '--output'):
		opt_output = arg

	else:
		usage()
		sys.exit(2)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#CUT #ADVANCED #JOIN #FIX #DOWNLOAD
ct = 0
for checkopt in [(opt_start or opt_end), opt_advanced, opt_join, opt_fix, opt_download]:
	if (checkopt): ct += 1

if (ct < 1):
	print ("\n[!] Missing operation parameter/s (cut/advanced/join/fix/download).")
	usage()
	sys.exit(2)

elif (ct > 1):
	print ("\n[!] Only 1 operation at time can be performed (cut/advanced/join/fix/download).\n")
	sys.exit(2)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 




if ((not opt_input) and ((not opt_join) and (not opt_fix) and (not opt_download))):
	print ("[!] Missing input file")
	sys.exit(2)





if ((not opt_output) and (opt_input)):
	path, fname, ext = path_fn_ext (opt_input)

	#now = datetime.now()
	#date_time = now.strftime("%Y_%m_%d___%H_%M_%S")				# datetime.now().strftime("%y%d%m_%H.%M.%S")
	#opt_output = path + "/" + date_time + "_" + MODE + "_" + fname + ext

	# opt_output = path + "/" + MODE + "__" + fname + ext
	opt_output = MODE + "__" + fname + ext
	i = 2
	while (os.path.isfile(opt_output)):
		# opt_output = path + "/" + MODE + "__" + fname + " (" + str(i) + ")" + ext
		opt_output = MODE + "__" + fname + " (" + str(i) + ")" + ext
		i += 1
	
	print ("[i] Using \"" + opt_output + "\" as output")





elif ((not opt_output)):
	now = datetime.now()
	date_time = now.strftime("%Y_%m_%d___%H_%M_%S")					# datetime.now().strftime("%y%d%m_%H.%M.%S")
	opt_output = date_time + "__" + MODE + ".mp4"
	print ("[i] Using \"" + opt_output + "\" as output")




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 




if (MODE == "cut"):
	if (not opt_input):
		print ("[!] Missing input file")
		sys.exit(2)

	if (not os.path.exists(opt_input)):
		print ("[!] File: " + str(opt_input) + " does not exists")
		sys.exit(2)

	sec_start = sec_end = offset = cmd = None

	if (opt_start):					sec_start = from_time_to_sec(opt_start)
	if (opt_end): 					sec_end = from_time_to_sec(opt_end)
	if (opt_start and opt_end):		offset = sec_end-sec_start

	# print (sec_start, sec_end, offset)

	if (opt_start and opt_end):
		if (offset < 0): print ("[!] OFFSET can not be negative"); sys.exit(2)
		cmd = 'ffmpeg -ss ' + str(sec_start) + ' -i "' + str(opt_input) + '" -t ' + str(offset) + ' -codec copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)

	elif (opt_start):
		cmd = 'ffmpeg -ss ' + str(sec_start) + ' -i "' + str(opt_input) + '" -codec copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)

	elif (opt_end):
		cmd = 'ffmpeg -ss 0 -t ' + str(sec_end) + ' -i "' + str(opt_input) + '" -codec copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)

	print (cmd)
	exit_code = os.system (cmd)
	if (exit_code != 0):
		print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
		sys.exit(exit_code)





elif (MODE == "advanced"):
	if (not opt_input):
		print ("[!] Missing input file")
		sys.exit(2)

	if (not os.path.exists(opt_input)):
		print ("[!] File: " + str(opt_input) + " does not exists")
		sys.exit(2)

	if (not opt_advanced):
		print ("[!] Missing advanced string")
		sys.exit(2)


	path, fname, ext = path_fn_ext (opt_output)
	print (path, fname, ext)


	now = datetime.now()
	date_time = now.strftime("%H%M%S_tmp")
	concat_dir = date_time + "/"
	if not os.path.exists(concat_dir): 
		os.makedirs(concat_dir)

	concat = ""
	i = 0
	block_arr = opt_advanced.split(" ")
	for block in block_arr:
		i += 1
		values = block.split("-")
		sec_start = from_time_to_sec(values[0])
		sec_end = from_time_to_sec(values[1])
		offset = sec_end-sec_start

		concat += 'file \'' + str(i) + '_tmp' + str(ext) + '\'\n'
		# cmd = 'ffmpeg -ss ' + str(sec_start) + ' -i "' + str(opt_input) + '" -t ' + str(offset) + ' -codec copy "' + str(path) + "/" + str(concat_dir) + str(i) + '_tmp' + str(ext) + '"' + str(FFMPEG_LOG)
		cmd = 'ffmpeg -ss ' + str(sec_start) + ' ' + str(FFMPEG_SAFE) + ' -i "' + str(opt_input) + '" -t ' + str(offset) + ' -codec copy "' + str(concat_dir) + str(i) + '_tmp' + str(ext) + '"' + str(FFMPEG_LOG)
		# print (cmd)
		exit_code = os.system (cmd)
		if (exit_code != 0):
			print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
			sys.exit(exit_code)

	f = open(str(concat_dir) + str(date_time) + "_concat.txt", "w")
	f.write(concat)
	f.close()
	
	# cmd = 'ffmpeg -f concat ' + str(FFMPEG_SAFE) + ' -i "' + str(concat_dir) + str(date_time) + '_concat.txt" -codec copy "' + str(path) + "/" + str(fname) + str(ext) + '"' + str(FFMPEG_LOG)
	cmd = 'ffmpeg -f concat ' + str(FFMPEG_SAFE) + ' -i "' + str(concat_dir) + str(date_time) + '_concat.txt" -codec copy "' + str(path) + "/" + str(fname) + str(ext) + '"' + str(FFMPEG_LOG)
	exit_code = os.system (cmd)
	if (exit_code != 0):
		print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
		sys.exit(exit_code)
	
	shutil.rmtree(concat_dir)





elif (MODE == "join"):
	blocks = opt_join.split(" ")

	if (len(blocks) < 2):
		print ("[!] Error: too few elements to join.")
		sys.exit(2)

	for b in blocks:
		if (not os.path.isfile(b)):
			print ("[!] Error: " + str(b) + " not found.")
			sys.exit(2)


	basedir = "./"
	now = datetime.now()
	date_time = now.strftime("%H%M%S_tmp")

	concat = ""
	for b in blocks:
		concat += 'file \'' + str(b) + '\'\n'

	f = open(str(basedir) + str(date_time) + "_concat.txt", "w")
	f.write(concat)
	f.close()

	cmd = 'ffmpeg -f concat ' + str(FFMPEG_SAFE) + ' -i "' + str(basedir) + str(date_time) + '_concat.txt" -codec copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)
	exit_code = os.system (cmd)
	if (exit_code != 0):
		print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
		sys.exit(exit_code)

	os.remove (str(basedir) + str(date_time) + "_concat.txt")





elif (MODE == "fix"):
	if (not opt_fix):
		print ("[!] Missing input file")
		sys.exit(2)

	if (not os.path.exists(opt_fix)):
		print ("[!] File: " + str(opt_fix) + " does not exists")
		sys.exit(2)

	if (opt_fix == opt_output):
		print ("[!] Cannot edit existing files in-place")
		sys.exit(2)


	cmd = 'ffmpeg -err_detect ignore_err -i "' + str(opt_fix) + '" -c copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)
	exit_code = os.system (cmd)
	if (exit_code != 0):
		print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
		sys.exit(exit_code)





elif (MODE == "download"):
	if (opt_start or opt_end or opt_advanced or opt_join or opt_fix or opt_input):
		print ("[!] Too much parameter for MODE: " + str(MODE))
		sys.exit(2)

	if (not opt_download):
		print ("[!] Missing URL")
		sys.exit(2)


	cmd = 'ffmpeg -i "' + str(opt_download) + '" -c copy "' + str(opt_output) + '"' + str(FFMPEG_LOG)
	exit_code = os.system (cmd)
	if (exit_code != 0):
		print ("[!] FFMPEG exited with code: " + str(exit_code) + ", quitting...")
		sys.exit(exit_code)


else:
	print ("[!] Mode: " + str(MODE) + " not found")




