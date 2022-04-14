from re import X
from ctx import Ctx
import typing as t


F = t.TypeVar("F", bound=t.Callable[..., t.Any])

class Command:
    """Callable base class for engine components and context expressions
    """
    def __init__(
        self,
        name: t.Optional[str],
        command,
    ) -> None:
        self.name = name
        self.command:F = command
        self.context = None
               
    def set_context(self,context):
        self.context = context               
    
    def __call__(self,*args, **kwargs):
        self.command(self.context)

        
class Component(Command):
    def __init__(self, name: t.Optional[str], command) -> None:
        super().__init__(name, command)

        
class Expression(Command):
    def __init__(self, name: t.Optional[str], command) -> None:
        super().__init__(name, command)
    
    def __call__(self,*args, **kwargs):
        return self.command(self.context,*args,**kwargs)
    
    
class Frame():
    def __init__(self) -> None:
        self.var = Ctx()
        self.step_props = [('step',None),('expressions',None),('args',None),('error',None),('flow',None),("locals",Ctx())]
        self.flow_props = [('flow',None),('expressions',None),('conditions',None),('args',None),('error',None),("elsesteps",None),("collection",None),("var",None),("fail_on_error",True),("catchsteps",None),("locals",Ctx())]
        self.step_stack = []
        self.flow_stack = []
    
    def push_step(self,step):
        ps = self.__get_pretty_step(step)
        
        # If step is in a flow block link the locals of steps in that block
        if len(self.flow_stack) > 0:
            ps.locals = self.current_step.locals
            
        self.step_stack.append(ps)
        return ps
        
    def push_flow(self,flow):
        ps = self.__get_pretty_flow(flow)
        
        # If flow step is in a flow block link the locals.
        if len(self.flow_stack) > 0:
            ps.locals = self.current_step.locals
        
        self.flow_stack.append(ps)
        return ps
        
    def pop_step(self):
        return self.step_stack.pop()
        
    def pop_flow(self):
        return self.flow_stack.pop()
    
    def __get_current_step(self):
        return self.step_stack[-1]
    
    def __get_current_flow(self):
        return self.flow_stack[-1]
    
    def __get_pretty_flow(self,step):
        return self.__make_pretty(step,self.flow_props)
    
    def __get_pretty_step(self,step):
        return self.__make_pretty(step,self.step_props)
    
    def __make_pretty(self,step:t.Dict,default_kvp_list):
        val=Ctx({k:v for k,v in default_kvp_list})
        for k,v in step.items():
            val[k] = v
            
        return val
        
    current_step = property(__get_current_step)
    current_flow = property(__get_current_flow)
    
        
class Context(Ctx):
    """Context for Engine processing Context. 
    It's best to use builder method to construct engine and context at same time.
       
       Context's base class is Ctx that is a dictionary that allows
       both index and dot notation:
                  context.blah = 9
            is the same as
                  context['blah'] = 9
        
        to keep this general basic expressions for context processing are attached by factory method init_engine
        for more specific uses cases new expressions can be attached with decorator @context_instance.expression
        expressions are executed against the context and have access to all context values.
        assignment not allowed so a = 3 no. use set(a,3) instead
        
        @context.expression
        def do_some_thing(context,arg1,arg2):
            add code that does something
            
        this creates a new expression do_something(arg1,arg2)

    Args:
        Ctx (_type_): _description_
    """
    def __init__(self,frame:"Frame") -> None:
        """_summary_
            Do not use. Use factory method.
        Args:
            frame (Frame): stack frame for engine context.
        """
        self.cur_frame ={}
        self.frame = frame
        super().__init__()
        
    def __get_current_step(self):
        return self.frame.current_step
    
    def __get_current_flow(self):
        return self.frame.current_flow
    
    def __get_current_args(self):
        return self.frame.current_step.args
    
    def __get_current_locals(self):
        return self.frame.current_step.locals
    
    current_step = property(__get_current_step)
    current_flow = property(__get_current_flow)
    args = property(__get_current_args)
    locals= property(__get_current_locals)
    
    def eval_expression(self,expression):
        """Excecutes an expression in the context of this context/engine.

        Args:
            expression (str): python expression to evaluate

        Returns:
            any : result of evaluation
        """
        return eval(expression,globals(),self)


    def expression(
        self,*args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], Command]:
        """Adds expression to to context. 
           
           expects a function with the first param being type Context
            def get_full_name(context:Context,first,middle,last):
                pass
            results in a context function that can be called on the current context
            by name directly as an expression with the signature get_full_name(first,middle,last)
            or called in step or other python code context.get_full_name(first,middle,last)

        """
        from .decorators import expression

        def decorator(f: t.Callable[..., t.Any]) -> Command:
            cmd = expression(*args, **kwargs)(f)
            self[cmd.name] = cmd
            cmd.set_context(self)
            return cmd
        return decorator
     

