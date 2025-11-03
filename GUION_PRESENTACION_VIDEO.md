# Guion de Presentación del Proyecto - Video (5 minutos)

## Estructura General

**Duración total:** 5 minutos máximo
**Formato:** Presentación en equipo, cada miembro presenta su rol y contribuciones

---

## INTRODUCCIÓN (30 segundos)

**[Persona que habla: Cualquier miembro]**

"Hola, somos el equipo de desarrollo del proyecto de Machine Learning para estimación de niveles de obesidad. Este video presenta el trabajo realizado en la Fase 2, donde refactorizamos un proyecto de Jupyter Notebook a una estructura profesional siguiendo estándares de MLOps.

Somos:
- Alicia Canta Pandal - DevOps Engineer
- Iván Cruz Ibarra - Data Scientist
- Mayra Hernández Alba - Data Engineer
- Sebastián Coronado Rivera - ML Engineer

A continuación, cada integrante presentará su contribución al proyecto."

---

## SECCIÓN 1: ESTRUCTURACIÓN CON COOKIECUTTER (45 segundos)

**[Persona que habla: Sebastián Coronado Rivera - ML Engineer]**

"Mi responsabilidad incluyó estructurar el proyecto usando la plantilla Cookiecutter para Machine Learning. Esto abarca:

Primero, implementé la estructura de directorios estándar: separé el código fuente en módulos bajo `src/`, creé directorios para pipelines, scripts, tests y configuración. 

Segundo, establecí la configuración del paquete en `setup.py` y organicé las dependencias en `requirements.txt`.

Tercero, implementé utilidades centralizadas en `src/utils/` para configuración y logging, permitiendo que todos los módulos compartan parámetros y mantengan consistencia.

El resultado es una estructura profesional, escalable y mantenible que facilita la colaboración del equipo."

---

## SECCIÓN 2A: INFRAESTRUCTURA DE DATOS Y CARGA (40 segundos)

**[Persona que habla: Mayra Hernández Alba - Data Engineer]**

"Como Data Engineer, mi responsabilidad fue diseñar e implementar la infraestructura de datos del proyecto.

Desarrollé el módulo `data_loader.py`, que implementa la clase `DataLoader`. Esta clase centraliza toda la lógica de carga de datos, incluyendo validación de archivos, manejo robusto de errores, verificación de formatos y logging detallado. Esto garantiza que cualquier parte del sistema que necesite cargar datos lo haga de manera consistente y confiable.

Además, diseñé la arquitectura del pipeline de limpieza en `data_cleaner.py`, estructurándolo como una serie de transformadores modulares de Scikit-Learn. Cada transformador es independiente y reutilizable: ColumnDropper para eliminar columnas innecesarias, TextCleaner para normalizar texto, NAHandler para manejar valores faltantes, NumericConverter para conversiones de tipo, OutlierHandler para validación de rangos, CategoricalNormalizer para estandarización, y MissingValueImputer para imputación inteligente.

Esta arquitectura modular permite que cada etapa del procesamiento sea testeable, mantenible y fácilmente extensible, siguiendo las mejores prácticas de ingeniería de datos."

---

## SECCIÓN 2B: ANÁLISIS Y VALIDACIÓN ESTADÍSTICA (40 segundos)

**[Persona que habla: Iván Cruz Ibarra - Data Scientist]**

"Como Data Scientist, me enfoqué en el análisis exploratorio de datos y la validación estadística del proceso de refactorización.

Desarrollé el pipeline completo de EDA en `eda_pipeline.py`, que orquesta el flujo completo de análisis: carga de datos, limpieza mediante los transformadores diseñados por la Data Engineer, y registro de todas las métricas en MLflow para trazabilidad completa.

También implementé el módulo `eda_visualizer.py` que genera visualizaciones estadísticas profesionales: distribuciones de variables numéricas, análisis de variables categóricas, matriz de correlación, y análisis de la variable objetivo. Estas visualizaciones son fundamentales para entender la calidad de los datos y validar que las transformaciones mantienen la integridad estadística.

Mi responsabilidad crítica fue garantizar que la refactorización produjera resultados estadísticamente idénticos al notebook original. Para esto, desarrollé un proceso de validación exhaustivo que compara datasets columna por columna, valor por valor, confirmando que ambos tienen exactamente la misma forma, tipos de datos y valores. Esta validación es esencial para asegurar que no se introdujeron sesgos durante la refactorización."

---

## SECCIÓN 3: PIPELINES DE SCIKIT-LEARN Y MEJORES PRÁCTICAS (60 segundos)

**[Persona que habla: Sebastián Coronado Rivera - ML Engineer]**

