#!/usr/bin/env bash

if [ $# -ne 2 ]; then
    echo $0: usage: build-article-referential.sh source_dir target_csv_file
    exit 1
fi

echo "Extracting NLM files data stored in directory $1 to csv file $2"

find $1 -type f -name "*.xml" |xargs xmlstarlet sel -n -t -v "concat('\"', //_:journal-id[@journal-id-type='other'], '\"@\"', //_:journal-title, '\"@\"', //_:journal-subtitle, '\"@\"', //_:article-id[@pub-id-type='other'], '\"@', //_:pub-date[@pub-type='epub']/_:year, '@\"', //_:pub-date[@pub-type='collection']/_:year, '\"##')" | tr '\n' ' ' | sed "y/’āáǎàâēéěèīíǐìōóǒòūúǔùǖǘǚǜĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙǕǗǙǛ/'aaaaaeeeeiiiioooouuuuüüüüAAAAEEEEIIIIOOOOUUUUÜÜÜÜ/"| sed 's/##/\'$'\n/g' | sed '$ d'| sed -e 's/•//g' | sed -e "s/  */ /g" > $2
