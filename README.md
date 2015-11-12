Confluence Publisher
====================

*Publishes Sphinx compiled docs to Confluence.*

Supports:

 - confluence versions: 5.5
 - sphinx-build formats: "json", "json_conf"


Installation
------------

.. code-block:: bash
    
    > pip install confluence-publisher


Config format
-------------

Directives:

- **version** (required) Config version. Current is ``2``.
- **url** (required) Base Confluence URL.
- **base_dir** (required) Directory containing json to be published.
- **pages** (required) Pages to be published.

    - **id** (required)  Confluence page ID. If page does not exists, create it with ``conf_page_maker``.
    - **source** (required)  Path to json associated with the page
    - **watermark** (optional)  Watermark  to put on page. E.g.: *Automatic publish with web documentation toolkit*.
    - **link** (optional)  Link under watermark (for example to source rst in repo).
    - **attachments** (optional) Files to be attached.

        - **images**
            - <path_to_img1>
            - <path_to_img2>
        - **downloads** 
            - <path_to_file1>
            - <path_to_file1>
            
    - **pages** Subpages to be published.

        **...**

Config example
--------------

.. code-block:: yaml

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


Publisher
---------

.. code-block:: bash

    > conf_publisher config.yml --auth XXXXXjpwYXNzdXXXXX==


If a config doesn't contain page.id, you can use ``conf_page_maker`` command to create a page and page ID will be put into config automatically.


Parameters
~~~~~~~~~~

<path_to_config> - Path to your configuration file.
    required
    string
    
--auth (-a) - Confluence ``login:password`` encoded with base64.
    required
    string
    
--force (-F) - Publish all pages. Otherwise, publishes only changed or new pages.
    optional
    bool
    
--disable-watermark (-dw) - Remove watermarks in pages.
    optional
    string


Page Maker
----------

Creates new pages and puts page ID into configuration file.

.. code-block:: bash

    > conf_page_maker config.yml --auth XXXXXjpwYXNzdXXXXX== --parent-id 52332132


Parameters
~~~~~~~~~~

<path_to_config> - Path to your configuration file (the same as for ``conf_publisher``).
    required
    string
    
--auth (-a) - Confluence ``login:password`` encoded with base64.
    required
    string

--parent-id (-pid) - Parent page ID.
    required
    string
