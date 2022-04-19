from ...decorators import default_var_when_none


def block_logic(engine,flow_step):
    engine.do_steps(flow_step.steps)    