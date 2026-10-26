{{- /* Markdown output for a role, use-case or solutions index. Either .kind
  (this section's pages) or .groups (section, kind, title), as cast-index.html. */ -}}
{{- $page := .page -}}
{{- $groups := .groups | default (slice (dict "section" $page "kind" .kind "title" "")) -}}
# {{ $page.Title }}

> {{ $page.Params.lead }}
{{ range $groups }}{{ $meta := partial "cast-kind.html" (dict "kind" .kind) }}{{ $kind := .kind }}{{ with .title }}
## {{ . }}
{{ end }}{{ range .section.Pages.ByWeight }}{{ $item := partial "role-data.html" (dict "page" . "kind" $kind) }}
- [{{ $meta.labelPrefix }}{{ $item.name }}: {{ $item.headline }}]({{ .Permalink }})
{{- end }}
{{ end -}}
