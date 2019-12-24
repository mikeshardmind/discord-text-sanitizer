import re

import ftfy
from bidi.algorithm import get_display

__all__ = ["preprocess_text", "sanitize_mass_mentions"]

# Trial and error based detection of characters which are dropped 100% of the time
discord_drop_re = re.compile(
    r"[\u202e|\ud800|\udb7f|\udb80|\udbff|\udc00|\udfff|\U000e0195-\U000e01ef]"
)

# Should detect well formed html tags.
html_tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")
mass_mention_sanitizer = re.compile(r"(@)(?=everyone|here)")


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


def sanitize_mass_mentions(text: str, *, run_preprocess: bool = True, **kwargs) -> str:
    """
    Parameters
    ----------
    text: str
        Text to sanitize

    Other Parameters
    ----------------
    run_preprocess: bool
        Normalize text using ``preprocess_text`` prior to sanitizing
        Default: True
    **kwargs:
        Passthrough kwargs for ``preproccess_text``
    """
    if run_preprocess:
        text = preprocess_text(text, **kwargs)
    return mass_mention_sanitizer.sub("@\u200b", text)
