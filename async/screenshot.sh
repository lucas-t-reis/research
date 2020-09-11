#!/bin/bash
mkdir screenshot 2>/dev/null || true
for file in dot/*.dot
do
	NAME=$(basename $file | cut -d. -f1)
	dot $file -Tsvg -o screenshot/$NAME.svg
done
