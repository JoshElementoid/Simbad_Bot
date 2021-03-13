# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:48:26 2021

@author: Josh
"""


def dict_list (dictionary):
    names = list(dictionary.keys())
    dict_info = ", ".join(names)
    
    return dict_info


def parse_into_id (string): 
    # Probably should've used regex for this
    replace_dict = {
        "<": "",
        ">": "",
        "!": "",
        "@": ""
        }
    
    parsed = string.translate(str.maketrans(replace_dict))
    
    return parsed

def r (*args):
    
    wanted = args[1:]
    for x in wanted:
        print(x)
    
    return 




if __name__ == "__main__":
    
    cur_roles = [1,2,3,4,5,6]
    req_roles = [1,2,3,4,5,6,7,8,9]
    
    to_add = [x for x in req_roles if x not in cur_roles]
    to_remove = [x for x in req_roles if x in cur_roles]
    
