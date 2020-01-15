import re

import ftfy
from bidi.algorithm import get_display

__all__ = ["preprocess_text", "sanitize_mass_mentions"]

#: Trial and error based detection of characters which are dropped 100% of the time
discord_drop_re = re.compile(
    r"[\u202e|\ud800|\udb7f|\udb80|\udbff|\udc00|\udfff|\U000e0195-\U000e01ef]"
)

#: Should detect well formed html tags.
html_tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")

#: Trust the content source to not be intentionally abusing this
mass_mention_sanitizer = re.compile(r"@(?=everyone|here)")

#: Don't trust any character which couldn't be part of a user mention or role mention
aggresive_mass_mention_sanitizer = re.compile(r"@(?![0-9\u200b!&])")

#: Don't trust any character which couldn't be part of a user mention
roles_and_mass_mentions_sanitizer = re.compile(r"@(?![0-9\u200b!])")

#: This doesn't match all mentions, just all the ones which ping people
all_mention_sanitizer = re.compile(r"@(?!\u200b)")


def preprocess_text(
    text: str, *, strip_html: bool = False, fix_directional_overrides=True
) -> str:
    """
    Normalizes and fixes Unicode text
    drops any characters which are known to be dropped by discord.

    Parameters
    ----------
    text: str
        The text to normalize

    Other Parameters
    ----------------
    strip_html: bool
        Whether or not to strip html tags and normalize html entities
        Default: False
    fix_directional_overrides: bool
        Whether or not to render text with text overrides removed, equivalently
        Default: True

    Returns
    -------
    str
        The normalized text
    """

    if strip_html:
        text = html_tag_re.sub("", text)

    text = ftfy.fix_text(text, fix_entities=strip_html)

    if fix_directional_overrides:
        text = get_display(text)

    # If in case we still have any characters known to be dropped, drop them
    # For example, if we didn't fix directional overrides, they get dropped here.
    text = discord_drop_re.sub("", text)

    return text


def sanitize_mass_mentions(
    text: str,
    *,
    run_preprocess: bool = True,
    roles: bool = False,
    aggresive: bool = False,
    users: bool = False,
    **kwargs,
) -> str:
    """

    Because Discord refuses to handle unicode in any sane way,
    the only fully safe options will also break user mentions email addresses, etc
    because there's just no sane remaining way to do it.

    Options are provided based on your threat model to break as little as possible.

    https://github.com/discordapp/discord-api-docs/issues/1189
    
    https://github.com/discordapp/discord-api-docs/issues/1193

    https://github.com/discordapp/discord-api-docs/issues/1241
    
    https://github.com/discordapp/discord-api-docs/issues/1276
    

    Parameters
    ----------
    text: str
        Text to sanitize

    Other Parameters
    ----------------
    run_preprocess: bool
        Normalize text using ``preprocess_text`` prior to sanitizing
        Default: True
    aggresive: bool
        Don't trust the content source not to be abusive, will more agressively add
        non breaking spaces
        Default: False
    roles: bool
        Don't allow role mentions either.
        Default: False
    users: bool
        Don't allow user mentions either. This is shorthand for @ -> @\u200b
        And will break role mentions in the process as roles mention users.
        Default: False
    **kwargs:
        Passthrough kwargs for ``preproccess_text``
    """
    if run_preprocess:
        text = preprocess_text(text, **kwargs)
    if users:
        return all_mention_sanitizer.sub("@\u200b", text)
    if roles:
        return roles_and_mass_mentions_sanitizer.sub("@\u200b", text)
    if aggresive:
        return aggresive_mass_mention_sanitizer.sub("@\u200b", text)
    return mass_mention_sanitizer.sub("@\u200b", text)
