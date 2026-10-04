using Test

include(joinpath(@__DIR__, "..", "utils.jl"))

@testset "Recent publications use the full publication list" begin
    @test isdefined(Main, :recent_publications)
    if isdefined(Main, :recent_publications)
        source = """
        ## In Preparation
        1. Unannounced work
        ## Preprints
        1. A. Author, [New preprint](https://example.org/preprint)
        ## Journal articles
        1. B. Author, [Newest article](https://example.org/new), Journal (2025)
        2. C. Author, Second article (2025)
        3. D. Author, Third article (2024)
        4. E. Author, Older article (2022)
        ## Japanese articles
        1. Japanese article
        """
        recent = recent_publications(source)
        @test occursin("[New preprint](https://example.org/preprint)", recent)
        @test occursin("[Newest article](https://example.org/new)", recent)
        @test occursin("- [New preprint](https://example.org/preprint)\n  ~~~<span class=\"publication-meta\">~~~A. Author~~~</span>~~~", recent)
        @test occursin("B. Author · Journal (2025)", recent)
        @test occursin("Third article", recent)
        @test !occursin("Older article", recent)
        @test !occursin("Unannounced work", recent)
        @test !occursin("Japanese article", recent)
        @test count(line -> startswith(line, "- "), split(recent, '\n')) == 4
        @test occursin("Updated article", recent_publications(replace(source, "Newest article" => "Updated article")))
        @test isempty(recent_publications(""))
        @test recent_publications("## Preprints\n1. Only one paper") == "- Only one paper"
    end
end

@testset "Full publications preserve sections and linked entries" begin
    source = """
    ## In Preparation
    1. Hidden draft
    ## Preprints
    1. A. Author, [Preprint](https://example.org/preprint)
    ## Journal articles
    1. B. Author, [Paper](https://example.org/paper), Journal (2025)
    ## Japanese articles
    1. 著者, "[日本語の記事](https://example.org/japanese)", 会誌 (2024)
    """
    full = full_publications(source)
    @test count(line -> startswith(line, "## "), split(full, '\n')) == 3
    @test count(line -> startswith(line, "- ["), split(full, '\n')) == 3
    @test occursin("著者 · 会誌 (2024)", full)
    @test occursin("B. Author · Journal (2025)", full)
    @test !occursin("Hidden draft", full)
    @test !occursin("In Preparation", full)
end
