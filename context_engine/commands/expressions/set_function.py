def set_function(context,key:str,value):
    def walkKey(base_dic:dict,key_parts:str,value):
        next_keys = key_parts.split(".",1)
        releng = len(next_keys)
        if releng == 2 :
            walkKey(base_dic[next_keys[0]],next_keys[1],value)
        else:
            base_dic[next_keys[0]] = value
                
    if '.' in key:
        walkKey(context,key,value)
    else:
        context[key] = value      