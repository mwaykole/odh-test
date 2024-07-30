import sys
from itertools import product
from typing import List, Any, Optional


class Carteplex:
    """Main class for cartesian product test generation."""

    class CarteTestClass:
        """
        Decorator providing cartesian product parameter-like capability
        for unittest class.
        """

        def __init__(self, value: Optional[List[Any]] = None):
            """
            Override to provide data specific to your tests.

            Args:
                value (Optional[List[Any]]): Data automatically provided by the decorator.
                    Defaults to None.
            """
            self.axis_names: List[str] = ["cartesian", "product"]
            self.available_options: List[List[str]] = [["A", "B", "C", "D", "E"], ["one", "two", "three", "four"]]
            self.selections: List[List[str]] = []  # Replace with desired selections
            self.limits: List[List[str] | None] = [None] * len(self.available_options)  # Allow overriding

            if value:
                self.selections = value

        def __call__(self, obj):
            """
            Generates cartesian product test cases.

            Args:
                obj (object): Object automatically passed by the decorator.

            Returns:
                object: Empty object (removes original test class from run)
            """

            # Update selections with available options for 'ALL'
            for i, selection in enumerate(self.selections):
                if selection == "ALL":
                    self.selections[i] = self.available_options[i]

            # Update axis names with non-None limits
            updated_axis_names = [name for i, name in enumerate(self.axis_names) if self.limits[i]]

            # Calculate intersection of selections and limits
            intersect_sets = [
                set(selection) & set(limit) if limit else set(selection)
                for selection, limit in zip(self.selections, self.limits)
            ]

            iterables = list(intersect_sets)

            # Generate test cases
            for case in product(*iterables):
                suffix = "_".join(case)
                class_name = f"{obj.__name__}_{suffix}"

                new_class = type(class_name, (obj,), {})  # Create new class

                # Assign attributes from case to new class
                for i, name in enumerate(updated_axis_names):
                    setattr(new_class, name, case[i])

                # Set module name for the new class
                new_class.__module__ = obj.__module__

                # Add new class to the module
                setattr(sys.modules[obj.__module__], class_name, new_class)

            return obj