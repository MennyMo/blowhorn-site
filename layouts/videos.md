# {{ .Title }}

> {{ .Params.lead }}

{{- range .Sections.ByWeight }}

## {{ .Title }}
{{- range .RegularPages.ByDate.Reverse }}
- [{{ .Title }}]({{ .Permalink }}) - {{ .Description }}{{ with .Params.duration }} ({{ . }}){{ end }}
{{- end }}
{{- end }}
