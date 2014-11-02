#!/usr/bin/python
#encoding: utf-8
import os, sys, shutil
import subprocess, re
import platform

# Config

ffmpeg_binary = "ffmpeg"
ffmpeg_default_output = "timelapse.mkv"
frames_cache_dir = "frames"
ffmpeg_debugArgs = "-y"
ffmpeg_debug = True
filename_width = 10

ffmpeg_presets = {
	"h264_60": "-r 60 -i <input> -c:v libx264 -crf 0 -preset:v veryslow <output>", # predictive h264 (lossless) (not websafe)
	"h264_60_lossy": "-r 60 -i <input> -c:v libx264 -pix_fmt yuv422p -qp 16 -preset:v veryslow <output>", # h264 (lossy) web-safe
	"webm_60": "-r 60 -i <input> -c:v vp8 -b:v 2M <output>", # webm (VP8) (partially websafe (Newer browsers only))
	}

ffmpeg_formats = {
	"mp4":ffmpeg_presets["h264_60_lossy"],
	"avi":ffmpeg_presets["h264_60"],
	"mkv":ffmpeg_presets["h264_60"],
	"ts":ffmpeg_presets["h264_60"],
	"webm":ffmpeg_presets["webm_60"],
	}

arg_values = {
    "f":"forceCopy",
    "m":"moveSources",
    "s":"sortFiles",
    "nv":"disableVideo",
    "sc":"copySkip",
}

# Config end
input_args = sys.argv[1::]
arg_options = {}
for k, v in arg_values.iteritems():
    arg = "-" + k
    arg_value = v
    if arg in input_args:
        arg_value = True
        input_args.remove(arg)
    arg_options[k] = arg_value

if platform.system() != "Windows":
	arg_options["s"] = True
frames_path = frames_cache_dir
if not os.path.exists(frames_path):
	os.mkdir(frames_path)
frame_dir = os.listdir(input_args[0])
dest_path = os.listdir(frames_path)
if "Thumbs.db" in frame_dir:
	frame_dir.remove("Thumbs.db")
if "Thumbs.db" in dest_path:
	dest_path.remove("Thumbs.db")
if arg_options["s"] == True:
	frame_dir.sort(key=lambda s: s.lower())

ffmpeg_output = ffmpeg_default_output if len(input_args) < 2 else input_args[1]
frm_frmt = "." + re.match(".*\.(.*)$", (frame_dir[0] if len(frame_dir) >= 1 else dest_path[0])).group(1)
out_frmt = re.match(".*\.(.*)$", ffmpeg_output).group(1)
copy_success = False
frameid = 0

""" Copy frames """
if arg_options["sc"] != True:
	print("Comparing source with cache.")
	if len(frame_dir) >= 1:
		if not len(frame_dir) == len(dest_path) or arg_options["f"] == True:
			for frame in frame_dir:
				dest_frame = str(frameid).zfill(filename_width) + frm_frmt
				dest_file = os.path.join(frames_path, dest_frame)
				source_file = os.path.join(input_args[0], frame)
				print("Copying frame: %s -> %s" % (frame, dest_frame))
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

if arg_options["m"] == True and copy_success:
	print("Deleting source files.")
	for source_frame in frame_dir:
		os.remove(os.path.join(input_args[0], source_frame))

""" Generate time-lapse """
try:
	if arg_options["nv"] != True:
		if out_frmt in ffmpeg_formats:
			ffmpeg_input = os.path.join(frames_path, "%%%sd%s" % (str(filename_width), frm_frmt))
			if ffmpeg_debug == True:
				ffmpeg_formats[out_frmt] = "%s %s" % (ffmpeg_debugArgs, ffmpeg_formats[out_frmt])
			if "<input>" in ffmpeg_formats[out_frmt]:
				ffmpeg_formats[out_frmt] = ffmpeg_formats[out_frmt].replace("<input>", ffmpeg_input)
			if "<output>" in ffmpeg_formats[out_frmt]:
				ffmpeg_formats[out_frmt] = ffmpeg_formats[out_frmt].replace("<output>", ffmpeg_output)
			print("Loading FFmpeg.")
			ffmpeg = subprocess.Popen("%s %s" % (ffmpeg_binary, ffmpeg_formats[out_frmt]), shell=True, stdout=subprocess.PIPE)
			ffmpeg.wait()
		else:
			print("Warning: Unknown output format!")
	else:
		print("Skipping FFmpeg")
except OSError:
	print('Warning: Could not fetch FFmpeg. Is it installed? Try running with the "-nv" option to disable this warning.')
except KeyboardInterrupt:
	print("Exiting...")