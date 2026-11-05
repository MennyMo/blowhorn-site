{{- /* Markdown output of signup-form: the form itself needs a browser, so
  point at the page that carries it. */ -}}
{{- $kind := .Get "kind" | default "waitlist" -}}
{{- if eq $kind "waitlist" -}}
Sign up to be notified when this feature ships: [signup form]({{ .Page.RelPermalink }}).
{{- else -}}
Sign up for the Blowhorn newsletter: [signup form]({{ .Page.RelPermalink }}).
{{- end }}
