@def title = "Menu 3"

# Presentations

\toc

## International conference

1. R. Sakurai, W. Mizukami, and H. Shinaoka, 
“Hybrid quantum-classical algorithm for computing imaginary-time correlation function”, 
International Conference on Strongly Correlated Electron Systems 2020, 
ブラジル, 2021年9月(ポスター発表)

2. R. Sakurai, W. Mizukami, and H. Shinaoka, 
“Hybrid quantum-classical algorithm for computing imaginary-time correlation function”, 
American Physical Society, シカゴ, 2022年3月(ポスター発表)

3. R. Sakurai, W. Mizukami, and H. Shinaoka, “Hybrid quantum-classical algorithm for computing imaginary-time correlation function”, 
29 th International Conference on Low Temperature Physics, 
Sapporo, 2022年8月, ポスター発表予定



## Domestic conference

4. 櫻井理人, 福元好志, 
相互作用を拡張した古典フラクタルコードに信頼して埋め込める情報量,
[日本物理学会第75回年次大会](https://w4.gakkai-web.net/jps_search/2020sp/index.html),名古屋大学, 19aPS-21, 2020年3月, (ポスター発表)


## Customising tag lists

By default the tag list is very simple: it just collects all pages that match the tags and it shows them in a simple list by anti-chronological order (more recent at the top).

You can customise this by defining your own `hfun_custom_taglist` function in the `utils.jl` file. The commented blueprint for the simple default setting is below and should give you an idea of how to  write your own generator.

Assuming you've defined such a function, don't forget to use `{{custom_taglist}}` in the `_layout/tag.html` instead of the default `{{taglist}}`.

```julia
function hfun_custom_taglist()::String
    # -----------------------------------------
    # Part1: Retrieve all pages associated with
    #  the tag & sort them
    # -----------------------------------------
    # retrieve the tag string
    tag = locvar(:fd_tag)
    # recover the relative paths to all pages that have that
    # tag, these are paths like /blog/page1
    rpaths = globvar("fd_tag_pages")[tag]
    # you might want to sort these pages by chronological order
    # you could also only show the most recent 5 etc...
    sorter(p) = begin
        # retrieve the "date" field of the page if defined, otherwise
        # use the date of creation of the file
        pvd = pagevar(p, :date)
        if isnothing(pvd)
            return Date(Dates.unix2datetime(stat(p * ".md").ctime))
        end
        return pvd
    end
    sort!(rpaths, by=sorter, rev=true)

    # --------------------------------
    # Part2: Write the HTML to plug in
    # --------------------------------
    # instantiate a buffer in which we will write the HTML
    # to plug in the tag page
    c = IOBuffer()
    write(c, "...1...")
    # go over all paths
    for rpath in rpaths
        # recover the url corresponding to the rpath
        url = get_url(rpath)
        # recover the title of the page if there is one defined,
        # if there isn't, fallback on the path to the page
        title = pagevar(rpath, "title")
        if isnothing(title)
            title = "/$rpath/"
        end
        # write some appropriate HTML
        write(c, "...2...")
    end
    # finish the HTML
    write(c, "...3...")
    # return the HTML string
    return String(take!(c))
end
```

For instance the default uses:

```html
<!-- 1, 3: simple list-->
<ul>...</ul>
<!-- 2: simple list item plugging in path + title -->
<li><a href="/$rpath/">$title</a></li>
```
