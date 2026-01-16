from .classdiagram import render_classdiagram, render_header_classdiagram

RENDERERS = {
    "classDiagram": (render_classdiagram, render_header_classdiagram)
}