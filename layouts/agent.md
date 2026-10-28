# {{ .Title }}

> {{ .Params.lead }}

## How it works

1. Install Blowhorn for Mac and the Blowhorn browser extension.
2. {{ .Params.wire_title }}: {{ .Params.wire_body }}
3. Say what you want. {{ .Params.tool }} turns it into blowhorn commands, and you approve what publishes.

`{{ .Params.wire_file }}`

```{{ .Params.wire_lang }}
{{ .Params.wire_code }}
```
{{ with .Params.extra_file }}
`{{ . }}`

```{{ $.Params.extra_lang }}
{{ $.Params.extra_code }}
```
{{ end }}
{{- with .Params.prompts }}
## Try saying
{{ range . }}
- "{{ . }}"
{{- end }}
{{ end }}
## Commands

```{{ .Params.commands_lang | default "bash" }}
{{ .Params.commands }}
```

## Where it pays off
{{ range .Params.uses }}
- **{{ .t }}**: {{ .b }}
{{- end }}

## What {{ cond (eq .File.ContentBaseName "cli") "the CLI" .Params.tool }} can do on each platform
{{ range sort hugo.Data.platforms "weight" }}
{{- $pl := . }}
### {{ $pl.name }}

{{ $pl.reach }}. [{{ $pl.name }} docs]({{ $pl.docs | absURL }})
{{ range $pl.actions }}
{{- $act := partial "action-resolve.html" . }}
- **[{{ $act.name }}]({{ $pl.docs | absURL }}#{{ $act.slug }})**: {{ $act.description }}{{ with $act.limits }} Limits: {{ . }}{{ end }}
{{- end }}
{{ end }}
## Frequently Asked Questions {#questions}
{{ range .Params.faq }}
**{{ .q }}** {{ .a }}
{{ end }}
