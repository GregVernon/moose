import argparse
import json
import math
import os
from pathlib import Path

from coreform_utils import import_cubit, get_coreform_paths, run_command


path_to_this_script = Path( __file__ ).resolve().parent
output_prefix = "meshed_cframe_moose"


def main( args ):
    args.work_dir = args.work_dir.expanduser().resolve()
    args.work_dir.mkdir( parents=True, exist_ok=True )

    if args.mesh_mode == "boundingbox":
        args.mesh_mode = "immersed"
    if args.mesh_mode != "immersed":
        raise ValueError(
            "The new Coreform IGA Exodus workflow currently supports only immersed meshes. "
            f"You provided: {args.mesh_mode}"
        )
    if ( args.num_moose_proc != 1 ) and not args.skip_moose:
        raise ValueError(
            "The current implementation in MOOSE for trimmed meshes only supports LU linear "
            f"solvers, which are limited to serial processing (1 CPU). You provided: {args.num_moose_proc}"
        )

    coreform_paths = get_coreform_paths( args )
    source_cf, build_cf_options = run_cubit( args, coreform_paths )
    mesh_cf = run_build_cf( args, coreform_paths, source_cf, build_cf_options )
    mesh_sql = run_iga_mesh( args, coreform_paths, mesh_cf )
    run_interop( args, coreform_paths, mesh_cf, mesh_sql )
    if not args.skip_moose:
        run_moose( args )


def run_cubit( args, coreform_paths ):
    ## This routine verified to run with Coreform Cubit 2025.10
    cubit = import_cubit(
        verbose=args.verbose_cubit,
        cubit_python_module_path=coreform_paths["cubit_path"],
    )
    original_cwd = Path.cwd()

    try:
        os.chdir( args.work_dir )
        cubit.cmd( "reset" )

        ## Import geometry
        cubit.cmd( f'import step "{path_to_this_script / "c-frame.step"}" noheal' )

        ## Assign sets for boundary and load conditions
        cubit.cmd( f"create vertex on curve 12 73  distance {1.575 + 0.025} from surface 74" )
        cubit.cmd( f"create vertex on curve 17 78  distance {1.575 + 0.025} from surface 72" )
        cubit.cmd( "split surface 63  across location vertex 117  location vertex 118" )
        cubit.cmd( "split surface 97  across location vertex 119  location vertex 120" )
        cubit.cmd( "delete vertex all" )
        cubit.cmd( "block 1 volume 1" )
        cubit.cmd( 'block 1 name "cframe"' )
        cubit.cmd( "sideset 1 surface 102" )
        cubit.cmd( 'sideset 1 name "load_surface"' )
        cubit.cmd( "sideset 2 surface 103" )
        cubit.cmd( 'sideset 2 name "hold_surface"' )

        ## Define the background immersed mesh from the CAD bounding box
        bbox = [ float( value ) for value in list( cubit.get_total_bounding_box( "volume", cubit.get_entities( "volume" ) ) ) ]
        bbox_min = [ bbox[0], bbox[3], bbox[6] ]
        bbox_max = [ bbox[1], bbox[4], bbox[7] ]

        frame_origin = []
        extent_padding = []
        for axis, nudge_factor in enumerate( ( 0.07, 0.11, 0.13 ) ):
            length = bbox_max[axis] - bbox_min[axis]
            interval_count = int( math.ceil( length / args.mesh_size ) )
            resolved_length = interval_count * args.mesh_size
            padding = 0.5 * ( resolved_length - length )
            frame_origin.append( bbox_min[axis] - padding + args.mesh_size * nudge_factor )
            extent_padding.append( padding )

        build_cf_options = {
            "defaults": {
                "padding": args.degree,
                "small_cell_volume_ratio": args.small_cell_volume_ratio,
                "extension_max_generations": args.extension_max_generations,
                "trimming_options": { "tessellation_option": "trim_tess" },
                "element_layout": [ "node_centered", "node_centered", "node_centered" ],
                "frame_origin": frame_origin,
                "extent_padding": extent_padding,
            },
            "tessellation_options": [
                {
                    "label": "trim_tess",
                    "meshgems": {
                        "average_triangle_edge_subdivisions": 3,
                        "max_triangle_edge_physical_length": args.mesh_size,
                        "angle_refinement": {
                            "max_refinement_count": 2,
                            "max_edge_ratio": 0.15,
                        },
                    },
                }
            ],
        }

        ## Save Coreform Cubit file for potential debugging
        cubit.cmd( f'save cub5 "{args.work_dir / "cframe.cub5"}" overwrite' )

        ## Export the Coreform file that build_cf.py will convert for IGA meshing
        source_cf = args.work_dir / "cframe_geom.cf"
        cubit.cmd( f'export coreform "{source_cf}" overwrite' )
    finally:
        os.chdir( original_cwd )
        if hasattr( cubit, "destroy" ):
            cubit.destroy()

    return source_cf, build_cf_options


