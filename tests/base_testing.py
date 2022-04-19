from context_engine import Context,Engine
from functools import update_wrapper
import typing as t

def if_single_make_array(f,*args,**kwargs):
    def wrapper(f):
        val = f(*args,**kwargs)
        if val is list:
            return val
        else:
            return [val]
    update_wrapper(wrapper,f)
    return wrapper

def get_process_skeleton(steps:t.List[str]=[]):
    return {
        "process":steps
    }

@if_single_make_array    
def get_step(name:str=None,expressions:t.List[str]=None,args:t.Any=None):
    return {
        "step":name,
        "expressions":expressions,
        "args":args
        
    }

@if_single_make_array
def get_expression(expressions:t.List[str]=None):
    return {
        "expressions": expressions
    }
    
    
def get_if(conditions:t.List[str]=[],steps:t.List[t.Any]=[],elsesteps:t.List[t.Any]=None):    
    return{
        "flow":"if",
        "conditions":conditions,
        "steps":steps,
        "elsesteps":elsesteps
        
    }
    
def get_while(conditions:t.List[str]=[],steps:t.List[t.Any]=[],var:str=None):    
    return{
        "flow":"while",
        "conditions":conditions,
        "steps":steps,
        "var":var
    }
    
def get_do_while(conditions:t.List[str]=[],steps:t.List[t.Any]=[],var:str=None):    
    return{
        "flow":"do while",
        "conditions":conditions,
        "steps":steps,
        "var":var
    }
    
    
def get_for_each(collection:str='',var:t.Union[str,t.List[str]]='',steps:t.List[t.Any]=[]):    
    return{
        "flow":"for each",
        "collection":collection,
        "steps":steps,
        "var":var
        
    }

def get_try(steps:t.List[t.Any]=[],catchsteps:t.List[t.Any]=None):    
    return{
        "flow":"try",
        "steps":steps,
        "catchsteps":catchsteps
        
    }
def get_block(steps:t.List[t.Any]=[],expressions:t.List[str]=[]):
    return {
        "flow": "block",
        "steps":steps,
        "expressions":expressions
    }
    