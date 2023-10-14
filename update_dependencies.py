import os
import subprocess

# Ruta del directorio de tu proyecto
project_directory = "./"

# Nombre del archivo requirements.txt que se generará
requirements_file = "requirements.txt"

# Cambia al directorio del proyecto
os.chdir(project_directory)

# Ejecuta pipreqs para generar el archivo requirements.txt
subprocess.run(["pipreqs", ".", "--force"])

# Instala las dependencias desde requirements.txt
subprocess.run(["pip", "install", "-r", requirements_file])

print("Dependencias actualizadas e instaladas correctamente.")
