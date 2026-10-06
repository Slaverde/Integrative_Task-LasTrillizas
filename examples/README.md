# Example resumes

Resume fragments taken from the assignment, used as reference inputs for the
pipeline and the tests.

| File | Expected profile |
|---|---|
| `resumes/wednesday_addams.txt` | `FULL_STACK_DEVELOPER` |
| `resumes/mary_jane_watson.txt` | `MACHINE_LEARNING_ENGINEER` |

Run a resume through the pipeline once the stages are implemented:

```bash
python -c "from src.main import run_pipeline; print(run_pipeline(open('examples/resumes/wednesday_addams.txt', encoding='utf-8').read()))"
```
