---
pagename: Components/pydoc/Kamaelia.Visualisation.PhysicsGraph.GridRenderer
last-modified-date: 2009-06-05
page-template: default
page-type: text/markdown
page-status: current|legacy|needsupdate|deprecated|recommended
---
::: {.container}
::: {.section}
[Kamaelia](/Components/pydoc/Kamaelia.html){.reference}.[Visualisation](/Components/pydoc/Kamaelia.Visualisation.html){.reference}.[PhysicsGraph](/Components/pydoc/Kamaelia.Visualisation.PhysicsGraph.html){.reference}.[GridRenderer](/Components/pydoc/Kamaelia.Visualisation.PhysicsGraph.GridRenderer.html){.reference}
=============================================================================================================================================================================================================================================================================================================================
:::

::: {.section}
::: {.container}
:::

-   [Grid Renderer](#432){.reference}
    -   [Example Usage](#433){.reference}
    -   [How does it work?](#434){.reference}
:::

::: {.section}
Grid Renderer {#432}
=============

Renderer for the topology viewer framework that renders horizontal and
vertical gridlines on pass -1.

::: {.section}
[Example Usage]{#example-usage} {#433}
-------------------------------

Already used by
[Kamaelia.Visualisation.PhysicsGraph.TopologyViewer](/Components/pydoc/Kamaelia.Visualisation.PhysicsGraph.TopologyViewer.html){.reference}.

Rendering a grid in light grey with grid cell size of 100x100:

``` {.literal-block}
grid = GridRenderer(size=100, colour=(200,200,200))
renderer = grid.render( <pygame surface> )
for rendering_pass in renderer:
  print "Rendering for pass ", rendering_pass
```
:::

::: {.section}
[How does it work?]{#how-does-it-work} {#434}
--------------------------------------

Instances of this class provide a render() generator that renders
horizontal and vertical grid lines to conver the specified pygame
surface. The colour and spacing of the grid lines are specified at
initialisation.

Rendering is performed by the generator, returned when the render()
method is called. Its behaviour is that needed for the framework for
multi-pass rendering that is used by TopologyViewer.

The generator yields the number of the rendering pass it wishes to be
next on next. Each time it is subsequently called, it performs the
rendering required for that pass. It then yields the number of the next
required pass or completes if there is no more rendering required.

A setOffset() method is also implemented to allow the rendering position
to be offset. This therefore makes it possible to scroll the grid around
the display surface.

See TopologyViewer for more details.
:::
:::

------------------------------------------------------------------------

::: {.section}
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
