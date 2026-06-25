"""Lazy exports for colour helpers."""

__all__ = [
	"_cscale_get_map",
	"_process_color_scales",
	"apply_colour_scale",
	"cbar",
	"cscale",
	"get_colour_scale_map",
]


def __getattr__(name):
	if name in __all__:
		from .colour import (
			_cscale_get_map,
			_process_color_scales,
			apply_colour_scale,
			cbar,
			cscale,
			get_colour_scale_map,
		)

		return {
			"_cscale_get_map": _cscale_get_map,
			"_process_color_scales": _process_color_scales,
			"apply_colour_scale": apply_colour_scale,
			"cbar": cbar,
			"cscale": cscale,
			"get_colour_scale_map": get_colour_scale_map,
		}[name]
	raise AttributeError(name)
