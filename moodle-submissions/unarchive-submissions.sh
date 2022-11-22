#!/bin/bash
# (C) Andrei Olaru

if [ $# == 0 ]; then
	echo "Usage: ./unarchive-submissions.sh [OPTIONS] big-zip-file [name-selection-file=all] [select-file=none] "
	echo "OPTIONS:"
	echo "-np : present the ouput in SURNAME Name form, rather than Name SURNAME."
	echo "-a : files contain both online submissions and archives and other files."
	echo "-pre : prepend student directory names with the argument given after this option."
	echo "-post : append student directory names with the argument given after this option."
	echo "-keep : keep the directory structure of one directory for each phase of the processing."
	echo "-log : use the next argument as the name of the output log (default is log.txt)."
	echo "The big-zip-file is expected to contain several submission folders, each containing all the files submitted by the student."
	echo "The name-selection-file should contain lines of the form Firstname-Firstname-Firstname LASTNAME-LASTNAME . Use 'all' to select all students."
	echo "The last argument can be a pattern (\"*.txt\") or a specific file name (\"tema.txt\") or \"*\" to select all files into a flat structure."
	exit
fi

mixedfiles=false
namefirst=false
keepfiles=false
pre=""
post=""
log="log.txt"

while [ true ]; do
	if [ "${1:0:1}" == "-" ]; then
		case $1 in
			"-a") mixedfiles=true
			;;
			"-np") namefirst=true
			;;
			"-pre") shift; pre=$1
			;;
			"-post") shift; post=$1
			;;
			"-log") shift; log=$1
			;;
			"-keep") keepfiles=true
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

mkdir "$basedir" 2>> $log || ( echo "Output directory exists, press ENTER to REMOVE or Ctrl^C otherwise: $basedir";
	read; rm -r "$basedir"; mkdir "$basedir"; exit )


echo "Extracting main archive..." | tee -a $log
mkdir "$originals" 2> >(tee -a $log)
unzip -O UTF-8 "$1" -d "$originals" >> $log || exit


