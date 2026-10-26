{{- $item := partial "role-data.html" (dict "page" . "kind" "solution") -}}
{{- partial "cast-page-md.md" (dict "item" $item "kind" "solution") -}}
