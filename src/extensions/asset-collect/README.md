# Purpose and background

data from services need to be represented as assets in the connector. Therefore, an extension is required that would gather those and invoke them as assets in the connector. Preferably by api, but purpose is to be able to add features to the extention to handle other methods if necessairy

## api collector

we have:
    - file as a setting
    - reading file content
    - extract from json (cool would be to have sth like requests.get(guts) )

we still need:
    - parse content
      - parsing response according to pattern provided in the file
      - making response into assets

we want also:
    - idk yet
