import os
import pkg_resources
import subprocess

# # Nombre del directorio del entorno virtual (ajusta esto según tu configuración)
# root_dir = os.path.dirname(__file__)
# venv_name = "venv"
# virtualenv_dir = os.path.join(root_dir, venv_name)

# # Verificar si el entorno virtual ya existe
# if not os.path.exists(virtualenv_dir):
#     print("Entorno virtual no existe")
#     # create virtual enviroment in new directory
#     subprocess.run(["virtualenv", virtualenv_dir])
#     print("Entorno virtual creado.")
# else:
#     print("El entorno virtual ya existe.")


# # Comando para activar el entorno virtual en Windows
# activate_script = os.path.join(virtualenv_dir, "Scripts", "activate")

# subprocess.run(activate_script, shell=True)


# if 'VIRTUAL_ENV' in os.environ:
#     print("El entorno virtual está activado.")
# else:
#     print("El entorno virtual no está activado.")


# Obtén una lista de todas las bibliotecas instaladas en el entorno actual
installed_packages = {
    pkg.key: pkg.version for pkg in pkg_resources.working_set}

# Directorio raíz de tu proyecto (ajústalo según tu estructura de carpetas)
project_root = "./"

# Inicializa una lista para almacenar las bibliotecas utilizadas en tu proyecto
used_libraries = set()

# Recorre los archivos de tu proyecto en busca de importaciones de bibliotecas
for root, _, files in os.walk(project_root):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)

            # Verifica si la ruta contiene "venv"
            if "venv" not in file_path:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("import ") or line.startswith("from "):
                            libraries = line.split()
                            for lib in libraries[1:]:
                                used_libraries.add(lib.split(".")[0])

# Filtra las bibliotecas utilizadas que están instaladas
used_libraries = {lib: installed_packages.get(
    lib) for lib in used_libraries if lib in installed_packages}

# Actualiza requirements.txt con las bibliotecas utilizadas
with open("requirements.txt", "w") as req_file:
    for lib, version in used_libraries.items():
        if version:
            req_file.write(f"{lib}=={version}\n")
        else:
            req_file.write(f"{lib}\n")

# Actualiza las bibliotecas instaladas
for lib, version in used_libraries.items():
    if version:
        subprocess.run(["pip", "install", "--upgrade", f"{lib}=={version}"])
    else:
        subprocess.run(["pip", "install", "--upgrade", lib])
