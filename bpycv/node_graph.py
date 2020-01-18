#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Mon Jan 13 18:39:35 2020
"""

from boxx import *


class activate_node_tree:
    activate_node_tree_stack = []

    def __init__(self, node_tree):
        self.activate_node_tree_stack.append(node_tree)
        self.node_tree = node_tree

    def __enter__(self):
        return self

    def __exit__(self, typee, value, traceback):
        assert self.activate_node_tree_stack.pop() is self.node_tree


def is_node_socket(obj):
    return type(obj).__name__.startswith("NodeSocket")


class Node(object):
    """
    Usage:
        
    >>> with activate_node_tree(material.node_tree):
            Node("ShaderNodeOutputMaterial").Surface = Node("ShaderNodeEmission", Color=color).Emission
    
    >>> with activate_node_tree(material.node_tree):
            Node(
                "ShaderNodeOutputMaterial",
                Surface=Node("ShaderNodeEmission", Color=color).Emission,
            )
    """

    def __init__(self, node, node_tree=None, **kv):
        assert len(
            activate_node_tree.activate_node_tree_stack
        ), "Node init must under `with activate_node_tree(node_tree):`"
        if node_tree is None:
            node_tree = activate_node_tree.activate_node_tree_stack[-1]
        if isinstance(node, str):
            node = node_tree.nodes.new(node)
            node["is_auto"] = True
        self.node = node
        self.node_tree = node_tree
        self.kv = kv
        self.set_input(kv)
        self.begin_to_set_by_attr = True

    def __getattr__(self, key):
        node = object.__getattribute__(self, "node")
        if key in node.outputs:
            return node.outputs[key]
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value, *l):
        if self.__dict__.get("begin_to_set_by_attr"):
            self.set_kv(key, value)
        else:
            object.__setattr__(self, key, value, *l)

    def __getitem__(self, key):
        return self.node.outputs[key]

    def __setitem__(self, key, value):
        self.set_kv(key, value)

    def set_kv(self, k, v):
        if k in self.node.inputs:
            node_input = self.node.inputs[k]
            if is_node_socket(v):
                self.node_tree.links.new(v, node_input)
            else:
                node_input.default_value = v
        else:
            setattr(self.node, k, v)

    def set_input(self, dic=None, **kv):
        if dic is None:
            dic = {}
        kv.update(dic)
        for k, v in kv.items():
            self.set_kv(k, v)


if __name__ == "__main__":
    pass
