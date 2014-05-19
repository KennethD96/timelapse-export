#!/usr/bin/python
#encoding: utf-8
import os, sys, shutil
import subprocess, re

ffmpeg_presets = {
	"h264_50": "-y -r 50 -i <input> -vcodec libx264 -qp 5 -preset:v fast <output>",
	"webm_50": "-y -r 50 -i <input> -vcodec vp8 -b:v 2M <output>",
	}
ffmpeg_args = {
	"mp4":ffmpeg_presets["h264_50"],
	"avi":ffmpeg_presets["h264_50"],
	"ts":ffmpeg_presets["h264_50"],
	"mkv":ffmpeg_presets["h264_50"],
	"webm":ffmpeg_presets["webm_50"],
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

frame_dir = os.listdir(input_args[0])
if sort_dir:
	frame_dir.sort()

current_path = os.path.dirname(__file__)
frames_path = frames_output_path
ffmpeg_output = ffmpeg_default_output if len(input_args) < 2 else input_args[1]
frm_frmt = "." + re.match(".*\.(.*)$", frame_dir[0]).group(1)
out_frmt = re.match(".*\.(.*)$", ffmpeg_output).group(1)
frameid = 0

if not os.path.exists(frames_path):
	os.mkdir(frames_path)

""" Copy frames """
print("Comparing source with cache.")
if not len(frame_dir) == len(os.listdir(frames_path)) or force_copy:
	for frame in frame_dir:
		dest_frame = str(frameid).zfill(filename_width) + frm_frmt
		dest_file = os.path.join(frames_path, dest_frame)
		print("Moving frame: %s -> %s" % (frame, dest_frame))
		shutil.copy(os.path.join(input_args[0], frame), dest_file)
		frameid = frameid+1
	print("Frames exported successfully!")
else:
	print("Source unchanged from cache. Skipping.")

""" Generate time-lapse """
try:
	if not novideo:
		if out_frmt in ffmpeg_args:
			ffmpeg_input = os.path.join(frames_path, "%%%sd%s" % (str(filename_width), frm_frmt))
			if "<input>" in ffmpeg_args[out_frmt]:
				ffmpeg_args[out_frmt] = ffmpeg_args[out_frmt].replace("<input>", ffmpeg_input)
			if "<output>" in ffmpeg_args[out_frmt]:
				ffmpeg_args[out_frmt] = ffmpeg_args[out_frmt].replace("<output>", ffmpeg_output)
			print("Starting time-lapse export...")
			subprocess.Popen("ffmpeg %s" % ffmpeg_args[out_frmt], shell=True, stdout=subprocess.PIPE)
		else:
			print("Warning: Unknown output format!")
except OSError:
	print("Warning: Could not fetch FFMPEG. Is it installed?")