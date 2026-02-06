\ProvidesClass{msurj} % Create custom class
\LoadClass[twocolumn,twoside,9pt]{extarticle} % Basic Class Parameters
\RequirePackage[paperwidth=8.5in,paperheight=11in,lmargin=.5in,rmargin=.5in,tmargin=.625in,bmargin=.625in,footskip=15pt]{geometry}
\RequirePackage{amsmath,amsthm,amssymb}
\RequirePackage{mathrsfs}
\RequirePackage{mathtools}
\RequirePackage{thmtools} 
\RequirePackage{cancel}
\RequirePackage{proof}
\RequirePackage{enumitem}
\usepackage{threeparttable}
\RequirePackage[table]{xcolor}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{titlesec}
\RequirePackage{anyfontsize} % Remove if causing problems
\RequirePackage{sidecap}
\RequirePackage[colorlinks=true,allcolors=blue,allbordercolors=white]{hyperref}
\RequirePackage[font={footnotesize,sf},labelfont=bf, labelsep=period,singlelinecheck=true]{caption}
\RequirePackage{bigints}
\RequirePackage{xfrac}
\RequirePackage{tabularx}
\RequirePackage{fancyhdr}
\RequirePackage{siunitx}
\usepackage{multirow}
\usepackage{multicol}
\hypersetup{allcolors=black} % Default hyperlink colour
\captionsetup{width=.45\textwidth,} % Check
\addtocounter{page}{26} % Editors change depending on article positioning (adds page numbers)
\pagestyle{fancy} % Set page style
\fancyhf{} % fancy header footer
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[LO, RE] {% Sets page number boxes on pages
    \hspace{.25in}\colorbox{black}%
    {\textcolor{white}{\fontsize{8}{9.6}\sffamily%
    \parbox{48pt}{\centering Page~\thepage}}}\hspace{.25in}
}
\fancyfoot[LE]{% Footer information
    \textcolor{gray}{\fontsize{8}{9.6}\sffamily McGill Science Undergraduate Research Journal --- \href{https://msurjonline.mcgill.ca}{\textcolor{gray}{msurjonline.mcgill.ca}}}\hspace{-.25in}%
}
\fancyfoot[RO]{% Footer information
    \hspace{-.25in}\textcolor{gray}{\fontsize{8}{9.6}\sffamily Volume 20 | Issue 1 | April 2025}%
}
\RequirePackage[ % References
    backend=biber,
    style=nature,
]{biblatex}

%%%%%%%%%%%%%%%%%%%% Commands to change references %%%%%%%%%%%%

\renewbibmacro*{name:andothers}{% Use "et al." when >5 authors
  \ifboolexpr
    {
      test {\ifnumequal{\value{listcount}}{\value{liststop}}}
      and
      test \ifmorenames
    }
    {
      \ifnumgreater{\value{liststop}}{1}
        {\finalandcomma}
        {}%
      \andothersdelim
      \bibstring{andothers}%
    }
    {}%
}

% Create website reference
\DeclareFieldFormat[website]{title}{#1}
\DeclareFieldFormat[website]{url}{\href{#1}{#1}}

\DeclareBibliographyDriver{website}{%
  \usebibmacro{bibindex}%
  \usebibmacro{begentry}%
  \printnames{author}%
  \setunit{\addperiod\addspace}%
  \printfield{title}%
  \newunit\newblock
  \setunit{\addspace}%
  \printtext{\printfield[parens]{year}; }
  \printfield{url}
  %\printfield{addendum}
  \iflistundef{pageref}{}{\usebibmacro{pageref}}\iflistundef{shorthand}{}{\usebibmacro{shorthand}}}

% Changes to the article reference style
\DeclareBibliographyDriver{article}{%
  \usebibmacro{bibindex}%
  \usebibmacro{begentry}%
  \printnames{author}%
  \setunit{\addspace}%
  \printfield{title}%
  \newunit\newblock
  \printfield{journaltitle}%
  \setunit{\addspace}%
  \printfield{volume}%
  \setunit{\addcomma\addspace}%
  \printfield{pages}%
  \setunit{\addspace}%
  \printfield{note}
  \printtext{\printfield[parens]{year}. }
  \iffieldundef{doi}
    {}
    {\href{\thefield{doi}}{\thefield{doi}}}
  %\setunit{\addspace}%
  %\usebibmacro{finentry}}
  \iflistundef{pageref}{}{\usebibmacro{pageref}}\iflistundef{shorthand}{}{\usebibmacro{shorthand}}}

\DeclareBibliographyDriver{report}{%
  \usebibmacro{bibindex}%
  \usebibmacro{begentry}%
  \printnames{author}%
  \setunit{\addperiod\addspace}%
  \printtext{\printfield{title}}%
  \newunit\newblock
  \printfield{institution}%
  \setunit{\addcomma\addspace}%
  \printfield{pages}%
  \setunit{\addperiod\addspace}%
  \printfield{note}
  \printtext{\printfield[parens]{year}. }
  \iffieldundef{doi}
    {}
    {\href{\thefield{doi}}{\thefield{doi}}}
  %\setunit{\addspace}%
  %\usebibmacro{finentry}}
  \iflistundef{pageref}{}{\usebibmacro{pageref}}\iflistundef{shorthand}{}{\usebibmacro{shorthand}}}

% Changes to incollection
\DeclareBibliographyDriver{incollection}{%
  \usebibmacro{bibindex}%
  \usebibmacro{begentry}%
  \printnames{author}%
  \setunit{\addperiod\addspace}%
  \printtext{in \printfield{booktitle}}%
  \newunit\newblock
  \setunit{\addspace}%
  \printtext{(\bibstring{editors} \printnames{editor}) }
  \printfield{pages}
  \printfield{chapter}
  \printtext{(\printlist{publisher}, \printfield{year}).}
  \printfield{url}
  \printfield{addendum}
  \iflistundef{pageref}{}{\usebibmacro{pageref}}\iflistundef{shorthand}{}{\usebibmacro{shorthand}}}

% Redefine \cite so that there are no brackets
\DeclareCiteCommand{\cite}
  {}
  {\bibhyperref{\printfield{labelnumber}}}
  {\multicitedelim}
  {}

%%%%%%%%%%%%%%%%%%%% End of commands %%%%%%%%%%%%%%%%%

\addbibresource{bib.bib}

\renewcommand{\eqref}[1]{\textup{\ref{#1}}} % Change equation reference to remove parentheses

\renewcommand{\qedsymbol}{$\blacksquare$} % QED symbol for proofs
\setlist[enumerate]{itemsep=\smallskipamount,parsep=0pt,label={\rm \roman*)}} % List styles
\setlist[itemize]{itemsep=\smallskipamount,parsep=0pt}
\newtheorem{thm}{Theorem} % Create Shortcuts for theorems, defns, etc.
\newtheorem{dfn}{Definition}
\newtheorem{pro}{Proposition}
\newtheorem{lem}{Lemma}
\newtheorem{cor}{Corollary}
\theoremstyle{definition}
\newtheorem{exm}{Example}
\newcommand{\F}{\mathbb{F}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\hr}{\begin{center}
    \rule{.99\textwidth}{1pt}
\end{center}}
\RequirePackage{fontspec}
\setmainfont[ % Main font
BoldFont=MinionPro-bold.otf,
ItalicFont=MinionPro-Italic.otf,
BoldItalicFont=MinionPro-BoldIt.otf
]{MinionPro-Regular.otf}[
Path = Fonts/,
Extension = .otf
]
\setsansfont[ % Alternate sans font
BoldFont=MyriadPro-Bold.otf,
ItalicFont=MyriadPro-It.otf,
BoldItalicFont=MyriadPro-BoldIt.otf
]{MyriadPro-Regular.otf}[
Path = Fonts/,
Extension = .otf
]
\usepackage{fix-cm}
\setlength{\parskip}{9pt} % Standard Paragraph spacing and indent
\setlength{\parindent}{0pt}
\newcommand*{\YZraggedright}{
    \raggedright
    \exhyphenpenalty 0 
}
\def\blackbox#1{ % Black box configuration
    \hspace{-.75in}\colorbox{black}{\color{white}\fontsize{9}{9}\sffamily\parbox{\linewidth+.75in-3\fboxsep}{\raggedleft \vspace{2pt}#1\hspace{3pt}\vspace{2pt}}}
}

% Alternate format to indent start of black boxes in case of different printing specifications
% \def\blackbox#1{ % Black box configuration
%    \hspace{-.375in}\colorbox{black}{\color{white}\fontsize{9}{9}\sffamily\parbox{\linewidth+.375in-3\fboxsep}{\raggedleft #1 }}
% }

\long\def\maketitle#1#2#3#4#5#6#7#8{ 
\begin{minipage}[t]{1.4083in} % Configure left column on first page
\sffamily 
    \begin{flushright}
        \textsuperscript{Submitted: #3}\\
        \textsuperscript{Accepted: 03/05/2025}\\
        \textsuperscript{Published: 03/31/2025}\\
    \end{flushright}
    \smallskip
    \setlength{\fboxsep}{1pt}
    
    \blackbox{\vphantom{y} #4} % Article Type
    \smallskip 
    
    {\raggedright \fontsize{8}{9.6}\sffamily#5} % Affiliation 
    
    \smallskip
    \smallskip
    \blackbox{Keywords}
    
    \smallskip 
    {\raggedright \fontsize{7}{7}\sffamily
    \parbox[t]{1.4083in}{\setlength{\baselineskip}{9pt}#6}}  % Keywords
    
    \bigskip
    \blackbox{Email Correspondence}
    
    \smallskip
    {\raggedleft \fontsize{7}{7}\sffamily\href{mailto:#7}{#7}}
    
    \bigskip
    {\raggedright \fontsize{7}{7}\sffamily
    \href{https://doi.org/10.26443/msurj.v20i1.216}{https://doi.org/10.26443/msurj.v20i1.216}}
    
    \bigskip
    {\raggedright \fontsize{7}{5}\sffamily\parbox[t]{1.4083in}{\setlength{\baselineskip}{9pt}\rightskip=0pt plus 2em \copyright\, The Authors. This article is published under a CC-BY license: \href{https://creativecommons.org/licenses/by/4.0/}{https://creativecommons.org/\allowbreak licenses/\allowbreak by/4.0/}}}
 %doi and copyright 
\end{minipage}
\hfill
\begin{minipage}[t]{5.667in} % Title minipage on right
\sffamily
{\YZraggedright
    {\fontsize{11}{13.2}\sffamily #1} % Authors
    \vspace{-\smallskipamount}
    
    {\fontsize{22}{26.4pt}\sffamily #2 \strut} % Article Title
    \bigskip 

    {\fontsize{12}{14.4}\sffamily Abstract} \smallskip 
}

    \setlength{\parskip}{9pt}
    {#8} \bigskip % Abstract
\end{minipage}
\hr \bigskip   
}
\titleformat*{\section}{\fontsize{12}{14.4}\sffamily} % Subtitle formatting for numbered and non-numbered sections.
\titleformat*{\subsection}{\sffamily}
\titleformat*{\subsubsection}{\sffamily}
\titlespacing{\section}{0pt}{2\parskip}{0pt}
\titlespacing{\subsection}{0pt}{\parskip}{0pt}
\titlespacing{\subsubsection}{0pt}{.5\parskip}{0pt}
\renewcommand{\thefootnote}{\fnsymbol{footnote}}
\setcounter{secnumdepth}{0} % Automatically removes section numbers