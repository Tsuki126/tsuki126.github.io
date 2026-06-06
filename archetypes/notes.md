+++
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
slug = '{{ .File.ContentBaseName }}'
date = {{ .Date }}
draft = true
+++