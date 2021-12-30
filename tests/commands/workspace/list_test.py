from pathlib import Path
from typing import Callable

from tests.conftest import run


def test_workspace_list(create_fixture_workspace: Callable[[str], Path]) -> None:
    create_fixture_workspace("list/basic")

    assert run("poetry", "workspace", "list") == """\
liba
libb"""

    assert run("poetry", "workspace", "list", "--show-external") == """\
typing-extensions
zipp
importlib-metadata
pyparsing
atomicwrites
attrs
colorama
more-itertools
packaging
pluggy
py
wcwidth
numpy
pytest
pytz
liba
libb"""

    assert run("poetry", "workspace", "list", "--show-external", "-o", "json") == """\
{
  "atomicwrites": {},
  "attrs": {},
  "colorama": {},
  "importlib-metadata": {
    "typing-extensions": {},
    "zipp": {}
  },
  "liba": {
    "pytz": {},
    "pytest": {
      "atomicwrites": {},
      "attrs": {},
      "colorama": {},
      "importlib-metadata": {
        "typing-extensions": {},
        "zipp": {}
      },
      "more-itertools": {},
      "packaging": {
        "pyparsing": {}
      },
      "pluggy": {
        "importlib-metadata": {
          "typing-extensions": {},
          "zipp": {}
        }
      },
      "py": {},
      "wcwidth": {}
    },
    "numpy": {}
  },
  "libb": {
    "liba": {
      "pytz": {},
      "pytest": {
        "atomicwrites": {},
        "attrs": {},
        "colorama": {},
        "importlib-metadata": {
          "typing-extensions": {},
          "zipp": {}
        },
        "more-itertools": {},
        "packaging": {
          "pyparsing": {}
        },
        "pluggy": {
          "importlib-metadata": {
            "typing-extensions": {},
            "zipp": {}
          }
        },
        "py": {},
        "wcwidth": {}
      },
      "numpy": {}
    },
    "pytz": {}
  },
  "more-itertools": {},
  "numpy": {},
  "packaging": {
    "pyparsing": {}
  },
  "pluggy": {
    "importlib-metadata": {
      "typing-extensions": {},
      "zipp": {}
    }
  },
  "py": {},
  "pyparsing": {},
  "pytest": {
    "atomicwrites": {},
    "attrs": {},
    "colorama": {},
    "importlib-metadata": {
      "typing-extensions": {},
      "zipp": {}
    },
    "more-itertools": {},
    "packaging": {
      "pyparsing": {}
    },
    "pluggy": {
      "importlib-metadata": {
        "typing-extensions": {},
        "zipp": {}
      }
    },
    "py": {},
    "wcwidth": {}
  },
  "pytz": {},
  "typing-extensions": {},
  "wcwidth": {},
  "zipp": {}
}"""

    assert run("poetry", "workspace", "list", "--show-external", "-o", "tree") == """\
atomicwrites

attrs

colorama

importlib-metadata
├── typing-extensions
└── zipp

liba
├── pytz
├── pytest
│   ├── atomicwrites
│   ├── attrs
│   ├── colorama
│   ├── importlib-metadata
│   │   ├── typing-extensions
│   │   └── zipp
│   ├── more-itertools
│   ├── packaging
│   │   └── pyparsing
│   ├── pluggy
│   │   └── importlib-metadata
│   │       ├── typing-extensions
│   │       └── zipp
│   ├── py
│   └── wcwidth
└── numpy

libb
├── liba
│   ├── pytz
│   ├── pytest
│   │   ├── atomicwrites
│   │   ├── attrs
│   │   ├── colorama
│   │   ├── importlib-metadata
│   │   │   ├── typing-extensions
│   │   │   └── zipp
│   │   ├── more-itertools
│   │   ├── packaging
│   │   │   └── pyparsing
│   │   ├── pluggy
│   │   │   └── importlib-metadata
│   │   │       ├── typing-extensions
│   │   │       └── zipp
│   │   ├── py
│   │   └── wcwidth
│   └── numpy
└── pytz

more-itertools

numpy

packaging
└── pyparsing

pluggy
└── importlib-metadata
    ├── typing-extensions
    └── zipp

py

pyparsing

pytest
├── atomicwrites
├── attrs
├── colorama
├── importlib-metadata
│   ├── typing-extensions
│   └── zipp
├── more-itertools
├── packaging
│   └── pyparsing
├── pluggy
│   └── importlib-metadata
│       ├── typing-extensions
│       └── zipp
├── py
└── wcwidth

pytz

typing-extensions

wcwidth

zipp"""
