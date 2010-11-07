Fallback Media Server
=====================

This is a drop-in replacement Django's django.views.static.serve to fetch missing static files from
a preconfigured URL.

In addition, it also provides a file storage engine as a thin proxy for Django's default FileSystemStorage,
again fetching missing static files.


Settings
========

FALLBACK_STATIC_PREFIXES - a list of prefixes relative to MEDIA_URL (without the leading slash)

e.g.

FALLBACK_STATIC_PREFIXES = (
	'uploads/',
)



FALLBACK_STATIC_URL - the URL from which to fetch missing static files


FALLBACK_STATIC_URL_USER - if the FALLBACK_STATIC_URL requires HTTP basic authentication, this sets the username

FALLBACK_STATIC_URL_PASS - if the FALLBACK_STATIC_URL requires HTTP basic authentication, this sets the password


