from ast import arg
import types
import typing as t
import decorator


def get_composite_key_value(dictionary:dict,key:str,value:any=None):
    next_key = key.split(".",1)
    
    if len(next_key) == 2:
        get_composite_key_value(dictionary[next_key[0]],next_key[1],value)
    elif value is not None:
        dictionary[next_key[0]] = value
    else:
        return dictionary[next_key[0]]

@decorator.decorator
def default_var_when_none(f, engine, step,*args,**kwargs):
    step.var = step.var or '_'
    f(engine,step,*args,**kwargs)

def preprocess_args(fun, varnames):
    """ Applie function to var in varnames before launching the function"""
    
    def wrapper(f, *args, **kwargs):
        
        #version test
        if hasattr(f,"func_code"):
            func_code = f.func_code #2
        else:
            func_code = f.__code__ #3
            
        names = func_code.co_varnames
        new_args = [fun(arg) if (name in varnames) else arg for (arg, name) in zip(args,names)]
        new_kwargs = {k: fun(v) if k in varnames else v for (k,v) in kwargs.items()}
        
        return f(*new_args,**new_kwargs)
    return decorator.decorator(wrapper)

@decorator.decorator
def push_pop_step(f, engine, step,*args,**kwargs):
    step.var = step.var or '_'
    step = engine.frame.push_step(step)
    f(engine,step,*args,**kwargs)
    engine.frame.push_step(step)
    
# @decorator.decorator
# def pop_stack_when_complete(f, engine, step,*args,**kwargs):
#     step.var = step.var or '_'
#     f(engine,step,*args,**kwargs)

class Command:
    """Callable base class for engine components and context expressions
    """
    def __init__(
        self,
        name: t.Optional[str],
        command,
    ) -> None:
        self.name = name
        self.command:F = command
        self.context = None
               
    def set_context(self,context):
        self.context = context               
    
    def __call__(self,*args, **kwargs):
        self.command(self.context)

        
class Component(Command):
    def __init__(self, name: t.Optional[str], command) -> None:
        self.engine = None
        super().__init__(name, command)
    def set_engine(self,engine):
        self.engine = engine  
    def __call__(self,*args, **kwargs):
        return self.command(self.engine,self.context,*args,**kwargs)    
        
class Expression(Command):
    def __init__(self, name: t.Optional[str], command) -> None:
        super().__init__(name, command)
    
    def __call__(self,*args, **kwargs):
        return self.command(self.context,*args,**kwargs)
    
class FlowComponent(Component):
    def __init__(self, name: t.Optional[str], command) -> None:
        super().__init__(name, command)
    
    def __call__(self,*args, **kwargs):
        return self.command(self.engine,*args,**kwargs)
    


F = t.TypeVar("F", bound=t.Callable[..., t.Any])
            
FC = t.TypeVar("FC", bound=t.Union[t.Callable[..., t.Any], Command])            

def expression(
    name: t.Optional[str] = None,
    cls: t.Optional[t.Type[Command]] = None,
    **attrs: t.Any,
)-> t.Callable[[F], Expression]: #-----------------------------------------
    
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
)-> t.Callable[[F], Component]: #-----------------------------------------
    
    if cls is None:
        cls = Component
    
    def decorator(f: t.Callable[..., t.Any]) -> Command:
        cmd = _make_command(f,name,attrs,cls)
        cmd.__doc__ = __doc__
        return cmd
    return decorator

def flow_component(
    name: t.Optional[str] = None,
    cls: t.Optional[t.Type[Command]] = None,
    *attrs: t.Any,
)-> t.Callable[[F], FlowComponent]: #-----------------------------------------
    
    if cls is None:
        cls = FlowComponent
    
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