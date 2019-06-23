#!/usr/bin/env bash

echo Note: Compiler Error 134 is insignificant, generated code still should work properly.
antlr4 -Dlanguage=Python3 -visitor -no-listener ExtJSON.g4
