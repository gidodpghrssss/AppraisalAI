# Manual del Sitio Web y Panel de Administración de Apeko

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Primeros Pasos](#primeros-pasos)
4. [Interfaz de Usuario](#interfaz-de-usuario)
5. [Panel de Administración](#panel-de-administración)
6. [Personalización del Sitio Web](#personalización-del-sitio-web)
7. [Agente de IA](#agente-de-ia)
8. [Base de Datos RAG](#base-de-datos-rag)
9. [Solución de Problemas](#solución-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

Apeko es una plataforma integral de tasación de propiedades que combina metodologías tradicionales de tasación con tecnología de IA de vanguardia. La plataforma consta de un sitio web orientado al cliente y un panel de administración para gestionar tasaciones, clientes y el agente de IA.

### Características Principales

- **Tasaciones Potenciadas por IA**: Aprovecha la inteligencia artificial para ayudar en las valoraciones de propiedades
- **Gestión de Clientes**: Seguimiento y gestión de información e interacciones con clientes
- **Gestión de Documentos**: Almacenamiento y organización de documentos de tasación y archivos relacionados
- **Base de Datos RAG**: Sistema de Generación Aumentada por Recuperación para proporcionar respuestas contextualizadas
- **Panel de Análisis**: Visualización de métricas clave e indicadores de rendimiento

## Instalación

### Requisitos del Sistema

- Python 3.9 o superior
- Base de datos SQLite (predeterminada) o PostgreSQL
- 4GB de RAM mínimo (8GB recomendado)
- 10GB de espacio libre en disco

### Pasos de Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tunombredeusuario/AppraisalAI.git
   cd AppraisalAI
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicializar la base de datos:
   ```bash
   python -m app.database.init_db
   ```

5. Iniciar la aplicación:
   ```bash
   python -m app.main
   ```

6. Acceder a la aplicación en http://localhost:8001

## Primeros Pasos

Después de la instalación, necesitará configurar su cuenta de administrador inicial:

1. Navegar a http://localhost:8001/admin/login
2. Usar las credenciales predeterminadas:
   - Nombre de usuario: admin
   - Contraseña: apeko2025
3. Se le solicitará cambiar su contraseña en el primer inicio de sesión

## Interfaz de Usuario

El sitio web de Apeko consta de varias secciones clave:

### Página de Inicio

La página de inicio muestra los principales servicios ofrecidos por Apeko, incluyendo:
- Tasaciones Residenciales
- Tasaciones Comerciales
- Análisis de Mercado
- Valoraciones Asistidas por IA

### Servicios

Información detallada sobre cada servicio ofrecido, incluyendo:
- Descripciones de procesos
- Información de precios
- Tiempos de entrega
- Informes de muestra

### Acerca de Nosotros

Información sobre la empresa, miembros del equipo, cualificaciones y certificaciones.

### Contacto

Un formulario de contacto e información de la empresa para que los clientes puedan comunicarse.

## Panel de Administración

El panel de administración es el centro de control para gestionar todos los aspectos de la plataforma Apeko.

### Visión General del Panel

El panel principal muestra métricas clave:
- Total de clientes
- Proyectos activos
- Solicitudes pendientes
- Actividades recientes

### Gestión de Clientes

La sección de clientes le permite:
- Ver todos los clientes
- Añadir nuevos clientes
- Editar información de clientes
- Archivar clientes inactivos

### Gestión de Tasaciones

La sección de tasaciones le permite:
- Crear nuevos informes de tasación
- Seguir el estado de las tasaciones
- Asignar tasadores
- Generar informes finales

### Explorador de Archivos

El explorador de archivos proporciona:
- Organización de documentos por cliente y proyecto
- Funcionalidad de carga
- Control de versiones
- Capacidades de búsqueda

### Agente de IA

La sección del agente de IA le permite:
- Interactuar con el asistente de IA
- Ver el historial de chat
- Configurar ajustes de IA
- Entrenar la IA con nuevos datos

### Base de Datos RAG

La sección de la base de datos RAG (Generación Aumentada por Recuperación) le permite:
- Cargar documentos a la base de conocimientos
- Gestionar categorías de documentos
- Ver historial de consultas
- Monitorear el rendimiento del sistema

### Análisis

La sección de análisis proporciona:
- Tendencias de volumen de tasaciones
- Métricas de adquisición de clientes
- Análisis de ingresos
- Estadísticas de uso de IA

### Configuración

La sección de configuración le permite:
- Gestionar cuentas de usuario
- Configurar ajustes del sistema
- Personalizar plantillas de correo electrónico
- Configurar integraciones

## Personalización del Sitio Web

### Modificación del Contenido del Sitio Web

El contenido del sitio web puede modificarse editando los archivos de plantilla ubicados en:
```
app/templates/
```

Los archivos de plantilla clave incluyen:
- `index.html`: Página de inicio
- `services.html`: Página de servicios
- `about.html`: Página de acerca de
- `contact.html`: Página de contacto

### Cambio de Imágenes

Para cambiar imágenes en el sitio web:

1. Prepare sus nuevas imágenes con las dimensiones apropiadas:
   - Banner principal: 1920x1080px
   - Iconos de servicio: 512x512px
   - Fotos del equipo: 800x800px

2. Coloque sus imágenes en el directorio estático:
   ```
   app/static/images/
   ```

3. Actualice las referencias de imágenes en los archivos de plantilla:
   ```html
   <img src="{{ url_for('static', path='/images/su-nueva-imagen.jpg') }}" alt="Descripción">
   ```

### Modificación de Estilos CSS

Para cambiar la apariencia del sitio web:

1. Edite el archivo CSS principal:
   ```
   app/static/css/apeko.css
   ```

2. Secciones de estilo clave:
   - Variables de esquema de colores en la parte superior del archivo
   - Estilos de tipografía
   - Estilos específicos de componentes
   - Puntos de ruptura de diseño responsive

3. Ejemplo de cambio del color primario:
   ```css
   :root {
     --apeko-primary: #9d0208;  /* Cambie esto a su color deseado */
     --apeko-secondary: #dc2f02;
     --apeko-accent: #f48c06;
   }
   ```

### Añadir Nuevas Páginas

Para añadir una nueva página al sitio web:

1. Cree un nuevo archivo de plantilla en `app/templates/`

2. Añada una nueva ruta en `app/web/controllers.py`:
   ```python
   @router.get("/su-nueva-pagina", response_class=HTMLResponse)
   async def su_nueva_pagina(request: Request, db: Session = Depends(get_db)):
       return templates.TemplateResponse(
           "su-nueva-pagina.html",
           {"request": request}
       )
   ```

3. Añada un enlace a la nueva página en el menú de navegación en `app/templates/base.html`

## Agente de IA

### Configuración del Agente de IA

El agente de IA está impulsado por la API de Nebius y puede configurarse en:
```
app/core/config.py
```

Opciones de configuración clave:
- `NEBIUS_API_KEY`: Su clave API de Nebius
- `NEBIUS_API_ENDPOINT`: URL del punto final de la API
- `NEBIUS_MODEL_NAME`: Nombre del modelo a utilizar (predeterminado: meta-llama/Meta-Llama-3.1-70B-Instruct)

### Entrenamiento del Agente de IA

El agente de IA utiliza un sistema RAG (Generación Aumentada por Recuperación) para proporcionar respuestas contextualizadas:

1. Cargue documentos relevantes a la base de datos RAG a través del panel de administración
2. Categorice los documentos apropiadamente
3. La IA utilizará automáticamente estos documentos para proporcionar respuestas más precisas

### Uso del Agente de IA

Para usar el agente de IA:

1. Navegue a la sección Agente de IA en el panel de administración
2. Escriba su consulta en la interfaz de chat
3. La IA responderá con información basada en su entrenamiento y los documentos en la base de datos RAG
4. Puede ver las fuentes utilizadas por la IA haciendo clic en "Ver Fuentes" debajo de cada respuesta

## Base de Datos RAG

### Añadir Documentos

Para añadir documentos a la base de datos RAG:

1. Navegue a la sección Base de Datos RAG en el panel de administración
2. Haga clic en "Añadir Documento"
3. Complete los detalles del documento:
   - Título
   - Tipo de documento
   - Cargue el archivo del documento
   - Añada descripción opcional
4. Haga clic en "Añadir Documento" para procesar e indexar el documento

### Tipos de Documentos

El sistema admite varios tipos de documentos:
- Informes de Tasación
- Análisis de Mercado
- Regulaciones
- Datos de Propiedades
- Otros

### Monitoreo de Rendimiento

El panel de la Base de Datos RAG proporciona métricas sobre:
- Total de documentos
- Total de fragmentos
- Volumen de consultas
- Puntuaciones de relevancia

## Solución de Problemas

### Problemas Comunes

#### La Aplicación No Inicia

**Problema**: La aplicación no inicia con un mensaje de error.

**Solución**:
1. Verifique si está instalada la versión correcta de Python
2. Verifique que todas las dependencias estén instaladas: `pip install -r requirements.txt`
3. Asegúrese de que la base de datos esté correctamente inicializada: `python -m app.database.init_db`
4. Verifique conflictos de puerto y cambie el puerto si es necesario en `app/core/config.py`

#### Errores de Base de Datos

**Problema**: Aparecen mensajes de error relacionados con la base de datos.

**Solución**:
1. Verifique la configuración de conexión a la base de datos en `app/core/config.py`
2. Asegúrese de que el servidor de base de datos esté en ejecución (si usa PostgreSQL)
3. Verifique los permisos de la base de datos
4. Intente reinicializar la base de datos: `python -m app.database.init_db`

#### El Agente de IA No Responde

**Problema**: El agente de IA no responde a las consultas.

**Solución**:
1. Verifique su clave API de Nebius en `app/core/config.py`
2. Verifique la conectividad a Internet
3. Asegúrese de que el nombre del modelo sea correcto
4. Verifique los registros de la API para mensajes de error

## Preguntas Frecuentes

### Preguntas Generales

**P: ¿Puedo usar un sistema de base de datos diferente?**

R: Sí, la aplicación admite SQLite (predeterminado) y PostgreSQL. Para cambiar a PostgreSQL, actualice `DATABASE_URL` en `app/core/config.py`.

**P: ¿Cómo hago una copia de seguridad de mis datos?**

R: Para SQLite, copie el archivo `app.db`. Para PostgreSQL, use los procedimientos estándar de copia de seguridad de PostgreSQL.

**P: ¿Cómo añado un nuevo usuario administrador?**

R: Navegue a Configuración > Gestión de Usuarios en el panel de administración y haga clic en "Añadir Usuario".

### Preguntas de Personalización

**P: ¿Puedo cambiar el logotipo?**

R: Sí, reemplace el archivo de logotipo en `app/static/images/APEKOLOGO.png` con su propio logotipo (mantenga el mismo nombre de archivo o actualice las referencias en las plantillas).

**P: ¿Cómo cambio el esquema de colores?**

R: Edite las variables CSS en `app/static/css/apeko.css` para cambiar el esquema de colores en todo el sitio.

**P: ¿Puedo añadir JavaScript personalizado?**

R: Sí, añada su JavaScript personalizado a `app/static/js/` e inclúyalo en las plantillas usando:
```html
<script src="{{ url_for('static', path='/js/su-script.js') }}"></script>
```

### Preguntas Técnicas

**P: ¿Qué modelo de IA se utiliza?**

R: La aplicación utiliza el modelo Meta-Llama-3.1-70B-Instruct a través de la API de Nebius.

**P: ¿Cómo se generan los embeddings de documentos?**

R: Los embeddings de documentos se generan utilizando el mismo modelo que el agente de IA, con una dimensión de 1536.

**P: ¿Puedo implementar esto en un servidor de producción?**

R: Sí, para implementación en producción, recomendamos:
1. Usar un servidor ASGI de producción como Uvicorn o Hypercorn
2. Configurar autenticación adecuada
3. Usar PostgreSQL en lugar de SQLite
4. Configurar HTTPS
5. Establecer variables de entorno apropiadas
