# Context Engine


Simple way to organize processing jobs. generally best when one or more specifications is involved. Processes are designed in a JSON document process broken down into steps and flow steps that work to assemble,transform, score, or create on a shared context. Excellent for mapping/templating/interfacing dynamic repetitive processes.

engine and context are fully customizable to make processing to the point and fully testable. steps and custom expressions are defined in python also support valid python expressions for working with context.

## Intro 
A basic process document 


````jsonc
{
    "process":[
        {
            /*
            Steps reference engine components with the signature in this case of:
                init(context:Context)
            note the name of context can be anything but must map to the name of
            engine component to do processing. while not required each step can 
            only have one step.
            */
            "step":"init",
            
            // args are passed to the step code as context.args you probably shouldn't
            // hard code a value here but you can
            "args":"models/sample.json"
        },
        {
            /*
            The most basic step is just an array of one or more python/context
            expressions. assignments are not allowed but can be achieved with set
            expression.
            */
            "expressions":[
                "set('default_project_dirs',[])",
                "default_project_dirs.append('{project.path}')"
            ]
        },
        {
            /*
            steps can contain a single step and a list of expressions when this
            occurs the expressions are always run first. They can set arguments for
            the step. In this case a string is created on the context a = 'a thing'
            argsAsReff() resolves the name in arguments as a reference.
            */
            "expressions":[
                "set('a','a thing')",
                "argsAsReff()"
            ],
            "step":"other_step",
            "args":"a"
        },
        {
            /*
            flow steps change the processing control dynamically and can stack
            according to application a for each loops over a collection dynamically
            placing the current item in var.Flow steps also support expressions
            however these execute once before flow logic. flow steps also share locals
            of all sub steps.
            */
            "flow": "for each",
            "collection":"default_project_dirs",
            "var": "i",
            /*
            vars are created at locals.varName or context.locals.varName. i is removed
            after the block is complete.behavior uses locals so var = locals.i. locals
            are reset with each step block unless steps are nested in flow. when
            nested in a flow locals persist through the duration of the flow for all
            subsequently nested blocks
            */
            "steps":[
                {
                    /*
                    steps of a flow can contain any number of flow steps or 
                    steps and expressions.expressions are run first and can work on
                    same args as other expressions and the step.

                    a copy of locals is shared with step in a flow block.
                    */
                    "expressions":[
                        "custom_expression(i)"
                    ],
                    "step":"another_step",
                    "args":"i"
                }
            ]
        }
    ]
}

````

## Processing 
is done by the engine on the context. The first thing todo is to setup a process document while also creating engine and context. 

`init_engine(processJson)` expects the follow schema as a process document

````jsonc
{
    "process":[
        // list of steps and flow steps.
    ]
}
````


Then best way is by creating a factory function that calls the factory init_engine(processJson) this creates and returns an instance of Engine, and Context.


````python
# Example factory 
def my_data_engine_factory():
    
    processJson = loadFromSomewhere()
    # returns configured engine and context with basic expressions added to 
    # generic context.
    engine context init_engine(processJson)

    #setup steps each is created with a decorator and passed context in signature
    @engine.component(name='init')
    def initialize_project(context:Context):
        pass

    @engine.component(name='another_step')
    def some_weird_name(context:Context):
        pass
    
    # setup expressions. expressions are just python functions that can be called 
    # in addition to regular python expressions.
    @context.expression(name="log")
    def log_process(name:str,level:str,**kwargs):
        pass


    return (engine, context)

def do_the_thing():
    engine context = my_data_engine_factory()

    engine.run()

    # context does not need to have these properties
    if context.error:
        pass
    else:
        return context.final_product

````

## Steps:

A step is executed on the the context in order of how it appears in the the json config document.
no member is required but each step shall supply either a step or expressions block or both.
args are allowed and passed to context.args for each step. each step has access to local variables on context.locals or just locals.any_var that are available only for the duration of the step block.
expressions are executed first in-order before execution of step if both are present. this is designed to work with loosely typed json so members that are blank are ignored and don't need to be specified in the document. 
        
Steps are added with the syntax:
````python
@engine_instance_name.component(name=optional__name__if_None)
def name_of_step(context:Context):
    pass
````
````json
{
    "expressions":[
        "some_expression()"
    ],    
    "step": "name_of_step",
    "args":"arg value for step"
}
````
        
## Flowsteps:
a flow step must contain a member flow with one of the following flows.
`if, while, do while, for each, try, block`. A copy of flow step locals are available for all sub (step and flow steps). flow steps can also contain a list of expressions these are executed before flow logic and do not have access to flow control variables 

````jsonc
{
    "expressions":[
        "some_expression()"
    ],    
    "flow": "name_of_flow",
    "Steps":[
        //... steps / flow steps ...
        
    ],
    //...
}
````

<div>
&nbsp
</div>

