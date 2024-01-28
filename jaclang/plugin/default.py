"""Jac Language Features."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional, Type, Union
import unittest as ut
from jaclang import jac_import as __jac_import__

from jaclang.plugin.spec import (
    ArchBound,
    Architype,
    DSFunc,
    EdgeAnchor,
    EdgeArchitype,
    EdgeDir,
    GenericEdge,
    NodeArchitype,
    T,
    WalkerArchitype,
    root,
)


import pluggy

hookimpl = pluggy.HookimplMarker("jac")
tc = ut.TestCase()
ts = ut.TestSuite()


class JacFeatureDefaults:
    """Jac Feature."""

    @staticmethod
    @hookimpl
    def make_architype(
        arch_type: str, on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a new architype."""

        def decorator(cls: Type[ArchBound]) -> Type[ArchBound]:
            """Decorate class."""
            cls = dataclass(eq=False)(cls)
            for i in on_entry + on_exit:
                i.resolve(cls)

            match arch_type:
                case "obj":
                    arch_cls = Architype
                case "node":
                    arch_cls = NodeArchitype
                case "edge":
                    arch_cls = EdgeArchitype
                case "walker":
                    arch_cls = WalkerArchitype
                case _:
                    raise TypeError("Invalid archetype type")
            if not issubclass(cls, arch_cls):
                cls = type(cls.__name__, (cls, arch_cls), {})
            cls._jac_entry_funcs_ = on_entry
            cls._jac_exit_funcs_ = on_exit
            inner_init = cls.__init__

            @wraps(inner_init)
            def new_init(self: ArchBound, *args: object, **kwargs: object) -> None:
                inner_init(self, *args, **kwargs)
                arch_cls.__init__(self)

            cls.__init__ = new_init
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def create_test(test_fun: Callable) -> Callable:
        """Create a new test."""

        def test_deco() -> None:
            print("Inside test_deco")

            class JacCheck:
                def __getattr__(self, name: str) -> Union[bool, Any]:
                    return getattr(tc, "assert" + name)

            check = JacCheck()
            test_fun(check)
            ts.addTest(ut.FunctionTestCase(test_fun.__name__))

        return test_deco

    @staticmethod
    @hookimpl
    def run_test(filename: str) -> None:
        """Run the test suite in the specified .jac file.

        :param filename: The path to the .jac file.
        """
        if filename.endswith(".jac"):
            base, mod_name = os.path.split(filename)
            base = base if base else "./"
            mod_name = mod_name[:-4]
            mod = __jac_import__(target=mod_name, base_path=base)
            # print(mod.attr)
            if hasattr(mod, "ts"):
                ut.TextTestRunner().run(ts)  # noqa: B009
            else:
                print("No tests found.")
        else:
            print("Not a .jac file.")

    @staticmethod
    @hookimpl
    def elvis(op1: Optional[T], op2: T) -> T:
        """Jac's elvis operator feature."""
        return ret if (ret := op1) is not None else op2

    @staticmethod
    @hookimpl
    def spawn_call(op1: Architype, op2: Architype) -> Architype:
        """Jac's spawn operator feature."""
        return op1._jac_.spawn_call(op2)

    @staticmethod
    @hookimpl
    def report(expr: Any) -> Any:  # noqa: ANN401
        """Jac's report stmt feature."""

    @staticmethod
    @hookimpl
    def ignore(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's ignore stmt feature."""
        if isinstance(walker, WalkerArchitype):
            return walker._jac_.ignore_node(expr)
        else:
            raise TypeError("Invalid walker object")

    @staticmethod
    @hookimpl
    def visit_node(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's visit stmt feature."""
        if isinstance(walker, WalkerArchitype):
            return walker._jac_.visit_node(expr)
        else:
            raise TypeError("Invalid walker object")

    @staticmethod
    @hookimpl
    def disengage(walker: WalkerArchitype) -> bool:  # noqa: ANN401
        """Jac's disengage stmt feature."""
        walker._jac_.disengage_now()
        return True

    @staticmethod
    @hookimpl
    def edge_ref(
        node_obj: NodeArchitype,
        dir: EdgeDir,
        filter_type: Optional[type],
    ) -> list[NodeArchitype]:
        """Jac's apply_dir stmt feature."""
        if isinstance(node_obj, NodeArchitype):
            return node_obj._jac_.edges_to_nodes(dir, filter_type)
        else:
            raise TypeError("Invalid node object")

    @staticmethod
    @hookimpl
    def connect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        edge_spec: EdgeArchitype,
    ) -> NodeArchitype | list[NodeArchitype]:
        """Jac's connect operator feature.

        Note: connect needs to call assign compr with tuple in op
        """
        if isinstance(left, list):
            if isinstance(right, list):
                for i in left:
                    for j in right:
                        i._jac_.connect_node(j, edge_spec)
            else:
                for i in left:
                    i._jac_.connect_node(right, edge_spec)
        else:
            if isinstance(right, list):
                for i in right:
                    left._jac_.connect_node(i, edge_spec)
            else:
                left._jac_.connect_node(right, edge_spec)
        return left

    @staticmethod
    @hookimpl
    def disconnect(op1: Optional[T], op2: T, op: Any) -> T:  # noqa: ANN401
        """Jac's connect operator feature."""
        return ret if (ret := op1) is not None else op2

    @staticmethod
    @hookimpl
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]:
        """Jac's assign comprehension feature."""
        for obj in target:
            attrs, values = attr_val
            for attr, value in zip(attrs, values):
                setattr(obj, attr, value)
        return target

    @staticmethod
    @hookimpl
    def get_root() -> Architype:
        """Jac's assign comprehension feature."""
        return root

    @staticmethod
    @hookimpl
    def build_edge(
        edge_dir: EdgeDir,
        conn_type: Optional[Type[Architype]],
        conn_assign: Optional[tuple],
    ) -> Architype:
        """Jac's root getter."""
        conn_type = conn_type if conn_type else GenericEdge
        edge = conn_type()
        if isinstance(edge._jac_, EdgeAnchor):
            edge._jac_.dir = edge_dir
        else:
            raise TypeError("Invalid edge object")
        return edge
