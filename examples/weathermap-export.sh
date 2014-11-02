DATE=`date '+%y%m%d%H%M'`
# Point this to your generated weathermap image
SOURCE_PATH=/usr/share/cacti/plugins/weathermap/output/00000000000000000000.png
# Point this to your storage directory
DESTINATION_FOLDER=/var/weathermap/export
# This will be the filename to use for the exported files
DEST_FILE=$DESTINATION_FOLDER/weathermap_$DATE.png

# Uncomment this if you are concerned about storage and have optipng in path.
#sleep 10 && optipng -quiet $SOURCE_PATH -out $DEST_FILE
sleep 10 && cp $SOURCE_PATH $DEST_FILE