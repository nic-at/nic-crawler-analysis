# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from urllib.parse import urlparse
from tldextract import extract as tld_extract

from future import standard_library
from past.builtins import basestring
from ..util.misc import analyze_path

standard_library.install_aliases()

KNOWN_SCRIPT_MIME_TYPES = {
    "text/javascript": "js",
    "application/javascript": "js",
    "application/json": "json",
    "application/ld+json": "json",
    "application/gem+json": "json",
    "text/template": "template",
    "text/x-template": "template",
    "text/html": "html",
    "text/plain": "text",
    "text/xml": "xml",
}


def analyze_js_source(domain, input_):
    """Find the type of source of the javascript tags that are given as input.

    Classifies the source of a script tag into internal and external includes
    and into inline scripts.

    If external resources are loaded via a 'src' attribute it is determined
    whether the resources are loaded from the same page ('include-local') or
    ('include-external'). Resources that are loaded from the same domain
    (including subdomains) are also identified as 'include-local'.

    The dicts returned contain the following keys:

    * type
        one of 'inline-js', 'inline-unknown', 'inline-json', 'include-local',
        or 'include-external'
    * src *(for type == include-\*)*
        the full included path
    * src_path *(for type == include-\*)*
        relative path to included resource
    * 'src_domain' *(for type == include-external)*
        domain from which resource is included
    * 'content' *(for type == inline-\*)*
        content of the script tag


    Parameters
    ----------
    domain : str
        Domain the tags have been scraped from. Used to detect whether scripts
        are local or external includes. Expects the domain to be given up to
        the second level (e.g. domain="nic.at").
    input_ : list of (dict,str)
        List of script tags to analyze where the dictionary contains
        the attributes of the tag and the str the text of the tag.

    Returns
    -------
    js_code : list of dict
        the script sources found. Each dict describes a single <script> tag
        found. The keys are:

    """
    sources = []
    try:
        for attrs, text in input_:
            result = {}
            if "src" in attrs:
                # These are (possibly external) includes
                url = attrs["src"]
                result["src"] = url
                p_url = urlparse(url)
                result["src_path"] = p_url.path
                if p_url.netloc:
                    o_tld = tld_extract(p_url.netloc)
                    script_domain = o_tld.domain + "." + o_tld.suffix
                    if script_domain == domain:
                        result["type"] = "include-local"
                    else:
                        result["type"] = "include-external"
                        result["src_domain"] = script_domain
                else:
                    if result["src_path"].startswith("./"):
                        result["src_path"] = \
                            result["src_path"].replace("./", "/", 1)
                    result["type"] = "include-local"
            else:
                result["content"] = text
                # if tag has no type attr it is assumed text/javascript
                if "type" not in attrs:
                    result["type"] = "inline-js"
                elif (
                    isinstance(attrs["type"], basestring)
                    and (attrs["type"].lower() in KNOWN_SCRIPT_MIME_TYPES)
                ):
                    result["type"] = "inline-%s" % (
                        KNOWN_SCRIPT_MIME_TYPES[attrs["type"].lower()]
                    )
                else:
                    result["type"] = "inline-unknown"
            sources.append(result)
    except TypeError:
        raise ValueError("could not iterate over input_ "
                         "- expected list of tuples (dict,str) - %s")
    return sources


def analyze_js_path(path):
    """Analyze the include path given under the assumption that it is a
    javascript include.

    Expects the path of a script excluding the domain it is loaded from, e.g.
    path="/include/script.js".

    See the documentation for
    :func:`~nic_crawler_analysis.util.misc.analyze_path` for the fields that
    are returned.

    Parameters
    ----------
    path : str
        include path to be analyzed

    Returns
    -------
    analysis : dict
        Analysis of the include path
    """
    path_analysis = analyze_path(path)

    return path_analysis