class Engine():
    """ Engine processing class for context engine. 
    It's best to use builder method to construct engine and context at same time.
    """
    def __init__(
        self,
        context: "Context",
        frame: "Frame"
        ) -> None:
        self.steps = []
        self.context = context
        self.frame = frame
        self.has_started = False
        self.is_error = False
        self.halt = False
        self.step_functions: t.Dict[str,Command]= dict()
        self.run_once = False
        self.repeat_run = False
        pass
    
    def __is_finished__(self):
        return len(self.frame.step_stack) == 0 and self.has_started
    
    is_finished = property(__is_finished__)
    
    def run(self):
        # while not( self.is_finished and self.is_error and self.halt) and len(self.steps) > 0:
        self.has_started = True
        self.do_step(self.steps)
        
    def do_step(self,list_steps:t.List):
        for step in list_steps:
            
            step = self.frame.push_step(step)
            
            # Is flow step?
            if step.flow is not None:
                self.do_flow(step)
            else:
                # Do we have an expression?
                if step.expressions is not None:
                    self.__eval_step_expressions(step.expressions)
                # if step present run engine component code.
                if step.step is not None:
                    # test for missing step   
                    self.step_functions[step.step]()
                
            self.frame.pop_step()
            
    def __eval_step_expressions(self,expression_list):
        for expression in expression_list:
            self.context.eval_expression(expression)

    def do_flow(self,flow_step):
        """Base processing for flow step blocks.

        Args:
            flow_step (_type_): _description_
        """
        flow_step = self.frame.push_flow(flow_step)

        # Flow step expressions are executed once before flow logic so no
        # access to loop variables useful for setting up locals for processing.
        if flow_step.expressions is not None:
            self.__eval_step_expressions(flow_step.expressions)
               
        if flow_step.flow == 'while':
            self._flow_while(flow_step)        
        elif flow_step.flow == 'if':
            self._flow_if(flow_step)
        elif flow_step.flow == 'do while':
            self._flow_while_do(flow_step)
        elif flow_step.flow == 'for each':
            self._flow_for_each(flow_step)
        elif flow_step.flow == 'try':
            self.__flow_try(flow_step)
        elif flow_step.flow == 'block':
            self.__flow_block(flow_step)
               
        self.frame.pop_flow()
                
    def __flow_block(self,flow_step):
        self.do_step(flow_step.steps)
        
    
    def __flow_try(self,flow_step):
        try:
            self.do_step(flow_step.steps)
        except Exception as x:
            if flow_step.var is None:
                flow_step.var = "_"
                self.context.locals[flow_step.var] = Exception(x)
                
            if flow_step.catchsteps is not None:
                self.do_step(flow_step.catchsteps)

            
    def _flow_while_do(self,flow_step):
        self.do_step(flow_step.steps)
        self._flow_while(flow_step)
                
    def _flow_while(self,flow_step):
        while self.evaluate_flow_conditions(flow_step) is True:
            self.do_step(flow_step.steps)      

    def _flow_if(self,flow_step):
        if self.evaluate_flow_conditions(flow_step) is True:
            self.do_step(flow_step.steps)
        elif flow_step.elsesteps is not None:
            self.do_step(flow_step.elsesteps)

    def evaluate_flow_conditions(self,flow_step) -> bool:
        reg = []
        for condition in flow_step.conditions:
            reg.append(self.context.eval_expression(condition))
            
        return all(reg)
    
    def _flow_for_each(self,flow_step):
        for x in self.context[flow_step.collection]:
            if type(x) is dict:
                self.context.locals[flow_step.var] = Ctx(x)
            else:
                self.context.locals[flow_step.var] = x
                
            self.do_step(flow_step.steps)
    
        self.context.locals.pop(flow_step.var)
        
    def set_current_step(self,step):
        self.context.current_step = step
    
       
    def component(
        self,*args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], Command]:
        """Adds component to engine 
           
           step_name is the name that is refrenced in json
        """
        from .decorators import component

        def decorator(f: t.Callable[..., t.Any]) -> Command:
            cmd = component(*args, **kwargs)(f)
            self.step_functions[cmd.name] = cmd
            cmd.set_context(self.context)
            return cmd
        return decorator
        

    
