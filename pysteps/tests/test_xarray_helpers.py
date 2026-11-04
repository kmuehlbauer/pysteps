from pysteps.tests.helpers import get_precipitation_fields
from pysteps.xarray_helpers import validate_dataset

def test_simple_xarray():
    from pysteps_data import DATASETS
    import xarray as xr
    fname = "radar/fmi/geotiff/20160928/201609281445_FINUTM.tif"
    fname = DATASETS.fetch(fname)
    ds = xr.open_dataset(fname, engine="rasterio")
    print(ds)
    import wradlib
    print(wradlib.georef.ensure_crs(ds.spatial_ref.attrs["crs_wkt"]).to_proj4())
    print(ds.band_data)
    assert 1 == 2

def test_pysteps_data():
    from pysteps_data import DATASETS, locate
    print(locate())
    print(DATASETS.registry_files)
    assert 1 == 2


# in tests helpers there are already asserts like
# assert_dataset_equivalent(

def test_validate_dataset() -> None:
    precip_dataset = get_precipitation_fields(
        num_prev_files=0,
        num_next_files=0,
        return_raw=True,
        source="knmi",
        log_transform=False,
        qty="ACRR",
    )
    validate_dataset(precip_dataset)


def test_validate_xradar_dataset() -> None:
    precip_dataset = get_precipitation_fields(
        num_prev_files=0,
        num_next_files=0,
        return_raw=True,
        source="knmi",
        log_transform=False,
        qty="ACRR",
    )

    precip_dataset.attrs = {}
    #precip_dataset = precip_dataset.drop_vars(precip_dataset.coords)
    precip_dataset.precip_accum.attrs = {}
    precip_dataset = precip_dataset.rename(precip_accum="data", time="vcp_time")
    import pyproj
    print(pyproj.CRS.from_user_input(precip_dataset["polar_stereographic"].attrs))
    print(pyproj.CRS.from_cf(precip_dataset["polar_stereographic"].attrs))

    print(precip_dataset["polar_stereographic"])

    precip_dataset["data"].attrs = {
        "standard_name": "rainfall_rate",
        "long_name": "Rain rate composite from Marshall-Palmer Z-R",
        # CF's canonical units for rainfall_rate are kg m-2 s-1; mm h-1 is the conventional
        # radar-QPE form and assumes a water density of 1000 kg m-3 (1 mm h-1 = 2.778e-4).
        "units": "mm h-1",
        "grid_mapping": "spatial_ref",
        "cell_methods": "radar: maximum",
        "zr_a": 200.0,
        "zr_b": 1.6,
    }
    precip_dataset["x"].attrs = {
        "standard_name": "projection_x_coordinate",
        "long_name": "Easting",
        "units": "m",
        "axis": "X",
    }
    precip_dataset["y"].attrs = {
        "standard_name": "projection_y_coordinate",
        "long_name": "Northing",
        "units": "m",
        "axis": "Y",
    }
    precip_dataset["vcp_time"].attrs = {"standard_name": "time", "long_name": "Volume time", "axis": "T"}

    # rioxarray writes the CF grid mapping variable (grid_mapping_name, crs_wkt, datum
    # parameters) so the projection is carried inside the store.
    #precip_dataset = precip_dataset.rio.write_crs(proj_laea, grid_mapping_name="spatial_ref")

    precip_dataset.attrs = {
        "Conventions": "CF-1.10",
        "title": "gridded radar composite rain rate",
        "institution": "Open Radar Science Short Course, ERAD2026",
        "source": "pysteps source data with xradar attributes",
        "history": "some history here",
    }
    print(precip_dataset)
    validate_dataset(precip_dataset)
    assert 1 == 2
