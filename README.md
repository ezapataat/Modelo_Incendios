# Modelo_Incendios
Modelo Incendios: Repositorio del desarrollo y la ejecución operativa del modelo de incendios desarrollado y mantenido por el equipo de Hidrología

## Requisitos:

Para su correcta ejecución se deben tener los siguientes requisitos:

- Estar al interior de la red de SIATA para la realizaciónd e consultas. 
- Para consultar y transformar radar requiere: 
	- Conexión a los datos de radar. 
	- El módulo de Radar: https://github.com/nicolas998/Radar.git
- Los siguientes paquetes de **Python**:
	- Pandas.
	- numpy.
	- matplotlib.
	- datetime.
	- reportlab.
	
## Instalación:

Para instalar este paquete en su equipo debe en una terminal de bash indicar el siguiente 
codigo:

Primero debe desplazar la **terminal** hasta la carpeta *clonada* o *descargada* de este repo.

```bash
cd Path/CPR
```

Luego se realiza la instalación, para esto debe tener privilegios de **sudoer**.

```bash
sudo python setup.py install
```

