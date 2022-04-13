from context_engine import init_engine, Context, Engine, Frame
from ctx import Ctx
import typing as t

        
def get_process_skeleton(steps:t.List[str]=[]):
    return {
        "process":steps
    }
    
def get_step(name:str=None,expressions:t.List[str]=None,args:t.Any=None):
    return {
        "step":name,
        "expressions":expressions,
        "args":args
        
    }

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
    
def get_while(conditions:t.List[str]=[],steps:t.List[t.Any]=[]):    
    return{
        "flow":"while",
        "conditions":conditions,
        "steps":steps,
        
    }
    
def get_do_while(conditions:t.List[str]=[],steps:t.List[t.Any]=[]):    
    return{
        "flow":"do while",
        "conditions":conditions,
        "steps":steps,
        
    }
    
    
def get_for_each(collection:str='',var:str='',steps:t.List[t.Any]=[]):    
    return{
        "flow":"for each",
        "collection":collection,
        "steps":steps,
        "var":var
        
    }

def get_try(steps:t.List[t.Any]=[],elsesteps:t.List[t.Any]=None):    
    return{
        "flow":"if",
        "steps":steps,
        "elsesteps":elsesteps
        
    }
    
        
def test_context():
    test_process = get_process_skeleton([get_step('teststep')])
    
    engine, context = init_engine(test_process)
    
    assert len(engine.steps) == 1
    
def test_engine_component_can_set_context():
    test_process = get_process_skeleton([get_step('teststep')])
    engine, context = init_engine(test_process)
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert context.test == 'Pass'
    
def test_engine_component_can_call_context_expressions():
    test_process = get_process_skeleton([get_step('teststep')])
    engine, context = init_engine(test_process)
    
    @engine.component()
    def teststep(context):
        context.set("test","Pass")
        
    engine.run()
    
    assert context.test == 'Pass'
    
def test_engine_is_finished_when_finished():
    test_process = get_process_skeleton([get_step('teststep')])
    engine, context = init_engine(test_process)
    
    assert engine.is_finished == False
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert engine.is_finished == True
    
def test_context_expression_set():
    test_process = get_process_skeleton([get_expression(['set("thing",True)'])])
    engine, context = init_engine(test_process)
    
    assert engine.is_finished == False
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert context.thing == True

def test_context_step_without_spec_remains_unfinished():
    test_process = get_process_skeleton([get_expression(['set("thing",testexpression("name","is"))'])])
    engine, context = init_engine(test_process)
    
    assert engine.is_finished == False
    
    @context.expression()
    def testexpression(context,name,suffix):
        return f"{name}_{suffix}"
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
      
    assert "test" not in context.keys()     
    
def test_context_expression_custom():
    test_process = get_process_skeleton([get_expression(['set("thing",testexpression("name","is"))'])])
    engine, context = init_engine(test_process)
    
    @context.expression()
    def testexpression(context,name,suffix):
        return f"{name}_{suffix}"
        
    engine.run()

    assert context.thing == "name_is"
    
def test_context_expression_custom_var_replacement():
    test_process = get_process_skeleton([get_expression(['set("thing",testexpression(name_field,"is"))'])])
    
    engine, context = init_engine(test_process)
    
    context.name_field = 'timmy'
     
    @context.expression()
    def testexpression(context,name,suffix):
        return f"{name}_{suffix}"
        
    engine.run()
    
    assert engine.is_finished == True 
    
    assert context.thing == "timmy_is"
                 
def test_stack_frame_current_step():
    frame = Frame()
    context = Context(frame)

        
    step1 = get_step("step1",args="path_1")
    step2 = get_step("step2",args="path_2")
    
    step1 = frame.push_step(step1)
    
    assert context.current_step is step1
    
    step2 = frame.push_step(step2)
    
    assert context.current_step is step2
    
    frame.pop_step()
    
    assert context.current_step is step1
    
    
def test_for_each_local_variable():
    steps = [ get_expression(["set(f'test_{locals.i}',True)"]) ]
    fl = get_for_each('test_col','i',steps)
    pd = get_process_skeleton([fl])
    
    engine, context = init_engine(pd)
    
    context.test_col = [ x for x in range(1)]
    
    engine.run()
    
    assert context.test_0 == True
    
def test_for_each_local_variable_multi():
    steps = [ get_expression(["set(f'test_{locals.i}',True)"]) ]
    fl = get_for_each('test_col','i',steps)
    pd = get_process_skeleton([fl])
    
    engine, context = init_engine(pd)
    
    context.test_col = [ x for x in range(4)]
    
    engine.run()
    
    assert context.test_3 == True
    
    
    
    
    
