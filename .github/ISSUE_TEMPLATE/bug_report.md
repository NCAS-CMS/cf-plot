---
name: Bug report
about: Report something that is not working or not working as it should
title: ''
labels: bug
assignees: ''

---

Thank you for considering opening an Issue for cf-plot. Before you submit one, please
ensure you are familiar with our contributing guidelines, which can be found
[here in a dedicated section in the documentation](https://ncas-cms.github.io/cf-plot/support.html).
We also have a [code of conduct](https://github.com/NCAS-CMS/cf-plot/blob/main/CODE_OF_CONDUCT.md)
to facilitate a respectful and welcoming environment which you
should abide by.

For a bug report, at a minimum please provide information according the sections below.

### Subject of the issue
Describe your issue here.

### Steps to reproduce
Tell us how to reproduce this issue.

### Your environment
The version of cf-plot and its dependencies in which you are encountering an issue.

The best and preferred way to share this is by sharing the output of `cf.environment(paths=False)`
run within the code you have noticed the bug in. If you aren't also using cf-python and haven't
imported `cf`, do `import cf` first (note the reason this is useful
is because cf-plot and cf-python share a large amount of dependencies so it makes
sense to have one call which can report back on dependencies for both libraries).

### Expected behaviour
Tell us what should happen.

### Actual behaviour
Tell us what happens instead. If you see an error please provide the traceback, ideally in full.

It may be useful to share a plot, where the behaviour concerns a plot not displaying the intended plot.
(plus correct plots to compare this to, if you have those from using different software or environments).

### Relevant data

If the bug occurs for a specific dataset, please indicate a way to access the data you were using when
the issue occurred, either as a data file to send, a path on JASMIN if you use that, or by sharing the
output of `f.dump()` for the field `f` which displays the issue (or the same for multiple fields if applicable),
as close as possible to the code line where the issue manifests.
