# -*- coding: utf-8 -*-

"""Wiki operations.

This module contains operations to effectively communicate with the
wiki.  It would be a kind of top-level manager with over-simplified
operations to get, create and update wiki pages.

"""

from evennia import AccountDB
from wiki.models import Article, ArticleRevision, URLPath

def get_URI(uri):
    """
    Return the wiki article (Article) to a given URI.

    Args:
        uri (str): the URI (a page URI).

    Returns:
        article (Article or None): the article, if found, or None.

    Example:
        article = get("/facts")

    """
    try:
        path = URLPath.get_by_path(uri)
    except URLPath.DoesNotExist:
        return None

    return path.article

def create(path, title, content, user=None, message=""):
    """
    Create a new wiki page.

    Args:
        path (str): the page's new path (must be unusued).
        title (str): the title of the new page.
        content (str): the new page's content.
        user (Account, optional): the new page's owner.
        message (str, optional): the new revision's message.

    Returns:
        article (Artidcle): the new article.

    Notes:
        If `user` is unset, use Account #1 (the superuser).
        If `slug` is unset, use the path.

        The provided path is an URL.  The parent is taken to be the
        one before the last '/' sign.  For example: 'a/b/c/' as a
        path would mean 'a/b' is taken to mean the parent, and 'c'
        is taken to be the article's new slug.

    """
    print "Try to create a wiki page..."
    path = path.strip("/")
    if "/" in path:
        parent_path, slug = path.rsplit("/", 1)
    else:
        parent_path = ""
        slug = path
    parent = URLPath.get_by_path(parent_path)

    user = user or AccountDB.objects.get(id=1)
    newpath = URLPath.create_article(
        parent,
        slug,
        title=title,
        content=content,
        user_message=message,
        user=user,
        ip_address="127.0.0.1",
        article_kwargs={'owner': user,
                        'group': None,
                        'group_read': True,
                        'group_write': True,
                        'other_read': False,
                        'other_write': False,
                        })

    return newpath.article

def update(article, content, user=None, message="", title=None):
    """
    Update an article, creating a new revision.

    Args:
        article (Article): the article object.
        content (str): the new content of the article.
        user (Account, optional): the user responsible for the update.
        message (str, optional): the message of the update.
        title (str, optional): the new article's title.

    Note:
        If `user` isn't set, get the account #1 (the superuser).
        If `title` is unset, will use the current article's title.

    """
    user = user or AccountDB.objects.get(id=1)
    current = article.current_revision
    title = title if title is not None else current.title
    revision = ArticleRevision()
    revision.inherit_predecessor(article)
    revision.title = title
    revision.content = content
    revision.user_message = message
    revision.deleted = False
    revision.ip_address = "127.0.0.1"
    article.add_revision(revision)
    return revision
