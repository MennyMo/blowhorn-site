{{- /* Markdown output of supported-actions: same data, as a list. */ -}}
{{- $key := .Get 0 -}}
{{- $d := index hugo.Data.platforms $key -}}
{{- $row := false -}}
{{- range site.Data.integrations.platforms -}}
  {{- if eq .id $key }}{{ $row = . }}{{ end -}}
{{- end -}}
{{- if not $row }}{{ errorf "supported-actions: %q is not in data/integrations.json platforms" $key }}{{ end -}}
{{- $actions := slice -}}
{{- if $d }}{{ with $d.actions }}{{ $actions = . }}{{ end }}{{ end -}}
{{- if $actions }}
{{ range $actions }}
{{- $a := partial "action-resolve.html" . }}
- **[{{ $a.name }}]({{ printf "#%s" $a.slug }})**: {{ $a.description }}{{ with $a.limits }} Limits: {{ . }}{{ end }}
{{- end }}
{{- else }}
- **None yet**: This platform isn't available yet.
{{- end }}
