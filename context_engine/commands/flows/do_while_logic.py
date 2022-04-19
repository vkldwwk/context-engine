from ...decorators import default_var_when_none

from .while_logic import while_logic



@default_var_when_none
def do_while_logic(engine,flow_step):
    engine.increment_loop_counter(flow_step)
    engine.do_steps(flow_step.steps)
    while_logic(engine,flow_step)