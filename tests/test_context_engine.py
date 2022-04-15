from multiprocessing import context
from context_engine import init_engine, Context, Engine, Frame
from ctx import Ctx
import typing as t

from context_engine.engine import Flow, Step

        
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
    
        
def test_init_engine_set_process_steps():
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
    
def test_if_condition_false_steps_not_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    fi = get_if(['t1 == True'],steps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = False    
    engine.run()
    
    assert 'test' not in context.keys()
    
def test_if_condition_true_steps_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    fi = get_if(['t1 == True'],steps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True    
    engine.run()
    
    assert context.test == True
    
def test_if_multi_condition_false_steps_not_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    fi = get_if(['t1 == True','t2 == False'],steps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True
    context.t2 = True
        
    engine.run()
    
    assert 'test' not in context.keys()   
    
def test_if_multi_condition_true_steps_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    fi = get_if(['t1 == True','t2 == False'],steps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True
    context.t2 = False
        
    engine.run()   
    assert context.test == True
    
def test_if_condition_false_elsesteps_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    elsesteps = [ get_expression(["set(f'otherTest',False)"]) ]
    fi = get_if(['t1 == True'],steps,elsesteps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = False    
    engine.run()
    
    assert context.otherTest == False
    
    
def test_if_condition_true_elsesteps_not_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    elsesteps = [ get_expression(["set(f'otherTest',False)"]) ]
    fi = get_if(['t1 == True'],steps,elsesteps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True    
    engine.run()
    
    assert 'otherTest' not in context.keys()
    
def test_if_multi_condition_false_elsesteps_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    elsesteps = [ get_expression(["set(f'otherTest',False)"]) ]
    fi = get_if(['t1 == True','t2 == False'],steps,elsesteps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True
    context.t2 = True
        
    engine.run()
    assert context.otherTest == False
    
def test_if_multi_condition_true_elsesteps_not_run():
    steps = [ get_expression(["set(f'test',True)"]) ]
    elsesteps = [ get_expression(["set(f'otherTest',False)"]) ]
    fi = get_if(['t1 == True','t2 == False'],steps,elsesteps)
    
    pd = get_process_skeleton([fi])
    
    engine, context = init_engine(pd)
    
    context.t1 = True
    context.t2 = False
        
    engine.run()   
    assert 'otherTest' not in context.keys()   
    
def test_for_each_local_variable_multi_step_locals_shared_block():
    steps = [ get_expression(["set(f'test_{locals.i}',True)",
                              "set('locals.i',locals.i + 1)",
                              "list_of_things.append(locals.i)"])]

    fl = get_for_each('test_col','i',steps)
    pd = get_process_skeleton([fl])
    
    engine, context = init_engine(pd)
    
    context.test_col = [ x for x in range(4)]
    
    context.list_of_things = []
    engine.run()
    
    assert context.list_of_things[0] == 1
    
def test_block_same_share_locals():
    blk_exp = [
        "set('locals.mylist',[f'{x}_num' for x in range(3)])"
    ]
    steps = [ 
             get_expression(["locals.mylist.append('xx_1')"]),
             get_expression(["locals.mylist.append('xx_3')"]),
             get_expression(["set('mylist',list(locals.mylist))"])
            ]
    blk = get_block(steps,blk_exp)
    pd = get_process_skeleton([blk])
    
    engine, context = init_engine(pd)
    
    engine.run()

    assert context.mylist[-1] =='xx_3'
    
    
def test_while_contition_true_steps_run():
    pd = get_process_skeleton([
         get_while(['cond1 == True and not cond2'],
              [get_expression(['outlist.append("loop")',
                              'set("cond2",len(outlist) > 2)'])])
    ])
    
    engine, context = init_engine(pd)
    
    context.outlist = []
    context.cond1 = True
    context.cond2 = False
    
    engine.run()
    
    assert len(context.outlist) == 3
    
    
def test_while_contition_true_steps_not_run():
    pd = get_process_skeleton([
         get_while(['cond1 == True and not cond2'],
              [get_expression(['outlist.append("loop")',
                              'set("cond2",len(outlist) > 2)'])])
    ])
    
    engine, context = init_engine(pd)
    
    context.outlist = []
    context.cond1 = True
    context.cond2 = True
    
    engine.run()
    
    assert len(context.outlist) == 0
    
    
def test_try_catch_steps_run_on_except():
    pd = get_process_skeleton([
        get_try([get_expression(["true == true","set_continued()"])],[get_expression(['set_error(locals._)'])])
    ])
    
    engine, context = init_engine(pd)
    
    @context.expression()
    def set_error(context:Context,err):
        context.error = err
    
    @context.expression()
    def set_continued(context:Context):
        context.continued = True
        
    engine.run()
    
    assert type(context.error) is Exception
    assert "continued" not in context.keys()
        
def test_do_while_contition_true_steps_run():
    pd = get_process_skeleton([
         get_do_while(['cond1 == True and not cond2'],
              [get_expression(['outlist.append("loop")',
                              'set("cond2",len(outlist) > 2)'])])
    ])
    
    engine, context = init_engine(pd)
    
    context.outlist = []
    context.cond1 = True
    context.cond2 = False
    
    engine.run()
    
    assert len(context.outlist) == 3
    
def test_do_while_contition_false_steps_run():
    pd = get_process_skeleton([
         get_do_while(['cond1 == True and not cond2'],
              [get_expression(['outlist.append("loop")',
                              'set("cond2",len(outlist) > 2)'])])
    ])
    
    engine, context = init_engine(pd)
    
    context.outlist = []
    context.cond1 = False
    context.cond2 = True
    
    engine.run()
    
    assert len(context.outlist) == 1
    
def test_frame_push_step_returns_step():
    step = get_step(name='step')
    frame = Frame()
    step = frame.push_step(step)
    assert type(step) is Step
    
def test_frame_push_step_current_step():
    step = get_step(name='step')
    frame = Frame()
    step = frame.push_step(step)
    assert step is frame.current_step

def test_frame_push_flow_step_return_flow():
    flow = get_if()
    frame = Frame()
    
    flow = frame.push_flow(flow)
    assert len(frame.step_stack) == 0
    assert type(frame.current_flow) is Flow
    
def test_frame_link_locals_sub_steps():
    step1 = get_step(name="step1")
    step2 = get_step(name="step2")
    step3 = get_step(name="step3")
    step4 = get_step(name="step4")
    step5 = get_step(name="step5")
     
    flow = get_if()

    frame = Frame()
    # step 1,2
   
    step1 =frame.push_step(step1)
    step2 = frame.push_step(step2)
    
    # flow
    flow = frame.push_flow(flow)
    
    # step 3,4,5
    step3 = frame.push_step(step3)
    step4 = frame.push_step(step4)
    step5 = frame.push_step(step5)
    
        
    frame.current_step.locals.thing = True
    
    assert 'thing' not in step1.locals.keys()
    assert 'thing' in flow.locals.keys()
    assert step5.locals is flow.locals
    assert step1.locals is not flow.locals
    
    
    
    
    
    
    