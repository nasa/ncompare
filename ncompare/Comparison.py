from collections.abc import Iterator

import h5py
import netCDF4
import numpy as np
from colorama import Fore

from ncompare.getters import (
    get_and_check_variable_attributes,
    get_and_check_variable_scale_factor,
    get_root_dims,
    get_root_groups,
    get_subgroups,
    get_variables,
)
from ncompare.printing import Outputter
from ncompare.sequence_operations import common_elements, count_diffs
from ncompare.utility_types import (
    FileToCompare,
    GroupPair,
    SummaryDifferenceKeys,
    SummaryDifferencesDict,
    VarProperties,
)


class Comparison:
    def __init__(
        self,
        file1: FileToCompare,
        file2: FileToCompare,
        out: Outputter,
        show_chunks: bool,
        show_attributes: bool,
    ):
        assert file1.type == file2.type
        self.file1 = file1
        self.file2 = file2
        self.file_types = file1.type
        self.out: Outputter = out
        self.show_chunks: bool = show_chunks
        self.show_attributes: bool = show_attributes

        blank_difference_dict: SummaryDifferencesDict = {
            "shared": 0,
            "left": 0,
            "right": 0,
            "both": 0,
            "difference_types": set(),
        }
        self.num_group_diffs: SummaryDifferencesDict = blank_difference_dict.copy()
        self.num_var_diffs: SummaryDifferencesDict = blank_difference_dict.copy()
        self.num_attribute_diffs: SummaryDifferencesDict = blank_difference_dict.copy()

        self.open_file1 = None
        self.open_file2 = None

    def run_through_comparisons(self) -> int:
        """Execute a series of comparisons between two netCDF or HDF files.

        Returns
        -------
        int
            total number of differences found (across variables, groups, and attributes)
        """
        self._print_root_dimensions()
        self._print_root_groups()

        # Run through all the rest of the groups and variables, tallying differences along the way.
        self.out.print(Fore.LIGHTBLUE_EX + "\nAll variables:", add_to_history=True)
        self.out.side_by_side(" ", "File A", "File B", force_display_even_if_same=True)

        self._traverse_hierarchy()
        self._print_summary()

        # Return the total number of differences; zero indicates no differences were found.
        total_diff_count = sum(
            [
                x["left"] + x["right"]
                for x in [self.num_var_diffs, self.num_group_diffs, self.num_attribute_diffs]
            ]
        )

        return total_diff_count

    def _traverse_hierarchy(self):
        self.out.side_by_side(
            "All Variables", " ", " ", dash_line=False, force_display_even_if_same=True
        )
        self.out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)

        # Determine how the files will be opened.
        file_opener = netCDF4.Dataset if self.file_types == "netcdf" else h5py.File

        # Open and go through files.
        with (
            file_opener(self.file1.path, mode="r") as ds_a,
            file_opener(self.file2.path, mode="r") as ds_b,
        ):
            self.open_file1 = ds_a
            self.open_file2 = ds_b

            # Start with the Root Group, printing all the variables from it.
            group_counter = 0
            self._print_group_details_side_by_side(
                ds_a,
                "/",
                ds_b,
                "/",
                group_counter,
            )
            group_counter += 1

            for group_pair in self._dataset_pair_iterator(
                "",
                ds_a,
                get_subgroups(ds_a, self.file_types),
                "",
                ds_b,
                get_subgroups(ds_b, self.file_types),
            ):
                if group_pair.group_a_name == "":
                    self.num_group_diffs["right"] += 1
                elif group_pair.group_b_name == "":
                    self.num_group_diffs["left"] += 1
                else:
                    self.num_group_diffs["shared"] += 1

                self._print_group_details_side_by_side(
                    group_pair.group_a,
                    group_pair.group_a_name,
                    group_pair.group_b,
                    group_pair.group_b_name,
                    group_counter,
                )
                group_counter += 1

    def _print_group_details_side_by_side(
        self,
        group_a: netCDF4.Dataset | netCDF4.Group | h5py.Group,
        group_a_name: str,
        group_b: netCDF4.Dataset | netCDF4.Group | h5py.Group,
        group_b_name: str,
        group_counter: int,
    ) -> None:
        """Align and display group details side by side."""
        self.out.side_by_side(
            " ", " ", " ", dash_line=False, highlight_diff=False, force_display_even_if_same=True
        )
        self.out.side_by_side(
            f"GROUP #{group_counter:02}",
            group_a_name.strip(),
            group_b_name.strip(),
            dash_line=True,
            highlight_diff=False,
            force_display_even_if_same=True,
        )

        # Count the number of variables in this group as long as this group exists.
        vars_a_sorted: list | str = ""
        vars_b_sorted: list | str = ""
        if group_a:
            vars_a_sorted = get_variables(group_a, self.file_types)
        if group_b:
            vars_b_sorted = get_variables(group_b, self.file_types)
        self.out.side_by_side(
            "num variables in group:",
            len(vars_a_sorted),
            len(vars_b_sorted),
            highlight_diff=True,
            force_display_even_if_same=True,
        )
        self.out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)

        # Count differences between the lists of variables in this group.
        left, right, shared = count_diffs(vars_a_sorted, vars_b_sorted)
        self.num_var_diffs["left"] += left
        self.num_var_diffs["right"] += right
        self.num_var_diffs["shared"] += shared

        # Go through each variable in the current group.
        for variable_pair in common_elements(vars_a_sorted, vars_b_sorted):
            # Get and print the properties of each variable
            self._print_var_properties_side_by_side(
                self._create_var_properties(
                    group_a, variable_pair[1], original_dataset=self.open_file1
                ),
                self._create_var_properties(
                    group_b, variable_pair[2], original_dataset=self.open_file1
                ),
            )

    def _print_var_properties_side_by_side(
        self,
        v_a: VarProperties,
        v_b: VarProperties,
    ) -> None:
        """Align and display variable properties side by side."""
        # Gather all variable property pairs first, before printing,
        # so we can decide whether to highlight the variable header.
        pairs_to_check_and_show = [
            (v_a.dtype, v_b.dtype),
            (v_a.dimensions, v_b.dimensions),
            (v_a.shape, v_b.shape),
        ]
        if self.show_chunks:
            pairs_to_check_and_show.append((v_a.chunking, v_b.chunking))
        if self.show_attributes:
            for attr_a_key, attr_a, attr_b_key, attr_b in get_and_check_variable_attributes(
                v_a, v_b
            ):
                # Check whether attr_a_key is empty,
                # because it might be if the variable doesn't exist in File A.
                pairs_to_check_and_show.append((attr_a, attr_b))
        # Scale Factor
        scale_factor_pair = get_and_check_variable_scale_factor(v_a, v_b)
        if scale_factor_pair:
            pairs_to_check_and_show.append((scale_factor_pair[0], scale_factor_pair[1]))

        there_is_a_difference = False
        for pair in pairs_to_check_and_show:
            if pair[0] != pair[1]:
                there_is_a_difference = True
                break

        # If all attributes are the same, and keep-only-diffs is set -> DON'T print
        # If all attributes are the same, and keep-only-diffs is NOT set -> print
        # If some attributes are different -> print no matter else
        if there_is_a_difference or (not self.out.keep_only_diffs):
            self.out.side_by_side(
                "-----VARIABLE-----:",
                v_a.varname[:47],
                v_b.varname[:47],
                highlight_diff=False,
                force_display_even_if_same=True,
            )

        # Go through each attribute, show differences, and add differences to running tally.
        def _var_attribute_side_by_side(attribute_name, attribute_a, attribute_b):
            diff_condition: SummaryDifferenceKeys = self.out.side_by_side(
                f"{attribute_name}:", attribute_a, attribute_b, highlight_diff=True
            )
            self.num_attribute_diffs[diff_condition] += 1
            if diff_condition in ("left", "right", "both"):
                self.num_attribute_diffs["difference_types"].add(attribute_name)

        _var_attribute_side_by_side("dtype", v_a.dtype, v_b.dtype)
        _var_attribute_side_by_side("dimensions", v_a.dimensions, v_b.dimensions)
        _var_attribute_side_by_side("shape", v_a.shape, v_b.shape)
        # Chunking
        if self.show_chunks:
            _var_attribute_side_by_side("chunksize", v_a.chunking, v_b.chunking)
        # Scale Factor
        scale_factor_pair = get_and_check_variable_scale_factor(v_a, v_b)
        if scale_factor_pair:
            _var_attribute_side_by_side("scale_factor", scale_factor_pair[0], scale_factor_pair[1])
        # Other attributes
        if self.show_attributes:
            for attr_a_key, attr_a, attr_b_key, attr_b in get_and_check_variable_attributes(
                v_a, v_b
            ):
                # Check whether attr_a_key is empty,
                # because it might be if the variable doesn't exist in File A.
                attribute_key = attr_a_key if attr_a_key else attr_b_key
                _var_attribute_side_by_side(attribute_key, attr_a, attr_b)

    def _print_root_dimensions(self):
        # Show the dimensions of each file and evaluate differences.
        self.out.print(Fore.LIGHTBLUE_EX + "\nRoot-level Dimensions:", add_to_history=True)
        list_a = get_root_dims(self.file1)
        list_b = get_root_dims(self.file2)
        _, _, _ = self.out.lists_diff(list_a, list_b)

    def _print_root_groups(self):
        # Show the groups in each NetCDF file and evaluate differences.
        self.out.print(Fore.LIGHTBLUE_EX + "\nRoot-level Groups:", add_to_history=True)
        list_a = get_root_groups(self.file1)
        list_b = get_root_groups(self.file2)
        _, _, _ = self.out.lists_diff(list_a, list_b)

    def _print_summary(self):
        """Print summary counts of similarities and differences."""
        self.out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)
        self.out.side_by_side("SUMMARY", "-", "-", dash_line=True, force_display_even_if_same=True)

        self.__print_summary_count_comparison_side_by_side("variable", self.num_var_diffs)
        self.__print_summary_count_comparison_side_by_side("group", self.num_group_diffs)
        self.__print_summary_count_comparison_side_by_side("attribute", self.num_attribute_diffs)

        if self.num_attribute_diffs["difference_types"]:
            self.out.print(
                Fore.LIGHTBLUE_EX + "\nDifferences were found in these attributes:",
                add_to_history=True,
            )
            self.out.print(
                Fore.LIGHTBLUE_EX + f"\n{sorted(self.num_attribute_diffs['difference_types'])}",
                add_to_history=True,
            )

    def __print_summary_count_comparison_side_by_side(
        self,
        item_type: str,
        diff_dictionary: SummaryDifferencesDict,
    ) -> None:
        # Tally up instances where there were non-empty entries on both left and right sides.
        diff_dictionary["left"] += diff_dictionary["both"]
        diff_dictionary["right"] += diff_dictionary["both"]

        self.out.side_by_side(
            f"Total # of shared {item_type}s:",
            str(diff_dictionary["shared"]),
            str(diff_dictionary["shared"]),
            force_display_even_if_same=True,
        )

        self.out.side_by_side(
            f"Total # of non-shared {item_type}s:",
            str(diff_dictionary["left"]),
            str(diff_dictionary["right"]),
            force_display_even_if_same=True,
        )

    def _dataset_pair_iterator(
        self,
        node_a_name: str,
        node_a: netCDF4.Dataset | netCDF4.Group | h5py.Dataset | h5py.Group,
        node_a_subgroups: list,
        node_b_name: str,
        node_b: netCDF4.Dataset | netCDF4.Group | h5py.Dataset | h5py.Group,
        node_b_subgroups: list,
    ) -> Iterator[GroupPair]:
        """Yield names and groups, as pairs, from two netCDF or HDF hierarchies.

        Parameters
        ----------
        node_a_name
            name of the first group or dataset
        node_a
            the first group or dataset
        node_b_name
            name of the second group or dataset
        node_b
            the second group or dataset

        Yields
        ------
        tuple
            group A name : str
            group A object : netCDF4.Group or None
            group B name : str
            group B object : netCDF4.Group or None
        """
        # get a sorted list of subgroups from both node_a and node_b
        for _, group_a_name, group_b_name in common_elements(
            node_a_subgroups if node_a is not None else "",
            node_b_subgroups if node_b is not None else "",
        ):
            yield GroupPair(
                group_a_name=node_a_name + "/" + group_a_name if group_a_name else "",
                group_a=(
                    node_a[group_a_name]
                    if (group_a_name and (group_a_name in node_a_subgroups))
                    else None
                ),
                group_b_name=node_b_name + "/" + group_b_name if group_b_name else "",
                group_b=(
                    node_b[group_b_name]
                    if (group_b_name and (group_b_name in node_b_subgroups))
                    else None
                ),
            )

        for _, subgroup_a_name, subgroup_b_name in common_elements(
            node_a_subgroups if node_a is not None else "",
            node_b_subgroups if node_b is not None else "",
        ):
            subnode_a_name = node_a_name + "/" + subgroup_a_name if subgroup_a_name else ""
            subnode_a = (
                node_a[subgroup_a_name]
                if (subgroup_a_name and (subgroup_a_name in node_a_subgroups))
                else None
            )
            subnode_a_subgroups = get_subgroups(subnode_a, file_type=self.file_types)

            subnode_b_name = node_a_name + "/" + subgroup_b_name if subgroup_b_name else ""
            subnode_b = (
                node_b[subgroup_b_name]
                if (subgroup_b_name and (subgroup_b_name in node_b_subgroups))
                else None
            )
            subnode_b_subgroups = get_subgroups(subnode_b, file_type=self.file_types)

            yield from self._dataset_pair_iterator(
                subnode_a_name,
                subnode_a,
                subnode_a_subgroups,
                subnode_b_name,
                subnode_b,
                subnode_b_subgroups,
            )

    def _create_var_properties(
        self, group: netCDF4.Dataset | netCDF4.Group | h5py.Dataset | h5py.Group, varname: str, original_dataset
    ) -> VarProperties:
        """Get the properties of a variable.

        Parameters
        ----------
        group
            a dataset or group of variables
        varname
            the name of the variable

        Returns
        -------
        VarProperties
        """
        if varname:
            if self.file_types == "netcdf":
                the_variable = group.variables[varname]
            elif self.file_types == "hdf5":
                the_variable = group[varname]

            v_dtype = str(the_variable.dtype)

            if self.file_types == "netcdf":
                v_dimensions = str(the_variable.dimensions)
            elif self.file_types == "hdf5":
                print(str(the_variable))
                for dim in the_variable.dims:
                    print(str(dim))
                v_dimensions = str([dim.label for dim in the_variable.dims])

            v_shape = str(the_variable.shape).strip()

            if self.file_types == "netcdf":
                v_chunking = str(the_variable.chunking()).strip()
            elif self.file_types == "hdf5":
                v_chunking = str(the_variable.chunks)

            def __name_from_h5_ref(ref):
                return original_dataset[ref].name

            v_attributes = {}
            if self.file_types == "netcdf":
                for name in the_variable.ncattrs():
                    try:
                        retrieved_value = the_variable.getncattr(name)
                    except KeyError as key_err:
                        # Added this check because of "unsupported datatype" error that prevented
                        # fully running comparisons on S5P_OFFL_L1B_IR_UVN collections.
                        retrieved_value = f"netCDF error: {str(key_err)}"

                    v_attributes[name] = retrieved_value
            elif self.file_types == "hdf5":
                for name in the_variable.attrs.keys():
                    attribute_value = the_variable.attrs[name]
                    if isinstance(attribute_value, np.ndarray):
                        if attribute_value.dtype == h5py.ref_dtype:
                            retrieved_value = __name_from_h5_ref(attribute_value[0][0])
                        else:
                            try:
                                retrieved_value = str(
                                    [__name_from_h5_ref(a[0]) for a in attribute_value]
                                )
                            except IndexError:
                                retrieved_value = str(attribute_value)

                    else:
                        retrieved_value = str(attribute_value)

                    v_attributes[name] = retrieved_value
        else:
            the_variable = None
            v_dtype = ""
            v_dimensions = ""
            v_shape = ""
            v_chunking = ""
            v_attributes = None

        return VarProperties(
            varname, the_variable, v_dtype, v_dimensions, v_shape, v_chunking, v_attributes
        )
