+++
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
slug = '{{ .File.ContentBaseName }}'
date = {{ .Date }}
categories = ["thinking"]
draft = true
+++