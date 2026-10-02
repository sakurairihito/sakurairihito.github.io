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

- `index.md`: introduction, affiliations, research interests, and software/resources.
- `menu1.md`: CV and career history.
- `menu2.md`: complete publication list. Keep each publication on one numbered Markdown line, newest first within each section. On each full build, the home page automatically shows the first four entries from **Preprints**, followed by **Journal articles**. Work in preparation is not included in this summary.
- `menu3.md`: presentations, newest first within each category; undated entries come last.
- `_layout/` and `_css/`: shared page structure and styling.

The existing `menu1_copy.md` and `menu4_copy.md` drafts are excluded from site generation.

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