def run_build_cf( args, coreform_paths, source_cf, build_cf_options ):
    options_json = args.work_dir / "cframe_build_cf_options.json"
    options_json.write_text( json.dumps( build_cf_options, indent=2 ) + "\n", encoding="utf-8" )

    mesh_cf = args.work_dir / "cframe_geom_meshing.cf"
    command = (
        f'"{coreform_paths["build_cf_python"]}" "{coreform_paths["build_cf"]}" '
        f'"{source_cf}" "{mesh_cf}" '
        f'--cubit-python-module-path "{coreform_paths["cubit_path"]}" '
        f'--degree {args.degree} '
        f'--element-size {args.mesh_size} '
        f'--options-json "{options_json}"'
    )
    run_command( command, cwd=args.work_dir, env=coreform_paths["build_cf_env"] )
    return mesh_cf


def run_iga_mesh( args, coreform_paths, mesh_cf ):
    mesh_sql = args.work_dir / f"{output_prefix}.sql"
    if args.num_mesh_proc > 1:
        command = f'"{coreform_paths["mpiexec"]}" -n {args.num_mesh_proc} "{coreform_paths["iga_mesh"]}" "{mesh_cf}" --output-db "{mesh_sql}"'
    else:
        command = f'"{coreform_paths["iga_mesh"]}" "{mesh_cf}" --output-db "{mesh_sql}"'
    run_command( command, cwd=args.work_dir )
    return mesh_sql


def run_interop( args, coreform_paths, mesh_cf, mesh_sql ):
    command = f'"{coreform_paths["exodus_interop"]}" "{mesh_cf}" "{mesh_sql}" --output-prefix "{args.work_dir / output_prefix}"'
    run_command( command, cwd=args.work_dir )


def run_moose( args ):
    moose_executable = ( path_to_this_script / "../../../solid_mechanics-opt" ).resolve()
    input_file = path_to_this_script / "cframe_iga.i"
    if args.num_moose_proc == 1:
        command = f'"{moose_executable}" -i "{input_file}"'
    else:
        command = f'mpiexec -n {args.num_moose_proc} "{moose_executable}" -i "{input_file}"'
    run_command( command, cwd=args.work_dir )


def script_arguments():
    parser = argparse.ArgumentParser( description="Run the Coreform IGA Exodus pipeline." )
    parser.add_argument( "--degree", dest="degree", type=int, default=2 )
    parser.add_argument( "--mesh-size", dest="mesh_size", type=float, default=0.25 )
    parser.add_argument(
        "--mesh-mode",
        dest="mesh_mode",
        choices=[ "immersed", "boundingbox", "bodyfit", "flexfit" ],
        default="immersed",
        help="'boundingbox' is accepted as a legacy alias for the current immersed workflow.",
    )
    parser.add_argument( "--small-cell-volume-ratio", dest="small_cell_volume_ratio", type=float, default=0.0 )
    parser.add_argument( "--extension-max-generations", dest="extension_max_generations", type=int, default=2 )
    parser.add_argument( "--num-mesh-proc", dest="num_mesh_proc", type=int, default=1 )
    parser.add_argument( "--num-moose-proc", dest="num_moose_proc", type=int, default=1 )
    parser.add_argument( "--work-dir", dest="work_dir", type=Path, default=path_to_this_script )
    parser.add_argument( "--bin-dir", dest="bin_dir", type=Path )
    parser.add_argument( "--build-cf", dest="build_cf", type=Path )
    parser.add_argument( "--python", dest="python_exe", type=Path )
    parser.add_argument( "--cubit-python-module-path", dest="cubit_python_module_path", type=Path )
    parser.add_argument( "--skip-moose", dest="skip_moose", action="store_true" )
    parser.add_argument( "--verbose-cubit", dest="verbose_cubit", action="store_true" )
    return parser.parse_args()


if __name__ == "__main__":
    main( script_arguments() )
