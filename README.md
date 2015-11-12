Confluence Publisher
====================

Utility publishes Sphinx compiled docs to Confluence

Support:

 - confluence versions: 5.5
 - sphinx-build formats: "json", "json_conf"


Getting it
----------

pip install confluence-publisher


Configuration file format
-------------------------

Directives:

- version(required)  # Config version. Current is 2
- url(required)  # Base Confluence URL
- base_dir(required)  # Folder with json for publishing to Confluence
- pages(required)  # Pages for publishing
    - id(required)  # Confluence page ID. If page does not exists, it can make with `conf_page_maker` 
    - source(required)  # Path to json associated with page
    - watermark(optional)  # Watermark on confluence page, for example: Automatic publish with web documentation toolkit.
    - link(optional)  # Link (for example to source rst in repo) under watermark 
    - attachments(optional)  # attachment files
        - images  # Page images
            - <path_to_img>  # Page image path
            - <path_to_img>
        - downloads # Downloads
            - <path_to_file>  # Page file path
            - <path_to_file>
            
    - pages  # Pages for publishing inside current
        ...

Example:

```
---
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

Publishing
----------

```
conf_publisher config.yml --auth XXXXXjpwYXNzdXXXXX==
```

If page id is empty in config, use ``conf_page_maker`` for page creating. Page id set to the config automatically.


Parameters
~~~~~~~~~~


<path_to_config> - Config path
    required
    string
    
--auth(-a) - base64 encode confluence login:password
    required
    string
    
--force(-F) - Publish all pages. Otherwise, publish only changed or new pages.
    optional
    bool
    
--disable-watermark(-dw) - Remove watermark in all pages
    optional
    string


Page Maker
----------

Create new pages and set page id to the config 

```
conf_page_maker config.yml --auth XXXXXjpwYXNzdXXXXX== --parent-id 52332132
```

Parameters
~~~~~~~~~~

<path_to_config> - Config path (the same for conf_publisher)
    required
    string
    
--auth(-a) - base64 encode confluence login:password
    required
    string

--parent-id(-pid) - parent page id
    required
    string
