# Confluence Publisher

[![Build Status](https://travis-ci.org/Arello-Mobile/confluence-publisher.svg?branch=master)](https://travis-ci.org/Arello-Mobile/confluence-publisher)

Set of tools to help publish documentation to Confluence. It includes:

- conf_publisher
- conf_page_maker

This tools use own configuration file.

For now it supports:
 - confluence versions: 5.5 - 5.9
 - sphinx-build formats: "fjson", "html"

## Installation

    > pip install confluence-publisher

## Publisher

    > conf_publisher config.yml --auth XXXXXjpwYXNzdXXXXX==

If a config doesn't contain page.id, you can use ``conf_page_maker`` command
to create a page and page ID will be put into config automatically.

```
usage: conf_publisher [-h] [-u URL] [-a AUTH] [-F] [-w WATERMARK] [-l LINK]
                      [-ht] [-v]
                      config

Publish documentation (Sphinx fjson) to Confluence

positional arguments:
  config                Configuration file

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Confluence Url
  -a AUTH, --auth AUTH  Base64 encoded user:password string
  -F, --force           Publish not changed page.
  -w WATERMARK, --watermark WATERMARK
                        Overrides the watermarks. Also can be "False" to
                        remove all watermarks; or "True" to add watermarkswith
                        default text: "Automatically generated content. Do not
                        edit directly." on all pages.
  -l LINK, --link LINK  Overrides page link. If value is "False" then removes
                        the link.
  -ht, --hold-titles    Do not change page titles while publishing.
  -v, --verbose
```

## Page Maker

    > conf_page_maker config.yml --auth XXXXXjpwYXNzdXXXXX== --parent-id 52332132

```
usage: conf_page_maker [-h] [-u URL] [-a AUTH] [-pid PARENT_ID] [-v] config

Create Confluence pages and update configuration file with it ids

positional arguments:
  config                Configuration file

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Confluence Url
  -a AUTH, --auth AUTH  Base64 encoded user:password string
  -pid PARENT_ID, --parent-id PARENT_ID
                        Parent page ID in confluence.
  -v, --verbose
```

## Configuration file format

Directives:

- **version** (required) Config version. Current is ``2``.
- **url** (required) Base Confluence URL.
- **base_dir** (required) Directory containing json to be published.
- **downloads_dir** (optional) Default is _downloads
- **images_dir** (optional) Default is _images
- **source_ext** (optional) Default is .fjson
- **pages** (required) Pages to be published.

    - **id** (required)  Confluence page ID. If page does not exists, create it with ``conf_page_maker``.
    - **title** (optional)
    - **source** (required)  Path to json associated with the page
    - **link** (optional)  Link under watermark (for example to source rst in repo).
    - **watermark** (optional)  Watermark  to put on page. E.g.: "Automatically generated content. Do not edit directly"".
    - **attachments** (optional) Files to be attached.

        - **images**
            - path_to_img1
            - path_to_img2
        - **downloads**
            - path_to_file1
            - path_to_file2
    - **pages** Subpages to be published.

        - **...** same structure as for pages


### Config example

```
  version: 2
  url: https://confluence.atlassian.com
  base_dir: docs/build/json
  pages:
  - attachments:
      downloads:
      - check_required_keywords.sh
    id: 49807825
    source: part_1/newcomers
    watermark: <b>Automatic Publish</b>
    link: https://github.com/pet-project/doc.rst
  - id: 49807842
    pages:
    - id: 49807843
      source: part_1/development/start
    - id: 49807844
      source: part_1/development/structure
    - id: 49807845
      source: part_1/development/documentation
    - id: 49807846
      source: part_1/development/logs
    source: part_1/development/index
  - attachments:
      downloads:
      - release.sh
    id: 49807847
    source: part_1/release
  - id: 49807848
    source: part_1/deployment
  - id: 49807849
    source: part_1/tools
  - id: 49807850
    source: part_1/plans
  - attachments:
      images:
      - 38-aval_1.jpg
      - 38-aval_2.jpg
    id: 49807851
    source: part_2/availability
```

or more JSONify style:

```
{
  version: 2,
  base_dir: "result",
  pages: [
    {
      id: 52136662,
      source: "release_history"
    }
  ]
}
```