echo "Extracting individual archives..." 2> >(tee -a $log)
mkdir "$unarchived" 2> >(tee -a $log)
success=0
directories=0
globalfound=0
while read i; do
	echo "---------------" >> $log
	echo $i >> $log
	((directories+=1))
	found=0
	if [ "$mixedfiles" = "true" ] ; then
		# if mixed files, copy everything; the first archive will be unzipped later
		mkdir "$unarchived/$i" 2> >(tee -a $log)
		cp -r "$originals/$i"/* "$unarchived/$i" 2> >(tee -a $log)
		nfiles=$(ls -1q "$unarchived/$i/" | wc -l)
		if [[ nfiles -gt 0 ]] ; then
			((found+=1))
			((globalfound+=1))
			echo $nfiles "files copied" >> $log
		fi
	fi
	while read -r f ; do
		# find first tar archive; unarchive;
		# if mixed files, then remove the archive file itself from the output
		echo "-----> found archive tar:" $f >> $log
		if [ "$mixedfiles" = "false" ]; then mkdir "$unarchived/$i"; fi
		if tar -xzvf "$f" -C "$unarchived/$i" >> $log ; then
			((found+=1))
			((success+=1))
			if [ "$mixedfiles" = "true" ] ; then 
				((globalfound-=1))
				rm "$unarchived/$i/$(basename -- "$f")" 2> >(tee -a $log)
			fi
		else
			echo -e $errormarker "in" $i | tee -a $log
		fi
		break
	done < <(find "$originals/$i" -type f \( -name "*.tgz" -or -name "*.tar.gz" \))
#	if [ $found -eq 1 ]; then continue; fi
	while read -r f ; do
		# find first zip archive; unarchive;
		# if mixed files, then remove the archive file itself from the output	
		echo "-----> found archive zip:" $f >> $log
		if [ "$mixedfiles" = "false" ]; then mkdir "$unarchived/$i"; fi
		if unzip "$f" -d "$unarchived/$i" >> $log ; then
			((found+=1))
			((success+=1))
			if [ "$mixedfiles" = "true" ] ; then 
				((globalfound-=1))
				rm "$unarchived/$i/$(basename -- "$f")" 2> >(tee -a $log)
			fi
		else
			echo -e $errormarker "in" $i | tee -a $log
		fi
		break
	done < <(find "$originals/$i" -type f -name "*.zip")
	# if no files (when mixed) or no archives found, then error
	if [ $found -gt 0 ]; then continue; fi
	echo -e "-----> no archives or files found in " $i "\n" $errormarker | tee -a $log
done < <(ls "$originals")

result="Unarchived $success archives and copied $globalfound other files in $directories submissions"
finalresult="$result"
echo $result | tee -a $log

echo "Improving folder names..." | tee -a $log
rename -v 's/(.*)_[0-9]+_assignsubmission_file_(.*)/$1/' "$unarchived"/* >> $log

if [ "$mixedfiles" = "true" ] ; then
	rename -v 's/(.*)_[0-9]+_assignsubmission_onlinetext_/$1-online/' "$unarchived"/* >> $log
	while read -r i ; do
		name=${i:0:-7}
		mkdir "$name" 2> /dev/null
		cp "$i"/* "$name" 2> >(tee -a $log) && rm -r "$i" 2> >(tee -a $log)
	done < <(find "$unarchived/$i" -type d -name "*-online")
fi

selected=0
if [[ $# -gt 1 && $2 != "all" ]] ; then
	echo "Selecting submissions from $2 ..." | tee -a $log
	mkdir "$selection" 2> >(tee -a $log)
	while read i; do
		if [[ $(cat $2 | grep "$i" | wc -l) -gt 0 ]] ; then
			echo $i "selected" >> $log
		else
			echo -e $spacer $i "not selected" >> $log
			continue
		fi
		cp -r "$unarchived/$i" "$selection" 2> >(tee -a $log)
		((selected+=1))
	done < <(ls "$unarchived")
	result="$selected submissions selected"
else
	result="No selection made."
	mkdir "$selection"
	cp -r "$unarchived"/* "$selection" 2> >(tee -a $log)
fi
finalresult="$finalresult ; $result"
echo $result | tee -a $log

echo $namefirst
if [ "$namefirst" = "true" ] ; then
	echo "Putting name first..." | tee -a $log
	rename -v 's/(.*\/)(.*) ([^ ]*)/$1$3 $2/' "$selection"/* >> $log
fi

if [[ -n $pre || -n $post ]] ; then
	echo "Adding prefix / suffix <$pre>/<$post>" | tee -a $log
	rename -v 's/(.*\/)(.*)/$1'"$pre"'$2'"$post"'/' "$selection"/* >> $log
fi

function join_by { local d=${1-} f=${2-}; if shift 2; then printf %s "$f" "${@/#/$d}"; fi; }

selectedfiles=0
if [[ $# -gt 2 ]] ; then
	patterninput=$3
	IFS='|' read -ra pattern <<< "$patterninput"
	echo "Pattern: ${pattern[*]}" | tee -a $log
	if [[ ${#pattern[@]} -gt 1 ]] ; then
		patternS="\( -name \"${pattern[0]}\""
		unset -v 'pattern[0]'
		for i in "${pattern[@]}" ; do
			patternS="$patternS -o -name \"$i\""
		done
		patternS="$patternS \)"
	else
		patternS="-name \"${pattern[0]}\""
	fi
	echo "Selecting files $3 with find pattern: $patternS ..." | tee -a $log
	mkdir "$files" 2> >(tee -a $log)
	while read -r name ; do
		findCmd="find \"$selection/$name\" -type f $patternS"
		while read -r f ; do
			file=$(basename -- "$f")
			dir=$(dirname "$f")
			echo "found file: $file in $dir for $name" >> $log
			cp "$f" "$files/$name-$file" 2> >(tee -a $log)
			((selectedfiles+=1))
		done < <(eval $findCmd)
	done < <(ls "$selection")
	result="$selectedfiles files selected."
	echo $result | tee -a $log
	finalresult="$finalresult ; $result"
fi

if [ "$keepfiles" = "false" ]; then
	echo "cleanup & organization..." | tee -a $log
	rm -r "$originals" >> $log
	rm -r "$unarchived" >> $log
	if [[ $# -gt 2 ]] ; then
		rm -r "$selection" >> $log
		output="$files"
	else
		output="$selection"
	fi
	mv "$output"/* "$basedir" 2> >(tee -a $log)
	rm -r "$output" 2> >(tee -a $log)
fi

echo "DONE:" $finalresult | tee -a $log
echo "Log file in $log"


