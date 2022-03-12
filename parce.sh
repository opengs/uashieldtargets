#!/bin/sh
# 
#  Usage: parce.sh <file_with_proxies>
#  output to validated_<file_with_proxies>
#  <file_with_proxies> must be plain text, line by line
# 

filename="$1"
echo "Start"
filename_out="validated_${filename}"
echo "" > "${filename_out}"
while read p; do 
    # curl -Ik -x "$p" "https://googe.com"
    curl --silent --output /dev/null -I googe.com -x "$p" 2>/dev/null && echo "$p" >> "${filename_out}" || echo "$p   FAIL" 

done < "$filename"
echo "Done"
