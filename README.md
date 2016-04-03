# SurfaceImageContentGap
[![Build Status](https://travis-ci.org/Commonists/SurfaceImageContentGap.svg?branch=master)](https://travis-ci.org/Commonists/SurfaceImageContentGap)
[![Coverage Status](https://codecov.io/github/Commonists/SurfaceImageContentGap/coverage.svg?branch=master)](https://codecov.io/github/Commonists/SurfaceImageContentGap?branch=master)
[![Code Health](https://landscape.io/github/Commonists/SurfaceImageContentGap/master/landscape.svg?style=flat)](https://landscape.io/github/Commonists/SurfaceImageContentGap/master)
[![License](http://img.shields.io/badge/license-MIT-orange.svg?style=flat)](http://opensource.org/licenses/MIT)

R&amp;D project to surface articles with most views that are lacking illustration on Wikipedia. Currently it supports two kind of search, searching articles without images given from a category or including a given template.

Usage
-----
Searching articles from a given category without picture.
```sh
python imagegap.py -c "French long-distance runners" -w en \
        -r "User:PierreSelim/RunnerReport" -f myconfig.cfg
```
Searching articles with a given template without picture
```sh
python imagegap.py -t "Infobox Rugbyman" -w en \
        -r "User:PierreSelim/Rugbyman" -f myconfig.cfg
```

The configuration file should contain the login and password of your bot to the wikimedia project
```cfg
[login]
user = foo
password = bar
```
