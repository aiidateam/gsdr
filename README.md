[![Templated from python-copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mbercx/python-copier/refs/heads/main/docs/img/badge.json)](https://github.com/mbercx/python-copier)

# `gsrd`

A small Gray-Scott reaction-diffusion simulator, packaged as a single CLI command:

```bash
gsrd input.yaml
```

It reads a YAML parameter file, runs a 2D reaction-diffusion integration, and writes the final fields to `results.npz` in the current directory.

## Purpose

`gsrd` is built as the running example for a workflow-engine tutorial.
Its interface is deliberately designed to *emulate the conventions and quirks of real-world scientific codes* — the kind of legacy tooling that workflow managers typically wrap.
This makes it a realistic teaching target: many of the integration issues users encounter when wrapping established scientific software can be demonstrated here in a small, self-contained Python package.

## Design choices

| Aspect | Behaviour | Mirrors |
|---|---|---|
| Invocation | Single positional argument, no flags, no `--help` | Minimal-CLI binaries from the Fortran era |
| Output location | Hardcoded `./results.npz` in the working directory | Codes that write fixed-name files |
| Stdout | Verbose startup banner, citation block, progress lines, formatted diagnostics | Standard scientific-code log output |
| Scalar results | Printed to stdout only (`variance_V`, `mean_V`); not stored in the output file | Codes whose key numbers must be parsed from the log |
| Array results | Written to `results.npz` (`U_final`, `V_final`) | Binary outputs alongside textual logs |
| Parameter echo | Required keys printed; extra YAML keys silently retained in the output's `params` record | Tolerant input parsers with no schema enforcement |
| Restart mechanism | If `init/U_init.npy` and `init/V_init.npy` exist in the working directory, they are used as initial fields | Codes that pick up restart files from the run directory |
| Error reporting | Short stderr message (`ERR: ...`); exit code is always `0`; success is signalled by a `JOB DONE` marker on stdout | Codes whose exit codes are not reliably informative |
| No-arguments behaviour | Prints the banner and waits on stdin | "Waiting for input" pattern of interactive scientific binaries |

These are intentional design choices for pedagogical value, not bugs.
The point is to give users a realistic surface to practise wrapping: parsing log output, handling fixed-name files, providing restart inputs, dealing with uninformative exit codes, and validating input schemas at the workflow layer rather than relying on the code itself.

## Input format

A YAML file with the following keys:

```yaml
F: 0.04          # feed rate
k: 0.065         # kill rate
du: 0.16         # diffusion coefficient of U
dv: 0.08         # diffusion coefficient of V
dt: 1.0          # time step
grid_size: 64    # grid is grid_size x grid_size
n_steps: 3000    # number of integration steps
seed: 42         # (optional) RNG seed
```

## Output

On success, `results.npz` contains:

- `U_final`, `V_final` — final concentration fields, shape `(grid_size, grid_size)`
- `params` — the parameters as a JSON-serialised string

Scalar diagnostics (`variance_V`, `mean_V`) appear on stdout in the *Diagnostics* block; they are not written to the output file.
