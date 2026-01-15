You can extend doti18n to support custom file formats by implementing a custom loader. Loaders are **automatically registered** upon class definition.

### Requirements
To create a loader, define a class that inherits from `doti18n.loaders.BaseLoader` and meets these criteria:

1.  **`file_extension`**: A string attribute defining the extension (e.g., `.custom`).
2.  **`__init__`**: Must accept a `strict: bool` argument.
3.  **`load` method**: Must read the file and return data in one of these formats:
    - **Single locale:** `{ "en": { ... } }` (derived from filename).
    - **Multilocale:** `[ { "en": {...} }, { "fr": {...} } ]`.

!!! warning "Execution order"
    If you initialize `LocaleData` with `preload=True`, you **must** define or import your custom loader **before** creating the `LocaleData` instance.
    
    **Why?** With preloading enabled, `LocaleData` scans the directory immediately upon initialization. If your loader class hasn't been defined yet, it won't be in the registry, and your custom files will be ignored.

### Example Implementation

```python
import os
from typing import Union, Optional, Dict, List
from pathlib import Path

from doti18n.loaders import BaseLoader
# import custom_parser 

class CustomLoader(BaseLoader):
    file_extension = ".custom"
    
    def __init__(self, strict: bool = False):
        self._strict = strict
    
    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        # 1. Read file content
        with open(filepath, encoding='utf-8') as file:
            content = file.read()
        
        # 2. Parse data (using your custom logic)
        # data = custom_parser.parse(content)
        data = {"mock_key": "mock_value"} 

        # 3. Determine locale (usually from filename)
        locale = os.path.splitext(os.path.basename(filepath))[0]
        
        # 4. Return strictly typed dict: {locale: data}
        return {locale: data}
```