function hfun_bar(vname)
  val = Meta.parse(vname[1])
  return round(sqrt(val), digits=2)
end

function hfun_m1fill(vname)
  var = vname[1]
  return pagevar("index", var)
end

function lx_baz(com, _)
  # keep this first line
  brace_content = Franklin.content(com.braces[1]) # input string
  # do whatever you want here
  return uppercase(brace_content)
end

# _data/publications.md is the source of truth. Keep each publication on one numbered line,
# with preprints and journal articles ordered newest first within each section.
function publication_summary(entry::AbstractString)
  parts = match(r"^(.*?),\s*\"?(\[[^\]]+\]\(\S+\))\"?(?:,\s*(.*))?$", entry)
  isnothing(parts) && return "- " * entry
  authors, title, venue = parts.captures
  metadata = isnothing(venue) ? authors : authors * " · " * venue
  return "- " * title * "\n  ~~~<span class=\"publication-meta\">~~~" * metadata * "~~~</span>~~~"
end

function recent_publications(markdown::AbstractString)
  entries = String[]
  selected_section = false
  for line in split(markdown, '\n')
    if startswith(line, "## ")
      selected_section = strip(line[4:end]) in ("Preprints", "Journal articles")
    elseif selected_section
      entry = match(r"^\d+\.\s+(.+)$", line)
      isnothing(entry) || push!(entries, publication_summary(entry.captures[1]))
    end
  end
  return join(first(entries, 4), "\n\n")
end

function hfun_recent_publications()
  source = read(joinpath(@__DIR__, "_data", "publications.md"), String)
  return "<div class=\"recent-publications publication-list\">" *
    Franklin.fd2html(recent_publications(source), internal=true) * "</div>"
end

function full_publications(markdown::AbstractString)
  lines = String[]
  selected_section = false
  for line in split(markdown, '\n')
    if startswith(line, "## ")
      selected_section = strip(line[4:end]) in ("Preprints", "Journal articles", "Japanese articles")
      selected_section && push!(lines, line)
    elseif selected_section
      entry = match(r"^\d+\.\s+(.+)$", line)
      isnothing(entry) || push!(lines, publication_summary(entry.captures[1]))
    end
  end
  return join(lines, "\n\n")
end

function hfun_full_publications()
  source = read(joinpath(@__DIR__, "_data", "publications.md"), String)
  return "<div class=\"publication-list\">" *
    Franklin.fd2html(full_publications(source), internal=true) * "</div>"
end
