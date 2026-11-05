# {{ .Title }}

> {{ .Params.lead }}

## Videos

{{- $videosSection := site.GetPage "/resources/videos" }}
{{- range $videosSection.RegularPagesRecursive.ByDate.Reverse }}
- [{{ .Title }}]({{ .Permalink }}) - {{ .Description }}
{{- end }}

## Product intelligence

Articles are in the works.

## Field Manual

[Field Manual]({{ (site.GetPage "/field-manual").Permalink }}) - what each feed rewards and punishes.

## Docs

[Docs]({{ (site.GetPage "/docs").Permalink }}) - set up, how-to guides and reference.
