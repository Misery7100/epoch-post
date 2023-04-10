import matplotlib.pyplot as plt

# ----------------------------- #

def export_borderless(fig, ax, path: str):
    # extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(path, bbox_inches='tight', pad_inches=0, transparent=False, dpi=400)

# ----------------------------- #