# Branded evidence charts for does-emotional-neglect-cause-autism (2026-08-10)

Three house-style charts, palette validated (dataviz six checks, teal #009499
+ coral #c14a3f on white), rendered at 2x from heritability-charts.html:

1. autism-heritability-vs-environment-inline.webp - genetics 64-91% vs shared
   family environment 7-35% plus a third "Unique to one twin" row ~2-9%
   (Tick et al. 2016, JCPP, PMID 26709141)
2. twin-concordance-autism-inline.webp - identical 0.98 vs fraternal 0.53
   twin correlations (Tick et al. 2016)
3. autism-risk-genetic-relatedness-inline.webp - relative risk by relatedness,
   identical twin 153x to cousin 2.0x (Sandin et al. 2014, JAMA, PMID 24794370;
   an earlier revision of this file misattributed PMID 24196715, which is
   Jones & Klin 2013, Nature)

Amendments after review (this revision): fig1 gained the third row (gray
#9a9484) with legend key and a caption note that the three parts sum to 100%
within each model; fig2's fraternal small-text now reads "share about half of
the genes that vary, same home".

## Shipped 2026-08-10

Uploaded to the MasterMind Webflow site (6627fd62e242d50407cfe12d) after the
MCP connector was re-authorized; CDN byte-verified against these local files:

| file | md5 | asset id |
|---|---|---|
| autism-heritability-vs-environment-inline.webp | 78c83f4124cb411328e8763e473b4992 | 6a7a312d36c8b65f5fb5e728 |
| twin-concordance-autism-inline.webp | ba6526c041dcdc105cfebaf9042b0bb7 | 6a7a312de18736ddd008b5ff |
| autism-risk-genetic-relatedness-inline.webp | fe2e315c9fa90cc98aba285bf118a066 | 6a7a312dc165f7321b287b92 |

Wired into the live article (Blog Posts item 66e7ec0089e32577d87461a5, slug
does-emotional-neglect-cause-autism) as full-width rich-text figures with
descriptive alt text; on save Webflow re-ingested the images under the CMS
asset space (cfe155/6a7a3238... URLs), which is expected. See
../BUILD-RECORD-neglect-ship.md for the full ship record.
