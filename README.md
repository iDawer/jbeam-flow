**JBeam Flow** is an add-on for [Blender](https://www.blender.org/) aiming to provide 
editing support for [BeamNG.drive](https://beamng.com) vehicles.

**Project status: Preview.**
JBeam Flow is not production ready.
Lot's of things have to be completed yet.

## Features

 - Vehicle jBeam file import.
 - jBeam specific commands for editing.
 - jBeam export.
 - _todo_: Skin import/edit/export.

### jBeam to Blender feature map

|jBeam              |Blender                |
|-------------------|-----------------------|
|Vehicle            |Scene                  |
|jBeam file         |Group                  |
|Part               |Object                 |
|Part properties    |Custom properties      |
|Geometry:          |BMesh:                 |
|node               |vertex                 |
|beam               |edge                   |
|surface            |face                   |
|Geometry properties|BMesh custom data layer|
|_todo:_ Skin       |Texture                |

For more details see `jbeam_utils.py` file.

## Requirements

 - Blender version `2.78a` is well tested.
   `>=2.80` does not (yet) work.
 - ANTLR 4.7.2 toolkit and it's Python3 runtime.

## Installing

1) Manually copy `jbeam_flow` directory into Blender's `addons` directory.
   Check [Blender docs](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html)
   for directory layout.
2) Get [`antlr4-python3-runtime 4.7.2`](https://pypi.org/project/antlr4-python3-runtime/4.7.2/).
   Extract `src/antlr4` directory into Blender's `modules` directory.
3) Generate jbeam file parser in `jbeam_flow/jbeam/ext_json/`
   - [Install ANTLR 4.7.2 toolkit](https://github.com/antlr/antlr4/blob/4.7.2/doc/getting-started.md#installation).
   - `cd` into the `ext_json` directory and generate the parser:
      ```sh
      antlr4 -Dlanguage=Python3 -visitor -no-listener ExtJSON.g4
      ```

## Usage

Enable the add-on in Blender.
Invoke `Import JBeam (.jbeam)` or `JBeam vehicle` command to import existing assets.

_Todo: expand/more docs_
