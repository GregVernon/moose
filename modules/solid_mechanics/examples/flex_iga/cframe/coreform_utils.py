import os
import shlex
import subprocess
import sys
from pathlib import Path


def import_cubit( verbose=False, cubit_python_module_path=None ):
    coreform_paths = get_coreform_paths()
    cubit_path = Path( cubit_python_module_path ) if cubit_python_module_path is not None else coreform_paths["cubit_path"]
    sys.path.append( os.fspath( cubit_path ) )
    import cubit
    if verbose:
        cubit.init( [] )
    else:
        cubit.init( [ "cubit", "-noecho", "-nojournal", "-information", "off", "-warning", "off" ])
    return cubit


def run_command( command, *, cwd=None, env=None ):
    if isinstance( command, str ):
        print( f"\n$ {command}", flush=True )
        subprocess.check_call( command, shell=True, cwd=os.fspath( cwd ) if cwd is not None else None, env=env )
    else:
        normalized = [ os.fspath( arg ) for arg in command ]
        print( f"\n$ {shlex.join( normalized )}", flush=True )
        subprocess.check_call( normalized, cwd=os.fspath( cwd ) if cwd is not None else None, env=env )


def get_coreform_paths( args=None ):
    coreform_paths = _default_coreform_paths()
    if args is not None:
        coreform_paths = _apply_path_overrides( coreform_paths, args )
    return coreform_paths


def _default_coreform_paths():
    coreform_paths = {}
    if "win" in sys.platform:
        coreform_paths["cubit"] =               Path( r"C:\Program Files\Coreform Cubit 2025.10\bin\coreform_cubit.exe" )
        coreform_paths["cubit_path"] =          Path( r"C:\Program Files\Coreform Cubit 2025.10\bin" )
        coreform_paths["iga_mesh"] =            Path( r"C:\Program Files\Coreform IGA 2026.4\bin\coreform_iga_mesh.bat" )
        coreform_paths["iga_mesh_path"] =       Path( r"C:\Program Files\Coreform IGA 2026.4\bin" )
        coreform_paths["build_cf"] =            Path( r"C:\Program Files\Coreform IGA 2026.4\bin\build_cf.py" )
        coreform_paths["build_cf_path"] =       Path( r"C:\Program Files\Coreform IGA 2026.4\bin" )
        coreform_paths["exodus_interop"] =      Path( r"C:\Program Files\Coreform IGA 2026.4\bin\exodus_interop.exe" )
        coreform_paths["exodus_interop_path"] = Path( r"C:\Program Files\Coreform IGA 2026.4\bin" )
        coreform_paths["mpiexec"] =             Path( r"C:\Program Files\Coreform IGA 2026.4\bin\mpiexec.exe" )
        coreform_paths["mpiexec_path"] =        Path( r"C:\Program Files\Coreform IGA 2026.4\bin" )
    elif "lin" in sys.platform:
        coreform_paths["cubit"] =               Path( "/home/gvernon2/apps/coreform/Coreform-Cubit-2025.10/bin/coreform_cubit" )
        coreform_paths["cubit_path"] =          Path( "/home/gvernon2/apps/coreform/Coreform-Cubit-2025.10/bin" )
        coreform_paths["iga_mesh"] =            Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin/coreform_iga_mesh" )
        coreform_paths["iga_mesh_path"] =       Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin" )
        coreform_paths["build_cf"] =            Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin/build_cf.py" )
        coreform_paths["build_cf_path"] =       Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin" )
        coreform_paths["exodus_interop"] =      Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin/exodus_interop" )
        coreform_paths["exodus_interop_path"] = Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin" )
        coreform_paths["mpiexec"] =             Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin/mpiexec" )
        coreform_paths["mpiexec_path"] =        Path( "/home/gvernon2/apps/coreform/Coreform-IGA-2026.4/bin" )
    return coreform_paths


def _apply_path_overrides( coreform_paths, args ):
    if args.bin_dir is not None:
        bin_dir = args.bin_dir.expanduser().resolve()
        coreform_paths["iga_mesh_path"] = bin_dir
        coreform_paths["build_cf_path"] = bin_dir
        coreform_paths["exodus_interop_path"] = bin_dir
        coreform_paths["mpiexec_path"] = bin_dir
        coreform_paths["build_cf"] = bin_dir / "build_cf.py"
        if os.name == "nt":
            coreform_paths["iga_mesh"] = bin_dir / "coreform_iga_mesh.bat"
            coreform_paths["exodus_interop"] = bin_dir / "exodus_interop.exe"
            coreform_paths["mpiexec"] = bin_dir / "mpiexec.exe"
        else:
            coreform_paths["iga_mesh"] = bin_dir / "coreform_iga_mesh"
            coreform_paths["exodus_interop"] = bin_dir / "exodus_interop"
            coreform_paths["mpiexec"] = bin_dir / "mpiexec"

    if args.cubit_python_module_path is not None:
        coreform_paths["cubit_path"] = args.cubit_python_module_path.expanduser().resolve()
    if args.build_cf is not None:
        coreform_paths["build_cf"] = args.build_cf.expanduser().resolve()
        coreform_paths["build_cf_path"] = coreform_paths["build_cf"].parent

    _require_existing_path( coreform_paths["cubit_path"], "Cubit Python module path" )
    _require_existing_path( coreform_paths["build_cf"], "build_cf.py" )
    _require_existing_path( coreform_paths["iga_mesh"], "coreform_iga_mesh executable" )
    _require_existing_path( coreform_paths["exodus_interop"], "exodus_interop executable" )
    if args.num_mesh_proc > 1:
        _require_existing_path( coreform_paths["mpiexec"], "mpiexec executable" )

    coreform_paths["build_cf_python"] = _build_cf_python( args, coreform_paths )
    coreform_paths["build_cf_env"] = _build_cf_environment( coreform_paths )
    return coreform_paths


def _require_existing_path( path, description ):
    if not Path( path ).expanduser().resolve().exists():
        raise SystemExit( f"Missing {description}: {Path( path ).expanduser().resolve()}" )


def _build_cf_python( args, coreform_paths ):
    if args.python_exe is not None:
        _require_existing_path( args.python_exe, "Python executable" )
        return args.python_exe.expanduser().resolve()

    cubit_python = coreform_paths["cubit_path"] / "python3" / ( "python.exe" if os.name == "nt" else "python3" )
    if cubit_python.exists():
        return cubit_python
    return Path( sys.executable )


def _build_cf_environment( coreform_paths ):
    env = os.environ.copy()
    env["CUBIT_PYTHON_MODULE_PATH"] = os.fspath( coreform_paths["cubit_path"] )

    if "lin" in sys.platform:
        prepend = [
            os.fspath( coreform_paths["cubit_path"] ),
            os.fspath( coreform_paths["build_cf_path"] ),
            os.fspath( coreform_paths["iga_mesh_path"] ),
        ]
        existing = env.get( "LD_LIBRARY_PATH" )
        env["LD_LIBRARY_PATH"] = os.pathsep.join( prepend + ( [ existing ] if existing else [] ) )

    return env
