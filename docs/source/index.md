The nic.at crawler analysis library
----------------------------
A collection of tools that make analyzing web pages easier.


Functionality
-------------
+ **language detection:** use a page's metadata and its content to determine the
    language a website is written in. [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) and [langdetect](https://github.com/Mimino666/langdetect) are used to do the
    analysis.
+ **script extraction:** extract the script tags from HTML code and classify them
    according to their content and where they are included from.

Dependencies and python 2.7 compatibility
-----------------------------------------
You can find the required dependencies of this library in requirements.txt. In
addition, the following modules can be installed for additional functionality:

+ [rfc3987](https://pypi.org/project/rfc3987/) and
  [regex](https://bitbucket.org/mrabarnett/mrab-regex/src/hg/) - for automatically
  removing URIs from text

Note, that even though this library is compatible to python 2.7 at this time,
this compatibility may be removed in the future. Use python 3 instead.

How to install the package
--------------------------
``` bash
# Clone the repository
git clone https://github.com/nic-at/nic-crawler-analysis.git

# Change into the directory
cd nic_crawler_analysis

# Install the requirements
pip install -r requirements.txt

# Install the package itself
python setup.py install
```

How to use the package
----------------------
nic_crawler_analysis library comes with a command line tool that analysis
an HTML page (nca_analyze_html). It prints its results as a json object to
stdout.
``` bash
# print the help message
nca_html_analyze -h

# You can

# ... fetch the HTML from the given URL and analyze it
nca_analyze_html --url https://nic.at
# {
#    "inputurl": "https://nic.at",
#    "language_blocks": {
#        "de": 0.9523809523809523,
#        "unk": 0.04761904761904767
#    },
#    "languages": {
#        "de": 0.9999965420010537
#    },
#    ...
# }

# ... read HTML from stdin:
echo "<html><body>Hello World!</body></html>" | nca_analyze_html
# {
#    "language_blocks": {
#        "en": 1.0
#    },
#    "languages": {
#        "en": 0.9999954921711693
#    },
#    "noscript_blocks": [],
#    "script_blocks": [],
#    "source": "stdin",
#    "text": "Hello World"
# }

# ... or fetch the HTML from a file:
nca_analyze_html -f index.html
```

If you want to use nic_crawler_analysis as a library you can find the API
documentation [here](modules.rst).
``` python
>>> import nic_crawler_analysis.analysis.lang_detect as nca_lang
>>> nca_lang.detect_languages("A sample text written for testing")
{'en': 0.9999962591031502}
```

Contents
--------
* [API Documentation](modules.rst)

License
-------
This package is distributed under the MIT License. See the LICENSE file that
comes with the package for further information.

Funded by
---------

This project was partially funded by the CEF framework

![Co-financed by the Connecting Europe Facility of the European Union](_static/en_cef-1024x146.png "Co-financed by the Connecting Europe Facility of the European Union")
