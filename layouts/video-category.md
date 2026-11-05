# {{ .Title }}

> {{ .Description }}

{{- range .RegularPages.ByDate.Reverse }}
- [{{ .Title }}]({{ .Permalink }}) - {{ .Description }}{{ with .Params.duration }} ({{ . }}){{ end }}
{{- end }}
