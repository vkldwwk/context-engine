from context_engine import init_engine
from ctx import Ctx
import typing as t

        
def get_process_skeleton():
    test_process = Ctx()
    test_process.process = []
    return test_process
    
def get_step(name:str=None,expressions:t.List[str]=None,args:t.Any=None):
    v = Ctx()
    v.step = name
    v.expressions = expressions
    v.args = args
    
    return v

def get_expression(expressions:t.List[str]=None,args:t.Any=None):
    v = Ctx()
    v.expressions = expressions
    v.args = args
    
    return v
    
def get_if(conditions:t.List[str]=None,steps:t.List[t.Any]=None,elsesteps:t.List[t.Any]=None):    
        v = Ctx()
        v.flow = 'if'
        v.conditions = conditions
        v.steps = steps
        v.elsesteps = elsesteps
        
        return v
        
def test_context():
    
    test_process = get_process_skeleton()
    
    test_process.process.append(get_step('teststep'))
    
    engine, context = init_engine(test_process)
    
    assert len(engine.steps) == 1
    
def test_engine_component_can_set_context():
    test_process = get_process_skeleton()
    

    test_process.process.append(get_step('teststep'))
    engine, context = init_engine(test_process)
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert context.test == 'Pass'
    
def test_engine_component_can_call_context_expressions():
    test_process = get_process_skeleton()
    

    test_process.process.append(get_step('teststep'))
    engine, context = init_engine(test_process)
    
    @engine.component()
    def teststep(context):
        context.set("test","Pass")
        
    engine.run()
    
    assert context.test == 'Pass'
    
def test_engine_is_finished_when_finished():
    test_process = get_process_skeleton()
    
    #test_process.process.append(get_step(['set("thing",Ctx()']))
    test_process.process.append(get_step('teststep'))
    engine, context = init_engine(test_process)
    
    assert engine.is_finished == False
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert engine.is_finished == True
    
def test_context_expression_set():
    test_process = get_process_skeleton()
    
    test_process.process.append(get_expression(['set("thing",True)']))
    engine, context = init_engine(test_process)
    
    assert engine.is_finished == False
    
    @engine.component()
    def teststep(context):
        context.test = 'Pass'
        
    engine.run()
    
    assert context.thing == True

def test_context_step_without_spec_remains_unfinished():
    test_process = get_process_skeleton()
    
    test_process.process.append(get_expression(['set("thing",testexpression("name","is"))']))
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
    test_process = get_process_skeleton()
    
    test_process.process.append(get_expression(['set("thing",testexpression("name","is"))']))
    engine, context = init_engine(test_process)
    
    @context.expression()
    def testexpression(context,name,suffix):
        return f"{name}_{suffix}"
        
    engine.run()

    assert context.thing == "name_is"
    
def test_context_expression_custom_var_replacement():
    test_process = get_process_skeleton()
    
    test_process.process.append(get_expression(['set("thing",testexpression(name_field,"is"))']))
    engine, context = init_engine(test_process)
    
    context.name_field = 'timmy'
     
    @context.expression()
    def testexpression(context,name,suffix):
        return f"{name}_{suffix}"
        
    engine.run()
    
    assert engine.is_finished == True 
    
    assert context.thing == "timmy_is"
    
def test_engine_flow_if_conditions_true():
    pass
