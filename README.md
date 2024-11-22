# Site generator for the journal _Imaginations_

These scripts perform the following functions for generating a complete issue of the journal _Imaginations_:

1. conversion of copyedited docx files into markdown (where they are cleaned up.) Requires pandoc and lua filter.
2. access to metadata that are entered in OJS through the OJS API (OJS 3.3).
3. conversion of markdown files to html (requires pandoc and depends on json metadata)
4. generation of article cover pages from json in html format
5. generation of front page and front matter from json (html and pdf)
6. generation of a cover image from front page (PDF to png)
7. generation of article PDFs from html files and html cover pages
8. generation of the complete issue PDF from html front matter and html files
9. Consistent updates when data are changed in OJS

## Guiding principles

- minimal computing, avoid over-engineering
- single language, modular design
- minimize dependencies (python standard library including Tkinter, Beautiful Soup, pandoc, prince)
- integrate into OJS workflows
- each script is a tool in the workflow
- components can be swapped out
- open standards, human-readable, archivable formats: json, markdown, html (self-contained: images, fonts are base64 encoded)
- OS-independent
