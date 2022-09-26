import inspect

from solara.alias import reacton, rw
from solara.components import MarkdownIt


@reacton.component
def Sample(code, component):
    locals = globals().copy()
    exec(code, locals)
    c = locals[component]
    with rw.VBox() as main:
        MarkdownIt(
            f"""
```python
{code}
```
"""
        )
        c()
    return main


@reacton.component
def IncludeComponent(component, pre="", highlight=[], **kwargs):
    code = inspect.getsource(component.f)
    with rw.VBox(layout={"padding": "20px", "max_width": "1024px", "border": "1px #333 solid"}) as main:
        MarkdownIt(
            f"""
```python
{pre}{code}
```
""",
            highlight=highlight,
        )
        component(**kwargs)
    return main