def init_engine(processJSON):
    """Builds Engine and Context objects.
        Attaches basic context expressions. Add more specific engine components and expressions
        to objects returned from this function.
        
        Steps:
            A step is executed on the the context in order of how it aprear in the the json config document.
            no member is required but eact step shal supply either a step or expressions block or both.
            args are allowed and passed to context.args for each step.
            expressions are executed first before execution of step if both are present.
            
            Steps are added with the syntax:
                @engine_instance_name.component(name=optional__name__if_None)
        {
            "step": "name of engine component"
            "expressions":[
                "list of python/context expressions to execute in order",
                "next expression"
            ]
            "args":"arg value for step"
        }
        
        Flowsteps:
            a flow step must contain a member flow with one of the following flows.
                "flow": { "if", "while", "do while", "foreach" }
                
                if, while, do while, require a list of python expressions that must all return true
                "conditions":[ 
                    "i.type == 'video'"
                ],
                
                if supports an additional
                "elsesteps":[
                    a list of steps when false
                ]
                
                for each requires the name of a collection on the context or a python,context expression that returns one
                var name of var on context to fetch next item into, careful this can colide and is removed from the context
                on exit of block. but is accessable to all sub steps and expressions until then.
                
                "collection":"input",
                "var": "i",
                
                flow steps do not support expressions like steps
                
                all flow steps require a 
                "steps":[
                    array of steps and/or flow steps to execute.
                ]
            }
        
        Context Expressions
            argsAsReff()   - arguments supplied to the the following step are a reffrence to a variable.
            newList(name)  - create a new list with name
            newDict(name)  - creates a Ctx dictionary accepts dict_name['thing'] or dict_name.thing
            set(key,value) - expressions do not support assignment this allows creation and setting of context values
                             supports list/dict comprehention as values or most valid python.
                             
        Additional context expressions can be added to the returned context with the syntax: 
            @context_instance_name.expression(name=__name__ when None)
    
    Args:
            processJSON (any): json object representing engine. must cantain a 
            "process": [ list of steps/flow steps]
            
    example:
    {
        "process":[
            {
                "step":"init",
                "args":"models/sample.json"
            },
            {
                "expressions":[
                    "set('default_project_dirs',[])",
                    "default_project_dirs.append('{project.path}')"
                ]
            },
            {
                "flow": "for each",
                "collection":"default_project_dirs",
                "var": "i",
                "steps":[
                    {
                        "expressions":[
                            "argsAsReff()"
                        ],
                        "step":"create_dir_structure",
                        "args":"i"
                    }
                ]
            },
            {
                "expressions":[
                    "set('videos', Ctx())"
                ]
            }
        ]
    }
    the sample above requires 2 engine components that resolve to init(context:Context) and create_dir_structure(context:Context)
    Returns:
    (Engine,Context)    : New Engine and Context ready for initialization
    """
    # create and link frame and context
    frame = Frame()
    context = Context(frame)
        
    # adding top level expressions to context. Add more specif ones when you configure context    
    @context.expression(name='argsAsReff')
    def __arg_var(theContext):
        theContext.current_step.args = theContext[theContext.current_step.args]
    
    @context.expression(name='newList')
    def __createArray(theContext,name):
        theContext[name] = []
    
    @context.expression(name='newDict')
    def __createDict(theContext,key):
        theContext[key] = Ctx()
    
    @context.expression(name='set')
    def __set_function(theContext,key:str,value):
        def walkKey(base_dic:dict,key_parts:str,value):
            next_keys = key_parts.split(".",1)
            releng = len(next_keys)
            if releng == 2 :
                walkKey(base_dic[next_keys[0]],next_keys[1],value)
            else:
                base_dic[next_keys[0]] = value
                  
        if '.' in key:
            walkKey(theContext,key,value)
        else:
            theContext[key] = value      
    
    # Create new engine from context and frame
    engine = Engine(context,frame)
    
    # set engine steps to process section of json file 
    engine.steps = processJSON["process"]
         
    return (engine,context)