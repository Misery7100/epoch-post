import os
import json
from glob import glob
from tqdm import tqdm
import matplotlib.pyplot as plt

from epoch_post.epoch3d import OptimizedBuilder, plot_scalar_field, export_borderless
from epoch_post.epoch3d.utils import write_json

# ----------------------------- #

def postprocess(path: str, export_raw: bool = False, config_path: str = 'config-example.yml') -> None:

    builder3d = OptimizedBuilder()

    root_dir = path
    postprocess_dir = os.path.join(root_dir, 'postprocess')
    os.makedirs(postprocess_dir, exist_ok=True)

    sdf_files = glob(os.path.join(root_dir, '*.sdf'))

    metadict = {
        'postprocess_dir' : postprocess_dir
    }

    # TODO: move to config :/
    extract = ['Electric_Field_Ex', 'Current_Jx', 'Magnetic_Field_Bx']
    absval = [False, False, True]

    for sf in tqdm(sdf_files):
        data = builder3d.build(
            sf,
            config=config_path,
            verbose=False
        )
        fnum = os.path.split(sf)[-1]
        fnum = fnum.split('.')[0]

        metadict[fnum] = {
            'files' : {},
            'header' : data.Header
        }

        # plot scalar fields
        for param, isabs in zip(extract, absval):
            vector, component = param.split('_')[-1]

            for key in data[param].keys():
                fig, ax, metadata = plot_scalar_field(
                    data,
                    slice_=key,
                    vector=vector,
                    component=component,
                    forceabs=isabs,
                    for_export=export_raw,
                    scaler=1e-5 if vector == 'B' else 1
                )
                path = f'{param}_{key}'
                metadict[fnum]['files'][path] = metadata
                savedir = os.path.join(postprocess_dir, fnum)
                os.makedirs(savedir, exist_ok=True)
                export_borderless(fig, ax, os.path.join(savedir, path + '.jpg'))
                plt.close(fig)

                del ax, fig
        
        # plot densities
        # ...

        # plot phase spaces
        # ...

        del data
    
    # ...

    write_json(metadict, os.path.join(postprocess_dir, 'metadata.json'))

# ----------------------------- #

if __name__ == '__main__': #TODO: add run script based on postprocess function
    pass 