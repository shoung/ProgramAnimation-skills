"""A floating axonometric model on a bevel-edged block of sea."""

from lettering import titled
from miniature import render_set


@titled("isometric")
def frame(t):
    return render_set(t)
