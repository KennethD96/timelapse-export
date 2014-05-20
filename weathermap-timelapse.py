#!/usr/bin/python
#encoding: utf-8
import os, sys, shutil
import subprocess, re

ffmpeg_presets = {
	"h264_60": "-y -r 60 -i <input> -vcodec libx264 -qp 1 -preset:v veryslow <output>",
	"webm_60": "-y -r 60 -i <input> -vcodec vp8 -b:v 2M <output>",
	}

ffmpeg_formats = {
	"mp4":ffmpeg_presets["h264_60"],
	"avi":ffmpeg_presets["h264_60"],
	"mkv":ffmpeg_presets["h264_60"],
	"ts":ffmpeg_presets["h264_60"],
	"webm":ffmpeg_presets["webm_60"],
	}

ffmpeg_default_output = "weathermap.mp4"
frames_output_path = "frames"
filename_width = 10

input_args = sys.argv[1::]

"""No video (just copy frames)"""
if "-nv" in input_args:
	novideo = True
	input_args.remove("-nv")
else:
	novideo = False
"""Skip copy from source"""
if "-sc" in input_args:
	doskipcopy = True
	input_args.remove("-sc")
else:
	doskipcopy = False
"""Sort files"""
if "-s" in input_args:
	sort_dir = True
	input_args.remove("-s")
else:
	sort_dir = False
"""Force Copy (disable folder comparison)"""
if "-fc" in input_args:
	force_copy = True
	input_args.remove("-fc")
else:
	force_copy = False
"""Move source file (delete source when finished)"""
if "-m" in input_args:
	domove = True
	input_args.remove("-m")
else:
	domove = False

frames_path = frames_output_path
frame_dir = os.listdir(input_args[0])
dest_path = os.listdir(frames_path)
if sort_dir:
	frame_dir.sort()

ffmpeg_output = ffmpeg_default_output if len(input_args) < 2 else input_args[1]
frm_frmt = "." + re.match(".*\.(.*)$", (frame_dir[0] if len(frame_dir) >= 1 else dest_path[0])).group(1)
out_frmt = re.match(".*\.(.*)$", ffmpeg_output).group(1)
copy_success = False
frameid = 0

if not os.path.exists(frames_path):
	os.mkdir(frames_path)

""" Copy frames """
if not doskipcopy:
	print("Comparing source with cache.")
	if len(frame_dir) >= 1:
		if not len(frame_dir) == len(os.listdir(frames_path)) or force_copy:
			for frame in frame_dir:
				dest_frame = str(frameid).zfill(filename_width) + frm_frmt
				dest_file = os.path.join(frames_path, dest_frame)
				source_file = os.path.join(input_args[0], frame)
				print("Moving frame: %s -> %s" % (frame, dest_frame))
				shutil.copy(source_file, dest_file)
				frameid = frameid+1
			copy_success = True
			print("%s frames moved successfully!" % str(len(frame_dir)))
		else:
			print("Source unchanged. Skipping.")
	else:
		print("Source-dir is empty, skipping copy.")
else:
	print("Skipping copy.")

if domove and copy_success:
	for source_frame in frame_dir:
		os.remove(source_frame)

""" Generate time-lapse """
try:
	if not novideo:
		if out_frmt in ffmpeg_formats:
			ffmpeg_input = os.path.join(frames_path, "%%%sd%s" % (str(filename_width), frm_frmt))
			if "<input>" in ffmpeg_formats[out_frmt]:
				ffmpeg_formats[out_frmt] = ffmpeg_formats[out_frmt].replace("<input>", ffmpeg_input)
			if "<output>" in ffmpeg_formats[out_frmt]:
				ffmpeg_formats[out_frmt] = ffmpeg_formats[out_frmt].replace("<output>", ffmpeg_output)
			print("Starting time-lapse export...")
			ffmpeg = subprocess.Popen("ffmpeg %s" % ffmpeg_formats[out_frmt], shell=True, stdout=subprocess.PIPE)
			ffmpeg.wait()
		else:
			print("Warning: Unknown output format!")
except OSError:
	print('Warning: Could not fetch FFmpeg. Is it installed? Try running with the "-nv" option to disable this warning.')
except KeyboardInterrupt:
	print("Exiting...")