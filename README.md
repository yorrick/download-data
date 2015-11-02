[![Build Status](https://travis-ci.org/yorrick/erudit-download-data.svg?branch=master)](https://travis-ci.org/yorrick/erudit-download-data)

[![Coverage Status](https://coveralls.io/repos/yorrick/erudit-download-data/badge.svg?branch=master&service=github)](https://coveralls.io/github/yorrick/erudit-download-data?branch=master)

## Setup project

```
virtualenv --no-site-packages --python python2.7 ~/virtualenvs/erudit
source ~/virtualenvs/erudit/bin/activate
pip install -r requirements.txt
```


## Run tests
```
nosetests
```


## Run log filtering

```
./extract/filter_logs.py data/150304.log result.log
```


