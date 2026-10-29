# {{ .Title }}

> {{ .Params.lead }}

{{ with .Params.kits -}}
- Download full brand kit: [{{ .full.url | absURL }}]({{ .full.url | absURL }}) (ZIP, {{ .full.size }}). Logos, colors, type, usage rules, Major Blowhorn, the troops and Old Thunderlung.
- Download logos only: [{{ .logos.url | absURL }}]({{ .logos.url | absURL }}) (ZIP, {{ .logos.size }}). Logos, icons and wordmarks in SVG and PNG, light and dark.
{{- end }}

## Logo

The Crowhorn: a megaphone that is also a rooster. Use the horizontal lockup unless the space says otherwise, and pick the file drawn for the ground it sits on.
{{ range (.Params.lockups | append .Params.marks | append .Params.wordmarks) }}
- [{{ .name }}]({{ printf "assets/brand/logo/%s" .file | absURL }}){{ with .note }}: {{ . }}{{ end }}
{{- end }}

## Clear space and minimum size

- Clear space: half the icon's height on every side.
- Minimum sizes: horizontal lockup 96 px wide, stacked lockup 64 px, icon 24 px. Below that, use the favicons.

## Color
{{ range hugo.Data.brand_colors.groups }}
### {{ .name }}
{{ range .colors }}
- {{ .name }}: {{ .hex }}, rgb({{ delimit .rgb ", " }}). {{ .use }}
{{- end }}
{{ end }}
## Type
{{ range .Params.fonts }}
- {{ .family }} ({{ .role }}): {{ .weights }}. {{ .url }}
{{- end }}

## Major Blowhorn

The mascot. Put him on white, light teal or cream, one appearance per page, and keep him off security, billing and legal pages.
{{ range .Params.mascot }}
- {{ .name }}: [PNG]({{ printf "assets/brand/mascot/%s.png" .file | absURL }}), [WebP]({{ printf "assets/brand/mascot/%s.webp" .file | absURL }})
{{- end }}

## Old Thunderlung

Major Blowhorn's family bugle. Six generations of Blowhorns have carried it, and it has the dent to prove it.

It only sounds for real messages to real ears, so bots and bought crowds can't hear it. Nobody else plays it. As Major puts it: "Is not instrument. Is colleague."
{{ range .Params.thunderlung }}
- {{ .name }}: [PNG]({{ printf "assets/brand/mascot/%s.png" .file | absURL }}), [WebP]({{ printf "assets/brand/mascot/%s.webp" .file | absURL }})
{{- end }}

The red cord and tassels are its uniform. The plain version is for small or busy spaces.

## Usage

Do: full color on light grounds; the on-dark file on dark grounds; one color on teal and busy grounds.

Don't: recolor, stretch, squash or rotate the logo; add shadows, glows or gradients; set it on a busy ground; put the full-color icon on teal; retype the wordmark in a font; rearrange the parts; use retired marks or old names.

The name is Blowhorn: one word, capital B. Always just Blowhorn, in formal copy too.