"Como ML Engineer, implementé los pipelines de Machine Learning siguiendo las mejores prácticas de Scikit-Learn.

En el módulo `model_trainer.py`, desarrollé la clase `ModelTrainer` que automatiza el proceso completo de entrenamiento: desde el preprocesamiento de datos hasta la evaluación de modelos. Implementé pipelines que integran técnicas de balanceo con SMOTE, validación cruzada estratificada y búsqueda de hiperparámetros con RandomizedSearchCV.

El pipeline de ML en `ml_pipeline.py` orquesta el flujo completo: carga datos limpios, divide en conjuntos de entrenamiento y prueba, entrena múltiples modelos (Random Forest, KNN, SVM, XGBoost), evalúa cada uno y selecciona el mejor basado en métricas.

Todas las etapas están documentadas, son reproducibles y siguen el principio de pipeline de Scikit-Learn, garantizando que cada transformación y modelo pueda ser versionado y reproducido exactamente."

---

## SECCIÓN 4: SEGUIMIENTO DE EXPERIMENTOS CON MLFLOW (45 segundos)

**[Persona que habla: Sebastián Coronado Rivera - ML Engineer]**

"Integré MLflow para el seguimiento completo de experimentos y gestión de modelos.

Cada ejecución del pipeline registra automáticamente: parámetros de configuración, métricas de evaluación (accuracy, precision, recall, F1-score), artefactos como los datasets procesados y los modelos entrenados, y metadatos de ejecución.

El sistema de tracking permite comparar diferentes experimentos, visualizar métricas en tiempo real a través del UI de MLflow, y mantener un registro de versiones de modelos con sus hiperparámetros y resultados.

También implementé el registro automático de modelos en el Model Registry de MLflow, incluyendo versionado, tags y metadatos que permiten gestión profesional del ciclo de vida de modelos."

---

## SECCIÓN 5: CONTAINERIZACIÓN Y DEVOPS (45 segundos)

**[Persona que habla: Alicia Canta Pandal - DevOps Engineer]**

"Mi responsabilidad fue containerizar todo el proyecto para garantizar reproducibilidad completa e integrar control de versiones de datos con AWS S3.

Creé el `Dockerfile` que define un entorno Python 3.10 con todas las dependencias necesarias, y configuré `docker-compose.yml` con ocho servicios: DVC pull para obtener datos de S3, EDA pipeline, ML pipeline, comparación de datasets, generación de visualizaciones, ejecución de tests, servidor MLflow y un shell interactivo para desarrollo.

Además, implementé la integración completa de DVC con AWS S3: configuré scripts de setup para conectar el bucket S3 de forma automatizada, implementé servicios de pull y push de datos, y configuré el sistema para que todos los pipelines obtengan automáticamente los datos más recientes desde el almacenamiento en la nube antes de ejecutarse.

La containerización asegura que cualquier desarrollador pueda ejecutar el proyecto sin preocuparse por versiones de Python o dependencias del sistema. Los volúmenes montados permiten persistencia de datos entre ejecuciones y acceso directo a modelos y reportes desde el sistema local. La integración con S3 permite que todo el equipo comparta datasets y modelos de forma eficiente y versionada."

---

## SECCIÓN 6: TESTING Y VALIDACIÓN (30 segundos)

**[Persona que habla: Sebastián Coronado Rivera - ML Engineer]**

"Implementé una suite completa de tests unitarios para validar que el código refactorizado produce resultados idénticos al notebook original.

Desarrollé doce tests en `test_comparison.py` que validan: existencia de archivos, coincidencia de formas de datos, coincidencia de columnas y tipos de datos, valores idénticos tanto numéricos como categóricos, manejo correcto de valores faltantes y normalización de categorías. También implementé `test_ml_pipeline.py` para validar el pipeline completo de machine learning.

Todos los tests se ejecutan automáticamente con pytest y deben pasar antes de considerar cualquier cambio como válido. Esto garantiza que la refactorización no introdujo errores y mantiene la integridad de los resultados."

---

## SECCIÓN 7: RESULTADOS Y VALIDACIÓN (40 segundos)

**[Persona que habla: Mayra Hernández Alba - Data Engineer - 20 segundos]**

"Desde la perspectiva de ingeniería de datos, validamos que el pipeline refactorizado procesa los datos de manera eficiente y confiable.

El script `compare_datasets.py` que desarrollamos compara exhaustivamente ambos datasets, verificando no solo la estructura sino también la integridad de las transformaciones aplicadas. Confirmamos que cada transformador del pipeline funciona correctamente y en el orden adecuado, procesando 2153 registros y generando exactamente 17 columnas limpias, sin pérdida de información.

