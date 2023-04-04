# EPOCH Postprocessing

Simplify postprocessing for EPOCH sdf files

## Usage

```python
from epoch_post.epoch3d import OptimizedBuilder
from epoch_post.epoch3d import plot_bfield

builder3d = OptimizedBuilder()

data = builder3d.build(
    '0004.sdf',
    config='./epoch_post/config-example.yml',
    verbose=True
)

fig, ax = plot_bfield(
    data,
    slice_='z_slice_0.0_micro',
    component='x',
    forceabs=True
)
```
