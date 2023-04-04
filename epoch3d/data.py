import sdf_helper as sh
import numpy as np
import os
from functools import reduce
from tqdm import tqdm

from epoch_post.epoch3d.utils import read_yaml, DotDict, UNIT_TRANSFORM

# ----------------------------- #

class Builder:

    DEFAULT_EXTRACT = [
        'Electric_Field_Ex',
        'Electric_Field_Ey',
        'Electric_Field_Ez',
        'Magnetic_Field_Bx',
        'Magnetic_Field_By',
        'Magnetic_Field_Bz',
        'Current_Density_Jx',
        'Current_Density_Jy',
        'Current_Density_Jz',
        'Grid_Grid',
        'Header'
    ]

    DEFAULT_PARTICLE_EXTRACT = [
        'Derived_Number_Density',
        'Derived_Temperature',
        'Derived_Average_Particle_Energy'
    ]

    FLAT_ATTRS = [
        'Header'
    ]

    TUPLE_ATTRS = [
        'Grid_Grid'
    ]

    DEFAULT_CONFIG_PATH = 'output-config.yml'
    UNIT_TRANSFORM = UNIT_TRANSFORM

    # ............................. #

    def build(
            
            self, 
            fpath: str, 
            config: str = None,
            verbose: bool = True
        
        ) -> dict:
        config = self._read_config(config)
        attrs, data = self._check_attributes(
                    fpath,
                    species=config.get('species', []),
                    extract=config.get('extract', []),
                    particle_extract=config.get('particle_extract', []),
                    verbose=verbose
                )
        
        if verbose: 
            print('Building data using attributes:\n')
            for k in attrs:
                print(f'  - {k}')
            print('\n')
        
        output = DotDict()
        iter_ = tqdm(attrs) if verbose else attrs
            
        for attr in iter_:
            snap = getattr(data, attr)
            snap = snap.data if attr not in Builder.FLAT_ATTRS else snap
            output[attr] = snap
        
        output['config'] = config
        
        del data, attrs

        return output
    
    # ............................. #

    @staticmethod
    def _read_config(path: str) -> object:
        return read_yaml(path or Builder.DEFAULT_CONFIG_PATH)
    
    # ............................. #
    
    @staticmethod
    def _read_sdf(path: str) -> object:
        return sh.getdata(path, verbose=False)

    # ............................. #

    def _check_attributes(
            
            self,
            path: str, 
            species: list = None, 
            extract: list = None, 
            particle_extract: list = None,
            verbose: bool = True
        
        ) -> list:

        probe = self._read_sdf(path)
        dct = probe.__dict__

        if verbose: 
            print('\nAvailable attributes:\n')
            for k in dct.keys():
                print(f'  - {k}')
            print('\n')
        
        extract = extract + Builder.DEFAULT_EXTRACT
        particle_extract = particle_extract + Builder.DEFAULT_PARTICLE_EXTRACT

        if species:
            particle_extract = reduce(lambda x, y: x + y, [[f'{pe}_{s}' for s in species] for pe in particle_extract])
        
        extract = list(filter(lambda x: hasattr(probe, x), extract))
        particle_extract = list(filter(lambda x: hasattr(probe, x), particle_extract))

        return extract + particle_extract, probe
    
# ----------------------------- #

class OptimizedBuilder(Builder):

    NO_VOLUME_ATTRS = Builder.FLAT_ATTRS + Builder.TUPLE_ATTRS + ['config', ]

    # ............................. #

    def optimize(
            
            self, 
            data: DotDict
        
        ) -> DotDict:
        
        new_output = DotDict()
        grid_minmax = self._get_gridminmax(data.Grid_Grid)
        new_output['grid_minmax'] = grid_minmax

        for k, v in data.items():
            if k.startswith('Particles_'):
                new_output[k] = self._optimize_p_v(v)

            elif k.startswith('Grid_Particles_'):
                new_output[k] = self._optimize_grid(v)

            elif k not in OptimizedBuilder.NO_VOLUME_ATTRS:
                print(k, '...')
                new_output[k] = self._optimize_volumes(v, data.config['volume_slices'], grid_minmax)

            else:
                new_output[k] = v
        
        return new_output

    # ............................. #

    def build(
            
            self, 
            *args,
            **kwargs

        ) -> DotDict:

        data = super().build(*args, **kwargs)
        data_opt = self.optimize(data)

        return data_opt

    # ............................. #

    @staticmethod
    def _optimize_grid(grid: tuple, scale: float = 1e-9) -> tuple:
        x, y, z = grid
        grid_new = x / scale, y / scale, z / scale

        return grid_new

    # ............................. #

    @staticmethod
    def _optimize_p_v(pv: np.ndarray, scale: float = 1) -> np.ndarray:
        c = 3e8 # light speed
        scaled = pv / (c * scale)

        return scaled

    # ............................. #

    @staticmethod
    def _get_gridminmax(grid: tuple) -> dict:
        xgrid, ygrid, zgrid = grid
        return {
            'x' : [min(xgrid), max(xgrid), len(xgrid)],
            'y' : [min(ygrid), max(ygrid), len(ygrid)],
            'z' : [min(zgrid), max(zgrid), len(zgrid)]
        }

    # ............................. #

    @staticmethod
    def _optimize_volumes(volume: np.ndarray, slices: dict, gridminmax: dict) -> dict:

        def _reshape_slice(x):
            if isinstance(x, list):
                return x
            elif isinstance(x, (dict, DotDict)):
                start = x['start']
                stop = x['stop']
                nstep = x['nstep']

                x = np.linspace(start, stop, nstep + 1, endpoint=True)
                return x
            
            else:
                raise ValueError

        # .................. #

        output = DotDict()

        unit = OptimizedBuilder.UNIT_TRANSFORM.get(slices['unit'], 1)

        for k, v in slices.items():
            if k == 'unit':
                continue

            minq, maxq, sizeq = gridminmax[k]
            v = _reshape_slice(v)
            sl = [x * unit for x in v]
            sl_idx = [
                int((x - minq) * sizeq / (maxq - minq)) 
                if (x <= maxq) and (x >= minq) 
                else None 
                for x in sl
            ]
            
            for raw, idx in zip(v, sl_idx):
                key = f'{k}_slice_{round(raw, 5)}_{slices["unit"]}'

                if idx is None:
                    continue
                elif idx < 0:
                    continue

                if k == 'x':
                    output[key] = volume[idx, :, :]
                
                elif k == 'y':
                    output[key] = volume[:, idx, :]
                
                elif k == 'z':
                    output[key] = volume[:, :, idx]

        return output