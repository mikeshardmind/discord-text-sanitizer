# discord-text-sanitizer
Text sanitization suitable for discord bots. 


### Quick Start

```py
import discordtextsanitizer as dts

# If using a library which already handles raw @everyone and @here mentions
discord_safer = dts.preprocess_text(unsafe_content)

# If interacting directly
discord_safest = dts.sanitize_mass_mentions(unsafe_content, run_preprocess=True)

# Want to cleanup html tag and replace entities?
# (included for fuller sanitization of web fetched content for discord)

via_lib = dts.preprocess_text(unsafe_content, strip_html=True)
# or
direct_interaction = dts.sanitize_mass_mentions(unsafe_content, strip_html=True, run_preprocess=True)
```

### Why?

Discord sanitizes text, silently changing messages.

The process they use isn't fully documented, and their sanitizer has not been disclosed or open sourced.

This leaves the otherwise correct solutions for filtering mass mentions as not working as people would expect.

### Why not use this?

If you are only sending in embeds or sending from message content, you probably don't need this.
In the first case, embeds don't cause pings, at worst you might get some malformed messages.
In the second, you are reading input which has already been through the undocumented sanitization.

### So how does this work without a documented set of steps from Discord?

After some trial and error, I have a list of characters which Discord removes consistently.

There were many characters dropped inconsistently.

I've also found that I couldn't cause NFC normalized unicode to drop anything other than
the characters which were dropped consistently.
However, this includes right to left overrides, which may be useful for globaly sourced content.

Rather than reimplement NFC normalization, and directional override removal, this uses two
well supported libraries which handle this, then removes any remaining characters which
Discord is known to drop silently

### What to do if you find something this doesn't handle.

Open an issue with details, or a PR with a fix and a sample of text it fixes,
I'll be happy to include it.

I'd prefer this not be neccessary at all, but until such a time where that's the case,
cooperation among developers who may be impacted by this is great.
