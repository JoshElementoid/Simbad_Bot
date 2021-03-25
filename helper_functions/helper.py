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

def id_from_message (string):
    id_ = string.split("<")[1].split(">")[0]
    id_ = parse_into_id(id_)
    
    return int(id_)
    


if __name__ == "__main__":
    
    m = "$shop give <!12345> 55"
    
    id_from_message(m)
