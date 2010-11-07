"""
Views and functions for serving static files. These are only to be used
during development, and SHOULD NOT be used in a production setting.

modified from http://menendez.com/blog/using-django-as-pass-through-image-proxy/
to add authentication
"""

import mimetypes
import os
import posixpath
import urllib
import urllib2
from itertools import imap

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.static import serve as django_serve


def serve(request, path, document_root=None, show_indexes=False, cache=True,
          fallback_server=None, auth_user=None, auth_pass=None):
    """
    Serve static files using Django's static file function but if it returns a
    404, then attempt to find the file on the fallback_server. Optionally and by
    default, cache the file locally.
    
    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'static_fallback.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param (required by 
    Django). You may also set ``show_indexes`` to ``True`` if you'd like to 
    serve a basic index of the directory. These parameters are passed through
    directly to django.views.static.serve. You should see the doc_string there 
    for details.
    
    Passing cache to True (default) copies the file locally.
    
    Be sure to set settings.FALLBACK_STATIC_URL to something like:
    
    FALLBACK_STATIC_URL = 'http://myprodsite.com'
    
    Alternatively, you can also tell it the fallback server as a parameter
    sent in the URLs.
    
    Author: Ed Menendez (ed@menendez.com)
    Concept: Johnny Dobbins
    """

    # get out of the eway if the requested path does not start with any of the prefixes
    # specified in FALLBACK_STATIC_PREFIXES
    if not any(imap(path.startswith, getattr(settings, 'FALLBACK_STATIC_PREFIXES', []))):
        # let django take care of it
        return django_serve(request, path, document_root, show_indexes)
    
    if fallback_server is None:
        try:
            fallback_server = settings.FALLBACK_STATIC_URL
        except AttributeError:
            print u"You're using static_fallback.serve to serve static content " + \
                   "however settings.FALLBACK_STATIC_URL has not been set."

    try:
        u = settings.FALLBACK_STATIC_URL_USER
        p = settings.FALLBACK_STATIC_URL_PASS
        if auth_user is None and auth_pass is None:
            auth_user, auth_pass = u, p
    except AttributeError:
        pass
    
    # Save this for later to pass to Django.
    original_path = path
    
    # This was mostly copied from Django's version. We need the filepath for 
    # caching and it also serves as an optimization. If the file is not found
    # then there's no reason to go through the Django process.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)                    # RETURN
    fullpath = os.path.join(document_root, newpath)
    # End of the "mostly from Django" section.

    try:
        # Don't bother trying the Django function if the file isn't there.
        if not os.path.isdir(fullpath) and not os.path.exists(fullpath):
            raise Http404, '"%s" does not exist' % fullpath     # RAISE
        else:
            # Pass through cleanly to Django's verson
            return django_serve(                                # RETURN
                        request, original_path, document_root, show_indexes)
    except Http404:
        if fallback_server:
            # Attempt to find it on the remote server.
            path = request.path_info
            if path.startswith(settings.MEDIA_URL):
                path = path[len(settings.MEDIA_URL):]
            fq_url = '%s%s' % (fallback_server, path)
            print "fallback_serve: trying to fetch from %s" % fq_url
            try:
                handlers = []
                if auth_user or auth_pass:
                    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    passman.add_password(None, fallback_server, auth_user, auth_pass)
                    authhandler = urllib2.HTTPBasicAuthHandler(passman)
                    handlers.append(authhandler)
                opener = urllib2.build_opener(*handlers)
                contents = opener.open(fq_url).read()
            except urllib2.HTTPError, e:
                # Naive to assume a 404 - ed
                raise Http404, 'Cannot get %s - %s' % (fq_url, str(e))   # RAISE
            else:
                # Found the doc. Return it to response.
                mimetype = mimetypes.guess_type(fq_url)
                response = HttpResponse(contents, mimetype=mimetype[0])
                
                # Do we need to cache the file?
                if cache:
                    if not os.path.exists(os.path.split(fullpath)[0]):
                        os.makedirs(os.path.split(fullpath)[0])
                    f = open(fullpath, 'wb+')
                    f.write(contents)
                    f.close()
                
                # Success! We have the file. Send it back.
                return response                                 # RETURN
        else:
            # No fallback_server was defined. So, it's really a 404 now.
            raise Http404                                       # RAISE

