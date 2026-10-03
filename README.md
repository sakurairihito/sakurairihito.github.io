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

- `index.md`: current affiliations, publication summary, and software/resources.
- `menu2.md`: complete publication list. Keep each publication on one numbered Markdown line, newest first within each section. On each full build, the home page automatically shows the first four entries from **Preprints**, followed by **Journal articles**. Work in preparation is not included in this summary.
- `menu3.md`: presentations, newest first within each category; undated entries come last.
- `_layout/` and `_css/`: shared page structure and styling.

The existing `menu1_copy.md` and `menu4_copy.md` drafts and the local `password/` directory are excluded from site generation. The full CV is kept outside this public repository; its old `/menu1/` page has been withdrawn. The home page lists current affiliations only. Earlier versions of the CV remain in Git history.

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

## Private research notes

Research notes and their figures, numerical data, and reproduction scripts have been withdrawn from the public site and current source tree. Their password-encrypted bundle is published at `/private-notes/`, linked as **Research notes 🔒** from the home page and public navigation. Visitors must enter the password to read the notes. `private-notes/index.html` is generated with StatiCrypt 3.5.4 and contains encrypted content only. Images, data, and downloadable scripts are bundled inside the encryption; they are not published separately.

Keep the plaintext source, encryption tools, and password outside this public repository. To update the encrypted HTML, use the local private-notes workspace and copy only its encrypted output here. Do not edit the generated ciphertext by hand. The deployment workflow checks that the encrypted page exists and the old plaintext routes and assets are absent before publishing.

Removing files does not remove their earlier versions from Git history.
