# {{ .Title }}

> {{ .Description }}

- Category: {{ .Parent.Title }}
{{- with .Params.duration }}
- Duration: {{ . }}
{{- end }}
- Published: {{ .Date.Format "2006-01-02" }}
{{- with .Params.video }}
- Watch (MP4): {{ .mp4 | absURL }}
{{- end }}

{{ .Content }}
