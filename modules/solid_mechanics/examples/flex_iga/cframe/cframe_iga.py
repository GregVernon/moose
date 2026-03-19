import os
import sys
import math
import argparse
from pathlib import Path
import subprocess
from coreform_utils import import_cubit, get_coreform_paths

path_to_this_script = os.path.dirname( os.path.realpath( __file__ ) )

def main( args ):
    run_cubit( args )
    run_iga_mesh( args )
    run_interop( args )
    run_moose( args )

def run_cubit( args ):
    ## This routine verified to run with Coreform Cubit 2025.10
    cubit = import_cubit()
    cubit.cmd( 'reset' )
    ## Import geometry
    cubit.cmd( f'import step "{os.path.join( path_to_this_script, "c-frame.step" )}" noheal' )
    if args.mesh_mode == "boundingbox":
        ## Let Coreform Flex handle meshing...
        ### Assign sets for boundary conditions
        #### Partition surfaces to create sets for boundary and load conditions
        cubit.cmd( f'create vertex on curve 12 73  distance {1.575 + 0.025} from surface 74' )
        cubit.cmd( f'create vertex on curve 17 78  distance {1.575 + 0.025} from surface 72' )
        cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
        cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
        cubit.cmd( 'delete vertex all' )
        #### Make set assignments
        cubit.cmd( 'block 1 volume 1' )
        cubit.cmd( 'block 1 name "cframe"' )
        cubit.cmd( 'sideset 1 surface 102' )
        cubit.cmd( 'sideset 1 name "load_surface"' )
        cubit.cmd( 'sideset 2 surface 103' )
        cubit.cmd( 'sideset 2 name "hold_surface"' )
    else:
        ## Mesh according to user input
        if args.mesh_mode == "bodyfit":
            ### Defeature for body-fitted meshing
            #### Remove blend surfaces
            S = cubit.get_blend_surfaces( (1,) ) # Find blend surfaces in volume 1
            cubit.cmd( f'remove surface {cubit.get_id_string( S )} extend' )
            ### Assign sets for boundary conditions
            #### Partition surfaces to create sets for boundary and load conditions
            cubit.cmd( f'create vertex on curve 12 74  distance {1.575 + 0.025} from surface 74' )
            cubit.cmd( f'create vertex on curve 17 79  distance {1.575 + 0.025} from surface 72' )
            cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
            cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
            cubit.cmd( 'delete vertex all' )
            #### Make set assignments
            cubit.cmd( 'block 1 volume 1' )
            cubit.cmd( 'block 1 name "cframe"' )
            cubit.cmd( 'sideset 1 surface 101' )
            cubit.cmd( 'sideset 1 name "load_surface"' )
            cubit.cmd( 'sideset 2 surface 103' )
            cubit.cmd( 'sideset 2 name "hold_surface"' )
            ### Partition for body-fitted meshing
            cubit.cmd( 'webcut volume all with plane from surface 92' )
            cubit.cmd( 'webcut volume all with plane normal to curve 219  close_to vertex 121' )
            cubit.cmd( 'webcut volume all with plane normal to curve 219  close_to vertex 10' )
            cubit.cmd( 'webcut volume all with plane normal to curve 15  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with plane normal to curve 150  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with plane normal to curve 382  fraction .5 from start' )
            cubit.cmd( 'webcut volume all with sheet extended from surface 134 131 182 167 130 146' )
            ### Enforce mesh continuity across partitions
            cubit.cmd( 'imprint volume all' )
            cubit.cmd( 'merge volume all' )
            ### Assign mesh schemes and generate mesh
            cubit.cmd( f'volume all size {args.mesh_size}' )
            cubit.cmd( "mesh volume all" )
        elif args.mesh_mode == "flexfit":
            ### Assign sets for boundary conditions
            #### Partition surfaces to create sets for boundary and load conditions
            cubit.cmd( f'create vertex on curve 12 73  distance {1.575 + 0.025} from surface 74' )
            cubit.cmd( f'create vertex on curve 17 78  distance {1.575 + 0.025} from surface 72' )
            cubit.cmd( 'split surface 63  across location vertex 117  location vertex 118' )
            cubit.cmd( 'split surface 97  across location vertex 119  location vertex 120' )
            cubit.cmd( 'delete vertex all' )
            #### Make set assignments
            cubit.cmd( 'block 1 volume 1' )
            cubit.cmd( 'block 1 name "cframe"' )
            cubit.cmd( 'sideset 1 surface 102' )
            cubit.cmd( 'sideset 1 name "load_surface"' )
            cubit.cmd( 'sideset 2 surface 103' )
            cubit.cmd( 'sideset 2 name "hold_surface"' )
            ### Create simplified geometry for "flex-fitted" meshing
            cubit.cmd( 'volume 1 copy' )
            #### Remove blend surfaces
            S = cubit.get_blend_surfaces( (2,) ) # Find blend surfaces in volume 2
            cubit.cmd( f'remove surface {cubit.get_id_string( S )} extend' )
            #### Remove remaining small features
            cubit.cmd( f'remove surface 165 167 171 173 188 189 190 198 199 200 201 202 204 205 extend' )
            ### Assign volume to a mesh block
            cubit.cmd( 'block 2 volume 2' )
            cubit.cmd( 'block 2 name "cframe_flexmesh"' )
            ### Assign mesh schemes and generate mesh
            cubit.cmd( f'volume 2 size {args.mesh_size}' )
            cubit.cmd( 'curve 312 307 233 229 317 353 301 375 interval same' )
            cubit.cmd( 'curve 310 248 445 446 interval same' )
            cubit.cmd( 'volume 2 redistribute nodes off' )
            cubit.cmd( 'volume 2 autosmooth target on  fixed imprints off  smart smooth off' )
            cubit.cmd( 'volume 2 scheme Sweep source surface 180 target surface 178 sweep transform least squares' )
            cubit.cmd( 'mesh volume 2' )
    ## Save Coreform Cubit file for potential debugging
    cubit.cmd( 'save cub5 "cframe.cub5" overwrite' )
    ## Export Coreform Flex file
    cubit.cmd( 'export coreform "cframe_geom.cf" overwrite' )

