import os
import sys
from pathlib import Path

def import_cubit( verbose=False ):
    coreform_paths = get_coreform_paths()
    sys.path.append( os.fspath( coreform_paths["cubit_path"] ) )
    import cubit
    if verbose:
        cubit.init( [] )
    else:
        cubit.init( [ "cubit", "-noecho", "-nojournal", "-information", "off", "-warning", "off" ])
    return cubit

def get_coreform_paths():
    coreform_paths = {}
    if "win" in sys.platform:
        coreform_paths["cubit"] =               Path( r"C:\Program Files\Coreform Cubit 2025.10\bin\coreform_cubit.exe" )
        coreform_paths["cubit_path"] =          Path( r"C:\Program Files\Coreform Cubit 2025.10\bin" )
        coreform_paths["iga_mesh"] =            Path( r"C:\Program Files\Coreform IGA 2026.3\bin\coreform_iga_mesh.bat" )
        coreform_paths["iga_mesh_path"] =       Path( r"C:\Program Files\Coreform IGA 2026.3\bin" )
        coreform_paths["exodus_interop"] =      Path( r"C:\Program Files\Coreform IGA 2026.3\bin\exodus_interop.exe" )
        coreform_paths["exodus_interop_path"] = Path( r"C:\Program Files\Coreform IGA 2026.3\bin" )
        coreform_paths["mpiexec"] =             Path( r"C:\Program Files\Coreform IGA 2026.3\bin\mpiexec.exe" )
        coreform_paths["mpiexec_path"] =        Path( r"C:\Program Files\Coreform IGA 2026.3\bin" )
    elif "lin" in sys.platform:
        coreform_paths["cubit"] =               Path( "/home/gvernon2/apps/coreform/Coreform-Cubit-2025.10/bin/coreform_cubit" )
        coreform_paths["cubit_path"] =          Path( "/home/gvernon2/apps/coreform/Coreform-Cubit-2025.10/bin" )
        coreform_paths["iga_mesh"] =            Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin/coreform_iga_mesh" )
        coreform_paths["iga_mesh_path"] =       Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin" )
        coreform_paths["exodus_interop"] =      Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin/exodus_interop" )
        coreform_paths["exodus_interop_path"] = Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin" )
        coreform_paths["mpiexec"] =             Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin/mpiexec" )
        coreform_paths["mpiexec_path"] =        Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.3/bin" )
    return coreform_paths