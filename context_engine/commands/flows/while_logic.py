from ...decorators import default_var_when_none

@default_var_when_none
def while_logic(engine,flow_step):
    engine.increment_loop_counter(flow_step)
    while engine.evaluate_flow_conditions(flow_step) is True:
        engine.do_steps(flow_step.steps)      
        engine.increment_loop_counter(flow_step)   