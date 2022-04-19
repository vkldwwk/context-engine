from ...decorators import default_var_when_none

def if_logic(engine,flow_step):
    # engine.evaluate_flow_conditions(flow_step) and engine.do_steps(flow_step.steps) or engine.do_steps(flow_step.elsesteps)
    if engine.evaluate_flow_conditions(flow_step) is True:
        engine.do_steps(flow_step.steps)
    elif flow_step.elsesteps is not None:
        engine.do_steps(flow_step.elsesteps)