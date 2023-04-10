import matplotlib.pyplot as plt

from epoch_post.epoch3d.utils import DotDict, VECTOR_TO_NAME, VECTOR_TO_UNITS, UNIT_TRANSFORM, UNIT_SHORT

# ----------------------------- #

DEFAULT_DIVERGING = 'seismic'
DEFAULT_ABS = 'jet'

COLORMAPS = {
    'Electric_Field' : DEFAULT_DIVERGING,
    'Current_Density' : DEFAULT_DIVERGING,
    'Magnetic_Field' : DEFAULT_DIVERGING,
    'Number_Density_Abs' : 'hot',
    'Electric_Field_Abs' : DEFAULT_ABS,
    'Magnetic_Field_Abs' : DEFAULT_ABS,
    'Current_Density_Abs' : DEFAULT_ABS
}

# ----------------------------- #

def imshow_setup(data: DotDict, slice_: str, value: str, name: str, forceabs: bool):
    assert value in data.keys(), f'{value} not in data keys'
    assert slice_ in data[value].keys(), f'{slice_} not in data.{value} keys'

    vol = data[value][slice_]
    extent_key = slice_.split('_')[0]
    extent = []
    axes = ['x', 'y', 'z']
    axes.pop(axes.index(extent_key))
    labels = [
        r'$' + x + r'$, ' + UNIT_SHORT[data.config.volume_slices.unit] 
        for x in axes
    ][::-1]

    for k, v in data.grid_minmax.items():
        if k == extent_key:
            continue

        minq, maxq, _ = v
        extent.extend([minq, maxq])
    
    units = UNIT_TRANSFORM.get(data.config.volume_slices.unit, 1)
    extent = [x / units for x in extent]
    
    if forceabs:
        vmin = 0
        vmax = abs(vol).max()
        cmap = COLORMAPS.get(f'{name}_Abs', DEFAULT_ABS)
    
    else:
        mx = abs(vol).max()
        vmin, vmax = -mx, mx
        cmap = COLORMAPS.get(name, DEFAULT_DIVERGING)
    
    return vol, extent, vmin, vmax, cmap, labels

# ----------------------------- #

def plot_scalar_field(
        
        data: DotDict, 
        slice_: str, 
        vector: str = 'E',
        component: str = 'x', 
        forceabs: bool = False,
        scaler: float = 1.0,
        for_export: bool = False

    ):

    name = VECTOR_TO_NAME[vector]
    vol, extent, vmin, vmax, cmap, labels = imshow_setup(
                                    data, 
                                    slice_, 
                                    f'{name}_{vector}{component}',
                                    name, 
                                    forceabs
                                )
    
    metadata = {
        'vmin' : vmin,
        'vmax' : vmax,
        'scaler' : scaler,
    }
    
    fig, ax = plt.subplots(
                    figsize=(10, 10), 
                    frameon=not for_export
                )

    im = ax.imshow(
                vol * scaler,
                origin='lower', 
                extent=extent,
                cmap=cmap,
                vmin=vmin * scaler,
                vmax=vmax * scaler
            )

    if for_export:
        plt.axis('off')

    else:
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.1)
        cbar.set_label(
            r'$' + f'{vector}_{component}' + r'$, ' + \
            VECTOR_TO_UNITS.get(vector, r'$\rm{c.u.}$'), 
            labelpad=15)

        ax.set_xlabel(labels[0], labelpad=15)
        ax.set_ylabel(labels[1], labelpad=15)

    return fig, ax, metadata

# ----------------------------- #

def plot_density(data: DotDict, slice_: str):
    pass

# ----------------------------- #

def plot_temperature(data: DotDict, slice_: str):
    pass

# ----------------------------- #

def plot_efield(
        
        data: DotDict, 
        slice_: str, 
        component: str = 'x', 
        forceabs: bool = False,
        **kwargs

    ):
    
    fig, ax, metadata = plot_scalar_field(
        data, 
        slice_, 
        vector='E',
        component=component,
        forceabs=forceabs,
        **kwargs
    )

    return fig, ax, metadata

# ----------------------------- #

def plot_bfield(
        
        data: DotDict, 
        slice_: str, 
        component: str = 'x', 
        forceabs: bool = False,
        **kwargs
    
    ):
    
    fig, ax, metadata = plot_scalar_field(
        data, 
        slice_, 
        vector='B',
        component=component,
        forceabs=forceabs,
        scaler=1e-5, # force GGs: 
                    # 1e4 (from Ts to Gs) * 1e-9 (from Gs to GGs)
        **kwargs
    )

    return fig, ax, metadata

# ----------------------------- #

def plot_jfield(
        
        data: DotDict, 
        slice_: str, 
        component: str = 'x', 
        forceabs: bool = False,
        **kwargs
    
    ):
    
    fig, ax, metadata = plot_scalar_field(
        data, 
        slice_, 
        vector='J',
        component=component,
        forceabs=forceabs,
        **kwargs
    )

    return fig, ax, metadata