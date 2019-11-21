# Bib-Crawler
!! Works only for hep-th papers !!
Creates references.bib from inspire-hep 
References must be given in form of standard inspire-hep ref keys.

Checks .tex file for \cite{XYZ}, searches inspire-hep for XYZ and finds the inspire-refid associated to the paper
Then goes to http://inspirehep.net/record/refid/export/hx and finds the bibitem in the html
Does some more formatting and saves to references.bib (after renaming any existing ones)

Use examples:

bibcrawler.py 
 .. Relative path to .tex file: letterv22.tex
 imported bib items to mypath/references.bib
 runtime: 18.847268104553223

bibcrawler.py mypaper.tex
 renamed old reference file: mypath/referencesOld.bib
 imported bib items to mypath/references.bib
 runtime: 14.374775886535645