def run_iga_mesh( args ):
    mpiexec = get_coreform_paths()["mpiexec"]
    coreform_iga_mesh = get_coreform_paths()["iga_mesh"]
    command = f"{mpiexec} -n {args.num_mesh_proc} {coreform_iga_mesh} cframe_geom.cf --output-db meshed_cframe_moose.sql"
    subprocess.check_call( command, shell=True )

def run_interop( args ):
    exodus_interop = get_coreform_paths()["exodus_interop"]
    command = f"{exodus_interop} cframe_geom.cf meshed_cframe_moose.sql --output-prefix meshed_cframe_moose"
    subprocess.check_call( command, shell=True )

def run_moose( args ):
    moose_executable = Path( f"{ os.path.join( path_to_this_script, '../../../solid_mechanics-opt') }" ).resolve()
    input_file = os.path.join( path_to_this_script, "cframe_iga.i" )
    command = f"mpiexec -n {args.num_moose_proc} {moose_executable} -i {input_file}"
    subprocess.check_call( command, shell=True )

def script_arguments():
    parser = argparse.ArgumentParser(description="Run the Coreform pipeline.")
    parser.add_argument( "--degree", dest="degree", type=int, default=1 )
    parser.add_argument( "--mesh-size", dest="mesh_size", type=float, default=0.25 )
    parser.add_argument( "--mesh-mode", dest="mesh_mode", choices=["bodyfit", "flexfit", "boundingbox"], default="boundingbox" )
    parser.add_argument( "--small-cell-volume-ratio", dest="small_cell_volume_ratio", type=float, default=0.2 )
    parser.add_argument( "--num-mesh-proc", dest="num_mesh_proc", type=int, default=1 )
    parser.add_argument( "--num-moose-proc", dest="num_moose_proc", type=int, default=1 )
    return parser.parse_args()

if __name__ == "__main__":
    args = script_arguments()
    ## Validate arguments against current limitations
    if args.mesh_mode == "flexfit":
        raise ValueError( f"Currently only 'bodyfit' and 'boundingbox' mesh modes are supported by Coreform Flex Interop. You provided: {args.mesh_mode}" )
    if ( args.mesh_mode != "bodyfit" ) and ( args.num_moose_proc != 1 ):
        raise ValueError( f"The current implementation in MOOSE for trimmed meshes only supports LU linear solvers, which is limited to serial processing (1 CPU). You provided: {args.num_moose_proc}" )
    main( args )