#!/bin/bash
# (C) Andrei Olaru

if [ $# == 0 ]; then
	echo "Usage: ./unarchive-submissions.sh [-np] [-a] big-zip-file [name-selection-file=all] [select-file=none] "
	echo "-np : present the ouput in SURNAME Name form, rather than Name SURNAME."
	echo "-a : files contain both online submissions and archives and other files."
	echo "The big-zip-file is expected to contain several submission folders, each containing all the files submitted by the student."
	echo "The name-selection-file should contain lines of the form Firstname-Firstname-Firstname LASTNAME-LASTNAME . Use 'all' to select all students."
	echo "The last argument can be a pattern (\"*.txt\") or a specific file name (\"tema.txt\") or \"*\" to select all files in a flat structure."
	exit
fi

mixedfiles=false
namefirst=false

while [ true ]; do
	if [ "${1:0:1}" == "-" ]; then
		case $1 in
			"-a") mixedfiles=true
			;;
			"-np") namefirst=true
			;;
		esac
	else
		break
	fi
	shift
done



archive=$(basename -- "$1")
basedir="${archive%.*}"
originals="$basedir/1original"
unarchived="$basedir/2unarchived"
selection="$basedir/3selected"
files="$basedir/4files"

errormarker="\t\t\t\t\t\t\t\t\t\t ##### ERROR"
spacer="\t\t\t\t\t\t\t"

mkdir "$basedir" || ( echo "Output directory <$basedir> exists, press ENTER to REMOVE or Ctrl^C otherwise";
	read; rm -r "$basedir"; mkdir "$basedir"; exit )

echo "Extracting main archive"
mkdir "$originals"
unzip "$1" -d "$originals" || exit


echo "Extracting individual archives"
mkdir "$unarchived"
success=0
directories=0
while read i; do
	echo "---------------"
	echo $i
	((directories+=1))
	found=0
	if [ $mixedfiles ] ; then
		mkdir "$unarchived/$i"
		cp -r "$originals/$i"/* "$unarchived/$i"
		nfiles=$(ls -1q "$unarchived/$i/" | wc -l)
		if [[ nfiles -gt 0 ]] ; then
			((found+=1))
			echo $nfiles "files copied"
		fi
	fi
	while read -r f ; do
		echo "-----> found archive tar:" $f
		if [ ! $mixedfiles ]; then mkdir "$unarchived/$i"; fi
		if tar -xzvf "$f" -C "$unarchived/$i" ; then
			((found+=1))
			((success+=1))
			if [ $mixedfiles ] ; then rm "$unarchived/$i/"$(basename -- "$f"); fi
		else
			 echo -e $errormarker
		fi
		break
	done < <(find "$originals/$i" -type f \( -name "*.tgz" -or -name "*.tar.gz" \))
#	if [ $found -eq 1 ]; then continue; fi
	while read -r f ; do
		echo "-----> found archive zip:" $f
		if [ ! $mixedfiles ]; then mkdir "$unarchived/$i"; fi
		if unzip "$f" -d "$unarchived/$i" ; then
			((found+=1))
			((success+=1))
			if [ $mixedfiles ] ; then rm "$unarchived/$i/"$(basename -- "$f"); fi
		else
			echo -e $errormarker
		fi
		break
	done < <(find "$originals/$i" -type f -name "*.zip")
	if [ $found -gt 0 ]; then continue; fi
	echo -e "-----> no archive found in " $i "\n" $errormarker
done < <(ls "$originals")

echo "Correctly unarchived" $success "/" $directories "submissions"

echo "Improving folder names..."
rename -v 's/(.*)_[0-9]+_assignsubmission_file_/$1/' "$unarchived"/*

if $mixedfiles ; then
	rename -v 's/(.*)_[0-9]+_assignsubmission_onlinetext_/$1-online/' "$unarchived"/*
	while read -r i ; do
		name=${i:0:-7}
		mkdir "$name" 2> /dev/null
		cp "$i"/* "$name" && rm -r "$i"
	done < <(find "$unarchived/$i" -type d -name "*-online")
fi

selected=0
if [[ $# -gt 1 && $2 != "all" ]] ; then
	echo "Selecting submissions from $2 ..."
	mkdir "$selection"
	while read i; do
		if [[ $(cat $2 | grep "$i" | wc -l) -gt 0 ]] ; then
			echo $i "selected"
		else
			echo -e $spacer $i "not selected"
			continue
		fi
		cp -r "$unarchived/$i" "$selection"
		((selected+=1))
	done < <(ls "$unarchived")
	echo $selected "submissions selected"
else
	echo "No selection made."
	mkdir "$selection"
	cp -r "$unarchived"/* "$selection"
fi


if $namefirst ; then
	echo "Putting name first..."
	rename -v 's/(.*\/)(.*) ([^ ]*)/$1$3 $2/' "$selection"/*
fi


selectedfiles=0
if [[ $# -gt 2 ]] ; then
	echo "Selecting files $3 ..."
	mkdir "$files"
	while read -r name ; do
		while read -r f ; do
			file=$(basename -- "$f")
			dir=$(dirname "$f")
			echo "found file: $file in $dir for $name"
			cp "$f" "$files/$name-$file"
			((selectedfiles+=1))
		done < <(find "$selection/$name" -type f -name "$3")
	done < <(ls "$selection")
	echo $selectedfiles "files selected."
fi



