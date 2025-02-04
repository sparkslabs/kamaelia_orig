---
pagename: Components/pydoc/Kamaelia.Util.PureTransformer
last-modified-date: 2009-06-05
page-template: default
page-type: text/markdown
page-status: current|legacy|needsupdate|deprecated|recommended
---
::: {.container}
::: {.section}
[Kamaelia](/Components/pydoc/Kamaelia.html){.reference}.[Util](/Components/pydoc/Kamaelia.Util.html){.reference}.[PureTransformer](/Components/pydoc/Kamaelia.Util.PureTransformer.html){.reference}
====================================================================================================================================================================================================
:::

::: {.section}
::: {.container}
-   **component
    [PureTransformer](/Components/pydoc/Kamaelia.Util.PureTransformer.PureTransformer.html){.reference}**
:::

-   [Pure Transformer component](#223){.reference}
    -   [Example Usage](#224){.reference}
:::

::: {.section}
Pure Transformer component {#223}
==========================

This component applies a function specified at its creation to messages
received (a filter). If the function returns None, no message is sent,
otherwise the result of the function is sent to \"outbox\".

::: {.section}
[Example Usage]{#example-usage} {#224}
-------------------------------

To read in lines of text, convert to upper case and then write to the
console:

``` {.literal-block}
Pipeline(
    ConsoleReader(),
    PureTransformer(lambda x : x.upper()),
    ConsoleEchoer()
).run()
```
:::
:::

------------------------------------------------------------------------

::: {.section}
[Kamaelia](/Components/pydoc/Kamaelia.html){.reference}.[Util](/Components/pydoc/Kamaelia.Util.html){.reference}.[PureTransformer](/Components/pydoc/Kamaelia.Util.PureTransformer.html){.reference}.[PureTransformer](/Components/pydoc/Kamaelia.Util.PureTransformer.PureTransformer.html){.reference}
========================================================================================================================================================================================================================================================================================================

::: {.section}
class PureTransformer([Axon.Component.component](/Docs/Axon/Axon.Component.component.html){.reference}) {#symbol-PureTransformer}
-------------------------------------------------------------------------------------------------------

::: {.section}
### [Inboxes]{#symbol-PureTransformer.Inboxes}
:::

::: {.section}
### [Outboxes]{#symbol-PureTransformer.Outboxes}
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
#### [\_\_init\_\_(self\[, function\])]{#symbol-PureTransformer.__init__}
:::

::: {.section}
#### [main(self)]{#symbol-PureTransformer.main}
:::

::: {.section}
#### [processMessage(self, msg)]{#symbol-PureTransformer.processMessage}
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
