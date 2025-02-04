---
pagename: Components/pydoc/Kamaelia.Audio.Codec.PyMedia.Encoder
last-modified-date: 2009-06-05
page-template: default
page-type: text/markdown
page-status: current|legacy|needsupdate|deprecated|recommended
---
::: {.container}
::: {.section}
[Kamaelia](/Components/pydoc/Kamaelia.html){.reference}.[Audio](/Components/pydoc/Kamaelia.Audio.html){.reference}.[Codec](/Components/pydoc/Kamaelia.Audio.Codec.html){.reference}.[PyMedia](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.html){.reference}.[Encoder](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.Encoder.html){.reference}
=================================================================================================================================================================================================================================================================================================================================================
:::

::: {.section}
::: {.container}
-   **component
    [Encoder](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.Encoder.Encoder.html){.reference}**
:::

-   [Audio encoding using PyMedia](#546){.reference}
    -   [Example Usage](#547){.reference}
    -   [How does it work?](#548){.reference}
:::

::: {.section}
Audio encoding using PyMedia {#546}
============================

Encodes raw audio data sent to its \"inbox\" inbox and outputs the
compressed audio data from its \"outbox\" outbox. Decoding done using
the PyMedia library.

::: {.section}
[Example Usage]{#example-usage} {#547}
-------------------------------

Capturing to an MP3 file:

``` {.literal-block}
Pipeline( Input(44100, 2, "S16_LE"),
          Encoder("mp3", bitrate=128000, sample_rate=44100, channels=2)
        ).run()
```
:::

::: {.section}
[How does it work?]{#how-does-it-work} {#548}
--------------------------------------

Set up Encoder by specifying the desired compression codec and bitrate
and the sample rate and number of channels of the raw audio. You may
also specify other parameters specific to pymedia and the particular
codec.

Send raw binary data strings containing the raw audio data to the
\"inbox\" inbox, and raw binary data strings containing the compressed
audio data will be sent out of the \"outbox\" outbox.

Encoder only supports a sample format of \"S16\_LE\".

This component will terminate if a shutdownMicroprocess or
producerFinished message is sent to the \"control\" inbox. The message
will be forwarded on out of the \"signal\" outbox just before
termination.
:::
:::

------------------------------------------------------------------------

::: {.section}
[Kamaelia](/Components/pydoc/Kamaelia.html){.reference}.[Audio](/Components/pydoc/Kamaelia.Audio.html){.reference}.[Codec](/Components/pydoc/Kamaelia.Audio.Codec.html){.reference}.[PyMedia](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.html){.reference}.[Encoder](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.Encoder.html){.reference}.[Encoder](/Components/pydoc/Kamaelia.Audio.Codec.PyMedia.Encoder.Encoder.html){.reference}
============================================================================================================================================================================================================================================================================================================================================================================================================================================

::: {.section}
class Encoder([Axon.Component.component](/Docs/Axon/Axon.Component.component.html){.reference}) {#symbol-Encoder}
-----------------------------------------------------------------------------------------------

Encoder(codec,bitrate,sample\_rate,channels,\*\*otherparams) -\> new
Encoder component.

Send raw audio data to the \"inbox\" inbox, and compressed audio data
will be sent out of the \"outbox\" outbox.

Keyword arguments:

-   codec \-- which codec to use, eg \"MP3\"
-   bitrate \-- desired bitrate, eg 128000 for 128kbps
-   sample\_rate \-- sample rate in Hz of the raw audio
-   channels \-- number of channels of the raw audio
-   otherparams \-- any other keyword arguments to be passed direct to
    PyMedia

::: {.section}
### [Inboxes]{#symbol-Encoder.Inboxes}

-   **control** : Shutdown signalling
-   **inbox** : Raw binary audio data as strings
:::

::: {.section}
### [Outboxes]{#symbol-Encoder.Outboxes}

-   **outbox** : NOT USED
-   **signal** : Shutdown signalling
:::

::: {.section}
### Methods defined here

::: {.container}
::: {.boxright}
**Warning!**

You should be using the inbox/outbox interface, not these methods
(except construction). This documentation is designed as a roadmap as to
their functionalilty for maintainers and new component developers.
:::
:::

::: {.section}
#### [\_\_init\_\_(self, codec, bitrate, sample\_rate, channels, \*\*otherparams)]{#symbol-Encoder.__init__}

x.\_\_init\_\_(\...) initializes x; see x.\_\_class\_\_.\_\_doc\_\_ for
signature
:::

::: {.section}
#### [main(self)]{#symbol-Encoder.main}
:::
:::

::: {.section}
:::
:::
:::
:::

::: {.section}
Feedback
========

Got a problem with the documentation? Something unclear that could be
clearer? Want to help improve it? Constructive criticism is very welcome
- especially if you can suggest a better rewording!

Please leave you feedback
[here](../../../cgi-bin/blog/blog.cgi?rm=viewpost&nodeid=1142023701){.reference}
in reply to the documentation thread in the Kamaelia blog.
:::

*\-- Automatic documentation generator, 05 Jun 2009 at 03:01:38 UTC/GMT*
