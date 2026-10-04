# Rihito Sakurai's website

Personal research website built with [Franklin.jl](https://franklinjl.org/) and published at <https://sakurairihito.github.io/>.

## Local preview

Use Julia 1.13 (the same minor version as CI). With Juliaup:

```sh
juliaup add 1.13
julia +1.13 --project=. -e 'using Pkg; Pkg.instantiate()'
julia +1.13 --project=. -e 'using Franklin; serve()'
```

Open the local URL printed by Franklin. If Julia 1.13 is already your default, `+1.13` can be omitted.

## Editing content

- `index.md`: current affiliations, a brief career history followed by recent publications. Career begins with the April 2024 JSPS postdoctoral fellowship at the University of Tokyo. Education and earlier appointments are omitted. The former `/career/` address redirects to `/#career`.
- `software.md`: software and resources, linked from the main navigation.
- `memories.md`: public research memories, with one figure and a short reflection or research introduction per entry. Images live in `_assets/memories/`. Additional entries can repeat the `memory-entry` article structure with unique IDs, descriptive alt text, a short caption, and a paper link with attribution. Dates are optional. Personal recollections should come from the author.
- `menu2.md`: complete publication list. Keep each publication on one numbered Markdown line, newest first within each section. On each full build, the home page automatically shows the first four entries from **Preprints**, followed by **Journal articles**. Work in preparation is not included in this summary.
- `_layout/` and `_css/`: shared page structure and styling.

The existing `menu1_copy.md` and `menu4_copy.md` drafts and the local `password/` directory are excluded from site generation. The full CV and presentation list are kept outside this public repository; their old `/menu1/` and `/menu3/` pages have been withdrawn. The home page lists current affiliations and career history from the postdoctoral fellowship onward. Earlier versions of these pages remain in Git history.

During `serve()`, editing `menu2.md` refreshes Publications only. Save `index.md` as well, or restart the preview, to refresh the home page's summary. Publishing always runs a full build and includes the latest entries.

## Verify and build

```sh
julia +1.13 --project=. test/runtests.jl
julia +1.13 --project=. -e 'using Franklin; optimize(minify=false, prerender=false, clear=true, suppress_errors=false, fail_on_warning=true)'
```

The generated site is written to `__site/`. Pre-rendering and minification are disabled following [Franklin's recommendation](https://github.com/JuliaDocs/Franklin.jl#important-notes); no separate Python or npm setup is required.

## Publishing

GitHub Actions builds pull requests without deploying. Pushes to `master`, and manual runs on `master`, build the site and publish `__site/` to the existing `gh-pages` branch. GitHub Pages should use that branch's root directory.

The optional GitLab workflow uses the same Julia version and build command.

## Research notes

Numerical research notes are public at `/research/`, linked from the home page and navigation without a password. Edit `research.md` for the index and `compression.md`, `fourier-pricing.md`, or `asian-barrier.md` for the numerical notes. Their figures, data, PDF, and reproduction scripts are in the corresponding `_assets/` directories.

Research ideas are password-encrypted at `/ideas/`, linked as **Ideas 🔒** from the notes index. Only the generated StatiCrypt HTML belongs in this repository. Edit `source/ideas.md` in the external private-notes workspace, build that snapshot, and run its `protect_ideas.py` with the existing password. Deployment checks that the encrypted page exists and no `ideas.md` is present here. Previously published ideas remain in Git history.

The former `/private-notes/` address redirects to the public notes, preserving the old note links. The local private workspace holds the Ideas source and earlier notes as an archive; do not run its old `protect_notes.py` builder. Password files and encryption tools stay outside the repository. Deployment checks that the public notes exist and that the withdrawn CV, presentation list, local drafts, and password directory remain excluded.

Removing files does not remove their earlier versions from Git history.