### **If**
require a list of python expressions that must all return true
````json
"conditions":[ 
    "i.type == 'video'"
],
````
* steps are executed when conditions all return true.
    ````json
    {
        "flow": "if",
        "conditions":[
        "i.type == 'video'"
        ],
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
            {
                "expressions":[
                    "argsAsReff()"
                ],
                "step":"evaluate_video_actions",
                "args":"i"

            }
        ]
    }
    ````
* if can optionally contain a block for `"elsesteps":[]` as block to execute when conditions fail.
    ````json
    {
        "flow": "if",
        "conditions":[
        "i.type == 'video'"
        ],
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
        ],
        "elsesteps":[
            {
                "expressions":[
                    "do_something_else"
                ]
            }
        ]
    }
    ````
<div>
&nbsp
</div>

### **While**
require a list of python expressions that must all return true. Supports adding a variable for loop counter. if none specified locals._ is used
````json
"conditions":[ 
    "i.type == 'video'"
],
````
* steps are executed while conditions all return true.
    ````json
    {
        "flow": "while",
        "conditions":[
        "i.type == 'video'"
        ],
        "var": "loop_counter",
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
            {
                "expressions":[
                    "argsAsReff()"
                ],
                "step":"evaluate_video_actions",
                "args":"i"

            }
        ]
    }
    ````
<div>
&nbsp
</div>

### **Do while**
require a list of python expressions that must all return true. Supports adding a variable for loop counter. if none specified locals._ is used
````json
"conditions":[ 
    "i.type == 'video'"
],
````
* executes steps prior to evaluating conditions then while conditions all return true.
    ````json
    {
        "flow": "do while",
        "conditions":[
        "i.type == 'video'"
        ],
        "var": "loop_counter",
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
            {
                "expressions":[
                    "argsAsReff()"
                ],
                "step":"evaluate_video_actions",
                "args":"i"

            }
        ]
    }
    ````
<div>
&nbsp
</div>

### **Try**
* steps are executed when until exception is raised. 
    ````json
    {
        "flow": "try",
        "var":"exception_name",
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
            {
                "expressions":[
                    "argsAsReff()"
                ],
                "step":"evaluate_video_actions",
                "args":"i"

            }
        ]
    }
    ````
* Try can optionally contain a block for `"catchsteps":[]` as block to execute after exception and/or var to store the exception. 
The raised exception is stored in locals._ when var is omitted
    ````jsonc
    {
        "flow": "try",
        "var":"exception_name",
        "steps":[
            {
                "expressions":[
                    "create_video(i.name,i.path)"
                ]
            },
        ],
        "catchsteps":[
            {
                "expressions":[
                    "cleanupThing(locals.exception_name)"
                ]
            }
        ]
    }
    ````
<div>
&nbsp
</div>

### **For each**
requires the name of an iterable collection somewhere on the context and a variable name to store current item. the variable is created by the block at `locals.[variableName]` or `context.locals.[variableName]` if the collection is enumerable add a list of variable names.

````json
    "collection":"default_project_dirs",
    "var": "i",
````
* steps are executed while conditions all return true.
    ````json
    {
        "flow": "for each",
        "collection":"default_project_dirs",
        "var": ["k","v"],
        "steps":[
            {
                "expressions":[
                    "argsAsReff()"
                ],
                "step":"create_dir_structure",
                "args":"i"
            }
        ]
    }
    ````

### **Block**
simple way to group related activities and share locals requires an array of steps also supports expressions.

````json
    "steps":[],
````
* steps are executed while conditions all return true.
    ````jsonc
    {
        "flow": "block",
        "steps":[
            {
                "expressions":[
                    "set('locals.thing','otherThing')"
                ],

            },
            {
                "expressions":[
                    // Locals.thing still has otherThing
                    "set('test',locals.thing)"
                ],

            }

        ]
    },
    {
        "expressions":[
            // Error Locals.thing gone.
            "set('test',locals.thing)"
        ],

    }
    ```` 



## Steps and Expressions
Each named step executes a configured code piece for that step. Steps are passed a copy of the context.

Expressions can be run in a step `context.expressionName(signature)` 

***Note context is injected so no need to specify context in expression signature. when calling from either python through `context.expressionName(signature)` or `expressionName(signature)` but a variable representing context must be the first argument to the expression definition in python***


````python
# Start by creating a new context engine context

engine,context = engine_builder() 

# context here is basically a workspace where jobs can be worked on.


 # The context is based on a dictionary that allows both self.property and self['prop'] access and assignment
 # setup area for processing

context.dbc = sqlite3.connect(db)

context.list_of_things = []

# this expression will be called as name_other(name,other) context is managed internally
@context.expression(name='name_other'):
def fun_with_names(context,name:str,other:str)
    context.list_of_things.append(f'{name}_{other}')

#Defining a engine component if the name is omitted the function name is used. engine components are not available
# as expressions but accept args that can be any type.
@engine.component(name="init")
def init(context):
    pass

````