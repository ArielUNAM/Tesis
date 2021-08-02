# Flujo de trabajo típico para la estimación de precipitación de archivos de radar

Los archivos de radar almacenan información muy útil sobre la distribución espacial de la lluvia. Sin embargo para que unos sea capaz de usar la información de los radares para estudios cuantitativos, la información debe ser cuidadosamente procesada para poder corregir algunos de los errores típicos que la información presenta como: ecos, atenuación de la señal o cierta incertidumbre en la relación Z/R.

Además de lo anterior, muchas veces es necesario transformar las coordenadas de la información de un sistema polar a uno cartesiano o combinar la información de diferentes estaciones de radar para lograr un mejor mapeo de las zonas y la estimación del error o la incertidumbre de la información. Al final uno espera obtener una representación visual típica de estos datos, para reconocer la distribución espacial de la lluvia en un mapa. 

Para lograr lo anterior se debe seguir una serie de pasos que permitan aprovechar la información para aplicaciones quantitativas. Todos los pasos juntos son típicamente conocidos como *radar data processing chain* ***Wradlib*** permite construir esta cadena de procesamiento y además permite al usuario modificarla a su beneficio.

1. **Lectura de los datos**

   ​	La codificación de la información es la mayor limitante que existe para muchos usuarios potenciales que buscan trabajar con esta información, ya que cada radar puede tener una codificación única con poca o nula documentación y que para lograr su manipulación es necesario comprar software específico. wradlib, pyart y algunas otras librerias intentar eliminar esta barrera poniendo a disposición del usuario funciones que permiten la lectura de algunas formatos como: **ODIM_H5, NetCDF e IRIS**.

   Usualmente la información se encuentra almacenada en una matriz mutidimensiona del tipo numpy.ndarray y la infromación complementaria es manejada en estructuras del tipo diccionario. 

   Para lograr la lectura de un archivo se debe usar el modulo *wradlib.io* 

2. **Remoción del ruido/desorden**

   ​	La información generada por los radares puede almacenar ecos no meteorológicos causados al chocar contra objetos que se encuentran en la superficie terrestre como montañas, casas, edificios, aves, aviones u otros objetos.

   Si se cuenta con información sobre la posición de objetos como montañas o edificios se puede aplicar un filtro estático que considere estos puntos durante el procesamiento de la información y con ello disminuir la presencia final en los archivos o, siguiendo la misma lógica, manipular una gran cantidad de archivos de la misma región para detectar estas anomalias y después aplicar el filtro. 

   Sin embargo, existen otros filtros que permiten remover otros tipos de ruido de forma eficiente, sin tener que pasar por filros estáticos. wradlib cuenta en su modulo *wradlib.clutter* algunas funciones que permiten limpiar la información.

3. **Remoción de la atenuación**

   

4. d

   

   