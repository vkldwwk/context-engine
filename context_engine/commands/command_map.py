
from context_engine.decorators import FlowComponent, Expression, Component
import context_engine.commands.components.all as sys_components
import context_engine.commands.expressions.all as sys_expressions
import context_engine.commands.flows.all as sys_flows

command_map = {
    "components": [
    ],
    "expressions": [
        ("Expression","sys_expressions","new_dict_function","new_dict"),
        ("Expression","sys_expressions","new_list_function","new_list"),
        ("Expression","sys_expressions","set_function","set"),
    ],
    "flows": [
        ("FlowComponent","sys_flows","block_logic","block"),
        ("FlowComponent","sys_flows","do_while_logic","do while"),
        ("FlowComponent","sys_flows","foreach_logic","for each"),
        ("FlowComponent","sys_flows","if_logic","if"),
        ("FlowComponent","sys_flows","while_logic","while"),
        ("FlowComponent","sys_flows","try_logic","try"),
    ]
    
}

def map_command(map_key,save_dic,context,engine=None):
    for obj, lib, name,cb in command_map[map_key]:
        comp= []
        exec("comp.append(%s( '%s', %s.%s))" % (obj,cb,lib,name),globals(),locals())
        cmd = comp and comp.pop()
        
        cmd and context and cmd.set_context(context)
        cmd and engine and cmd.set_engine(engine)
        
        save_dic[cb] = cmd
        1 == 1