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

# menu2.md is the source of truth. Keep each publication on one numbered line,
# with preprints and journal articles ordered newest first within each section.
function recent_publications(markdown::AbstractString)
  entries = String[]
  selected_section = false
  for line in split(markdown, '\n')
    if startswith(line, "## ")
      selected_section = strip(line[4:end]) in ("Preprints", "Journal articles")
    elseif selected_section
      entry = match(r"^\d+\.\s+(.+)$", line)
      isnothing(entry) || push!(entries, "- " * entry.captures[1])
    end
  end
  return join(first(entries, 4), "\n\n")
end

function hfun_recent_publications()
  source = read(joinpath(@__DIR__, "menu2.md"), String)
  return Franklin.fd2html(recent_publications(source), internal=true)
end
