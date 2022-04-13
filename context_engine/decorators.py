import types
import typing as t
from .engine import Command, Component, Expression



F = t.TypeVar("F", bound=t.Callable[..., t.Any])
            
FC = t.TypeVar("FC", bound=t.Union[t.Callable[..., t.Any], Command])            

def expression(
    name: t.Optional[str] = None,
    cls: t.Optional[t.Type[Command]] = None,
    **attrs: t.Any,
)-> t.Callable[[F], Command]: #-----------------------------------------
    
    if cls is None:
        cls = Expression
    
    def decorator(f: t.Callable[..., t.Any]) -> Command:
        cmd = _make_command(f,name,attrs, cls)
        cmd.__doc__ = __doc__
        return cmd
    
    return decorator

def component(
    name: t.Optional[str] = None,
    cls: t.Optional[t.Type[Command]] = None,
    *attrs: t.Any,
)-> t.Callable[[F], Command]: #-----------------------------------------
    
    if cls is None:
        cls = Component
    
    def decorator(f: t.Callable[..., t.Any]) -> Command:
        cmd = _make_command(f,name,attrs,cls)
        cmd.__doc__ = __doc__
        return cmd
    return decorator



def _make_command(
      f:F,
      name: t.Optional[str],
      attrs: t.Any,
      cls: t.Type[Command] = None ,
  ) -> Command: #------------------------------------------------
    
    return cls(
        name=name or f.__name__.lower(),
        command=f,
        *attrs,
    )