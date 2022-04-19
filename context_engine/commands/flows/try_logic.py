from ...decorators import default_var_when_none

@default_var_when_none
def try_logic(engine,flow_step):
    try:
        engine.do_steps(flow_step.steps)
    except Exception as x:
        engine.context.locals[flow_step.var] = Exception(x)
            
        if flow_step.catchsteps is not None:
            engine.do_steps(flow_step.catchsteps)
            
        engine.context.locals.pop(flow_step.var)