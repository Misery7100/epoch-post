import matplotlib.pyplot as plt

from epoch_post.epoch3d.utils import DotDict, VECTOR_TO_NAME, VECTOR_TO_UNITS, UNIT_TRANSFORM

# ----------------------------- #

DEFAULT_DIVERGING = 'seismic'
DEFAULT_ABS = 'jet'

COLORMAPS = {
    'Electric_Field' : DEFAULT_DIVERGING,
    'Current_Density' : DEFAULT_DIVERGING,
    'Magnetic_Field' : DEFAULT_DIVERGING,
    'Number_Density' : 'hot',
    'Electric_Field_Abs' : DEFAULT_ABS,
    'Magnetic_Field_Abs' : DEFAULT_ABS,
    'Current_Density_Abs' : DEFAULT_ABS
}

# ----------------------------- #

def imshow_setup(data: DotDict, slice_: str, value: str, name: str, forceabs: bool):
    assert value in data.keys()
    assert slice_ in data[value].keys()

    vol = data[value][slice_]
    extent_key = slice_.split('_')[0]
    extent = []

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
    
    return vol, extent, vmin, vmax, cmap

# ----------------------------- #

def plot_vector_component(
        
        data: DotDict, 
        slice_: str, 
        vector: str = 'E',
        component: str = 'x', 
        forceabs: bool = False,
        scaler: float = 1.0

    ):

    name = VECTOR_TO_NAME[vector]
    vol, extent, vmin, vmax, cmap = imshow_setup(
                                    data, 
                                    slice_, 
                                    f'{name}_{vector}{component}',
                                    name, 
                                    forceabs
                                )
    
    fig, ax = plt.subplots(figsize=(10, 10))

    im = ax.imshow(
                vol * scaler,
                origin='lower', 
                extent=extent,
                cmap=cmap,
                vmin=vmin * scaler,
                vmax=vmax * scaler
            )
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(
        r'$' + f'{vector}_{component}' + r'$, ' + \
        VECTOR_TO_UNITS.get(vector, r'$\rm{c.u.}$'), 
        labelpad=15)

    return fig, ax

# ----------------------------- #

def plot_efield(data: DotDict, slice_: str, component: str = 'x', forceabs: bool = False):
    
    fig, ax = plot_vector_component(
        data, 
        slice_, 
        vector='E',
        component=component,
        forceabs=forceabs
    )

    return fig, ax

# ----------------------------- #

def plot_bfield(data: DotDict, slice_: str, component: str = 'x', forceabs: bool = False):
    
    fig, ax = plot_vector_component(
        data, 
        slice_, 
        vector='B',
        component=component,
        forceabs=forceabs,
        scaler=1e-5
    )

    return fig, ax

# ----------------------------- #

def plot_jfield(data: DotDict, slice_: str, component: str = 'x', forceabs: bool = False):
    
    fig, ax = plot_vector_component(
        data, 
        slice_, 
        vector='J',
        component=component,
        forceabs=forceabs
    )

    return fig, ax