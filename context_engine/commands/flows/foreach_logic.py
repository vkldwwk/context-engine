from ...decorators import get_composite_key_value

def foreach_logic(engine,flow_step):
    collection = get_composite_key_value(engine.context,flow_step.collection)
    if flow_step.is_var_list and type(collection) is dict:
        for x,y in collection.items():
            engine.set_local(flow_step.var[0],x)
            engine.set_local(flow_step.var[1],y)
            engine.do_steps(flow_step.steps)
    elif flow_step.is_var_list:
        for x,y in enumerate(collection):
            engine.set_local(flow_step.var[0],x)
            engine.set_local(flow_step.var[1],y)
            engine.do_steps(flow_step.steps)
    else:
        for x in engine.context[flow_step.collection]:
            engine.set_local(flow_step.var,x)
            engine.do_steps(flow_step.steps)