# Example resumes

Hojas de vida de ejemplo para probar el pipeline y las pruebas automáticas.
Las dos primeras salen del enunciado, las otras las escribimos nosotros para
cubrir casos distintos (idioma, formato, variantes de escritura).

| Archivo | Perfil esperado | Qué tiene de particular |
|---|---|---|
| `resumes/wednesday_addams.txt` | `FULL_STACK_DEVELOPER` | Ejemplo del enunciado |
| `resumes/mary_jane_watson.txt` | `MACHINE_LEARNING_ENGINEER` | Ejemplo del enunciado |
| `resumes/ana_torres.txt` | `FULL_STACK_DEVELOPER` | Variantes de escritura (`Javascript`, `ReactJS`, `Node js`, `Mongo DB`) |
| `resumes/carlos_ruiz.txt` | `BACKEND_DEVELOPER` (provisional) | Inglés, viñetas, habilidades en mayúscula, link con punto final |
| `resumes/laura_gomez.txt` | `DATA_SCIENTIST` (provisional) | Español, tildes, nombre en mayúsculas, habilidades en minúscula |
| `resumes/sofia_nunez.txt` | ninguno | Sin habilidades técnicas, sirve para probar el rechazo |

Los perfiles marcados como provisionales cambian si el profesor define otros
requisitos.

Para ver la etapa 1 sobre una hoja de vida:

```bash
python -c "from src.extraction import extract; print(extract(open('examples/resumes/wednesday_addams.txt', encoding='utf-8').read()))"
```

## Sentencias del DSL

En `dsl/` están las sentencias del lenguaje de perfil del candidato (etapa 4,
ver [docs/dsl-grammar.md](../docs/dsl-grammar.md)).

| Carpeta | Contenido |
|---|---|
| `dsl/valid/` | Cuatro sentencias válidas, desde la más pequeña (`sofia_nunez.rl`) hasta la que usa todas las secciones (`laura_gomez.rl`) |
| `dsl/invalid/` | 17 sentencias inválidas. El prefijo del nombre dice el tipo de error: `lexical_`, `syntax_` o `semantic_`. La primera línea de cada archivo explica por qué se rechaza |

Los errores léxicos y sintácticos los rechaza la gramática. Los semánticos
(`semantic_`) son sintácticamente correctos y los rechaza la validación
posterior.