Los tests unitarios validan que cada componente del pipeline - desde la carga hasta la imputación final - funciona de manera aislada y en conjunto, garantizando que el flujo de datos es robusto y reproducible."

**[Persona que habla: Iván Cruz Ibarra - Data Scientist - 20 segundos]**

"Desde la perspectiva estadística, la validación demuestra que la refactorización mantiene perfectamente la integridad de los datos.

Comparación detallada muestra: misma forma (2153 filas, 17 columnas), mismas columnas en idéntico orden, mismos tipos de datos para cada columna, y -crítico- valores 100% idénticos en cada celda, tanto numéricos como categóricos. Ambos datasets tienen cero valores faltantes.

Los 12 tests unitarios cubren validaciones estadísticas específicas: rangos numéricos, normalización categórica, manejo de outliers, y preservación de distribuciones. Todos pasan exitosamente, confirmando que la refactorización no introdujo ningún sesgo estadístico y que los resultados son completamente equivalentes al análisis original."

---

## CONCLUSIÓN Y PRÓXIMOS PASOS (45 segundos)

**[Persona que habla: Cualquier miembro del equipo o coordinador]**

"Este proyecto demuestra la aplicación exitosa de buenas prácticas de MLOps: estructura profesional con Cookiecutter, código refactorizado con POO y pipelines de Scikit-Learn, seguimiento de experimentos con MLflow, containerización con Docker, y validación exhaustiva mediante testing.

Todos los objetivos de la actividad fueron cumplidos:
✓ Estructuración con plantilla Cookiecutter
✓ Refactorización del código con POO
✓ Pipelines de Scikit-Learn para automatización
✓ Seguimiento de experimentos con MLflow
✓ Containerización para reproducibilidad
✓ Testing comprehensivo

El proyecto está listo para continuar con las siguientes fases: despliegue de modelos, creación de APIs para predicciones, y automatización del pipeline completo.

Para más detalles, consulten nuestro repositorio en GitHub [mencionar URL] donde pueden ver el historial de commits de todos los integrantes y revisar el código completo."

---

## NOTAS PARA LA GRABACIÓN

1. **Tiempo por sección:** 
   - Introducción: 30s
   - Sección 1: 45s (ML Engineer - Sebastián)
   - Sección 2A: 40s (Data Engineer - Mayra)
   - Sección 2B: 40s (Data Scientist - Iván)
   - Sección 3: 60s (ML Engineer - Sebastián)
   - Sección 4: 45s (ML Engineer - Sebastián)
   - Sección 5: 45s (DevOps Engineer - Alicia)
   - Sección 6: 30s (ML Engineer - Sebastián)
   - Sección 7: 40s (Data Engineer 20s + Data Scientist 20s)
   - Conclusión: 45s
   - **Total: 4 minutos 40 segundos** (deja 20 segundos de margen)

2. **Recomendaciones:**
   - Cada persona debe presentar su sección de manera clara y profesional
   - Muestren el código o la interfaz cuando sea relevante
   - Pueden usar capturas de pantalla de MLflow UI, resultados de tests, o estructura de directorios
   - Mantengan un tono profesional pero accesible

3. **Elementos visuales sugeridos:**
   - Estructura de directorios del proyecto
   - Captura de MLflow UI mostrando experimentos
   - Resultados de tests (12/12 passed)
   - Comparación de datasets mostrando que son idénticos
   - Ejemplo de código refactorizado (una clase o módulo)

4. **Transiciones:**
   - Hagan transiciones suaves entre secciones
   - Mencionen cómo su trabajo se integra con el de otros miembros del equipo
   - Destaquen la colaboración entre roles
   - En particular, Mayra (Data Engineer) e Iván (Data Scientist) deben mencionar cómo colaboraron

5. **Equilibrio de participación:**
   - ML Engineer (Sebastián): 45s + 60s + 45s + 30s = 180 segundos (3 minutos)
   - Data Engineer (Mayra): 40s + 20s = 60 segundos
   - Data Scientist (Iván): 40s + 20s = 60 segundos
   - DevOps Engineer (Alicia): 45 segundos
   - Todos tienen participación significativa

---

## CHECKLIST PRE-GRABACIÓN

- [ ] Todos los miembros han revisado el guion
- [ ] Se ha asignado quién presenta cada sección
- [ ] Se han preparado capturas de pantalla o demos visuales
- [ ] El repositorio está actualizado con todos los commits
- [ ] Se ha verificado que todos los servicios funcionan correctamente
- [ ] Se tiene el link del repositorio listo para mencionar

