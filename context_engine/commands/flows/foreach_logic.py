from ...decorators import default_var_when_none

def foreach_logic(engine,flow_step):
    if flow_step.is_var_list:
        for x,y in enumerate(engine.context[flow_step.collection]):
            engine.set_local(flow_step.var[0],x)
            engine.set_local(flow_step.var[1],y)
            engine.do_step(flow_step.steps)
    else:
        for x in engine.context[flow_step.collection]:
            engine.set_local(flow_step.var,x)
            engine.do_step(flow_step.steps)