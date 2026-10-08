# ResumeLens

Integrative Task 1 de Computación y Estructuras Discretas III (2026-2).

ResumeLens recibe una hoja de vida en texto plano y revisa si las calificaciones que el candidato menciona cumplen el patrón de un perfil profesional. No rankea candidatos ni decide a quién contratar, solo verifica si se cumple un patrón definido formalmente.

Hoy en día cualquiera puede buscar palabras clave en un CV, pero lo difícil es que `JS`, `Javascript` y `JavaScript` cuenten como lo mismo. Por eso el proyecto usa lenguajes formales en cada etapa, de esta forma cada decisión se puede explicar con un modelo y no con un `if` suelto.

## Equipo

Equipo **Las Trillizas** (E35)

| Integrante | Responsabilidad principal |
|---|---|
| Santiago Laverde | Contratos entre módulos, etapa 1 (expresiones regulares) y etapa 4 (DSL con textX y HTML) |
| Mauricio Marin | Revisión de literatura, definición de perfiles y etapa 3 (autómatas finitos) |
| Alejandro Arango | Etapa 2 (transductores), ordenamiento, pipeline, UI y pruebas de integración |

IDEs: Visual Studio Code e IntelliJ IDEA.

## Cómo funciona

El texto pasa por cuatro etapas, una detrás de otra. Cada una usa un modelo formal distinto.

| Etapa | Qué hace | Modelo formal | Librería | Carpeta |
|---|---|---|---|---|
| 1. Extracción | Saca contacto, estudios, experiencia y habilidades tal como las escribió el candidato | Expresiones regulares | `re` | `src/extraction` |
| 2. Normalización | Convierte las variantes a una forma canónica (`JS` a `JAVASCRIPT`) y las ordena según el perfil | Transductores de estado finito | `pyformlang` | `src/normalization` |
| 3. Reconocimiento | Acepta o rechaza la secuencia normalizada para cada perfil | Autómatas finitos | `pyformlang` | `src/classification` |
| 4. Lenguaje del candidato | Valida el perfil estructurado y genera la visualización en HTML | Gramática libre de contexto | `textX` | `src/dsl` |

Los cuatro perfiles (Full Stack Developer, Machine Learning Engineer y los dos que definimos nosotros) pasan por el mismo código. Lo único que cambia entre perfiles son los datos: el orden canónico y el autómata. Las entradas y salidas de cada módulo están en [docs/contracts.md](docs/contracts.md).

Ejemplo del enunciado:

```
Texto:          JS, React.js, NodeJS, Postgres, Git
Etapa 1:        JS | React.js | NodeJS | Postgres | Git
Etapa 2:        JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
Etapa 3:        FULL_STACK_DEVELOPER -> ACCEPTED
Etapa 4:        perfil validado y HTML del candidato
```

## Estado

| Etapa | Estado |
|---|---|
| 1. Extracción | Lista, con pruebas y documentación |
| 2. Normalización | Pendiente |
| 3. Reconocimiento | Pendiente |
| 4. DSL y HTML | Gramática textX y validación listas, falta generar el HTML |

Los perfiles `BACKEND_DEVELOPER` y `DATA_SCIENTIST` son provisionales hasta que el profesor confirme los requisitos de los dos perfiles propios.

## Estructura del repositorio

```
docs/       diseño, formalización y casos de prueba
examples/   hojas de vida de ejemplo
src/        una carpeta por etapa y main.py con el pipeline
tests/      pruebas automáticas
```

## Cómo correrlo

Necesitas Python 3.10 o superior.

```bash
pip install -r requirements.txt
python -m pytest
```

Para ver la etapa 1 sobre una hoja de vida de ejemplo:

```bash
python -c "from src.extraction import extract; print(extract(open('examples/resumes/wednesday_addams.txt', encoding='utf-8').read()))"
```

## Documentación

- [Requisitos y trazabilidad](docs/requirements.md): qué pide el enunciado y dónde lo cubrimos.
- [Contratos entre módulos](docs/contracts.md): entradas y salidas de cada función.
- [Etapa 1, expresiones regulares](docs/extraction-regex.md): cada patrón, qué reconoce y sus límites.
- [Etapa 1, casos de prueba](docs/test-cases-extraction.md): escenarios y resultados esperados.
- [Etapa 4, gramática del DSL](docs/dsl-grammar.md): EBNF, terminales, no terminales y qué rechaza.
- [Hojas de vida y sentencias de ejemplo](examples/README.md).
