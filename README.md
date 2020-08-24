The nic.at crawler analysis library
----------------------------
A collection of tools that make analyzing web pages easier


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
```
# Clone the repository
> git clone https://github.com/nic-at/nic_crawler_analysis.git

# Change into the directory
> cd nic_crawler_analysis

# Install the requirements
> pip install -r requirements.txt

# Install the package itself
> python setup.py install
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