import os
import sys
from pathlib import Path

def import_flex( verbose=False ):
    coreform_paths = get_coreform_paths()
    sys.path.append( os.fspath( coreform_paths["flex_path"] ) )
    from coreform import flex
    flex.init( verbose=verbose, gui=False )
    return flex

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
        coreform_paths["cubit"] =        Path( r"C:\Program Files\Coreform Cubit 2025.10\bin\coreform_cubit.exe" )
        coreform_paths["cubit_path"] =   Path( r"C:\Program Files\Coreform Cubit 2025.10\bin" )
        coreform_paths["flex"] =         Path( r"C:\Program Files\Coreform Flex 2025.10\bin\coreform_flex.exe" )
        coreform_paths["flex_path"] =    Path( r"C:\Program Files\Coreform Flex 2025.10\bin" )
        coreform_paths["trim"] =         Path( r"C:\Program Files\Coreform Flex 2025.10\bin\coreform_trim.bat" )
        coreform_paths["trim_path"] =    Path( r"C:\Program Files\Coreform Flex 2025.10\bin" )
        coreform_paths["mpiexec"] =      Path( r"C:\Program Files\Coreform Flex 2025.10\bin\mpiexec.exe" )
        coreform_paths["mpiexec_path"] = Path( r"C:\Program Files\Coreform Flex 2025.10\bin" )
    elif "lin" in sys.platform:
        coreform_paths["cubit"] =        Path( "/opt/Coreform-Cubit-2025.10/bin/coreform_cubit" )
        coreform_paths["cubit_path"] =   Path( "/opt/Coreform-Cubit-2025.10/bin" )
        coreform_paths["flex"] =         Path( "/opt/Coreform-Flex-2025.10/bin/coreform_flex" )
        coreform_paths["flex_path"] =    Path( "/opt/Coreform-Flex-2025.10/bin" )
        coreform_paths["trim"] =         Path( "/opt/Coreform-Flex-2025.10/bin/coreform_trim" )
        coreform_paths["trim_path"] =    Path( "/opt/Coreform-Flex-2025.10/bin" )
        coreform_paths["mpiexec"] =      Path( "/opt/Coreform-Flex-2025.10/bin/mpiexec" )
        coreform_paths["mpiexec_path"] = Path( "/opt/Coreform-Flex-2025.10/bin" )
    return coreform_paths