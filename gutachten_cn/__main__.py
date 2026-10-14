"""支持 ``python -m gutachten_cn`` 调用。"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
