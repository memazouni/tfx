# Lint as: python2, python3
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Contains functions that resolve command line arguments."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Callable, List, Text
from . import structures


def resolve_command_line(
    container_spec: structures.ContainerSpec,
    input_value_getter: Callable[[Text], Text],
    input_uri_getter: Callable[[Text], Text],
    output_uri_getter: Callable[[Text], Text],
) -> List[Text]:
  """Resolves placeholders in the command line of a container.

  Args:
    container_spec: Container structure to resolve
    input_value_getter: Function that returns value for an input
    input_uri_getter: Function that returns uri for an input
    output_uri_getter: Function that returns uri for an output

  Returns:
    Resolved command line.
  """

  def expand_command_line_arg(
      cmd_arg: structures.CommandlineArgumentType,
  ) -> Text:
    """Resolves a single argument."""
    if isinstance(cmd_arg, str):
      return cmd_arg
    elif isinstance(cmd_arg, structures.InputValuePlaceholder):
      return input_value_getter(cmd_arg.input_name)
    elif isinstance(cmd_arg, structures.InputUriPlaceholder):
      return input_uri_getter(cmd_arg.input_name)
    elif isinstance(cmd_arg, structures.OutputUriPlaceholder):
      return output_uri_getter(cmd_arg.output_name)
    else:
      raise TypeError()

  resolved_command_line = []
  for cmd_arg in (container_spec.command or []):
    resolved_cmd_arg = expand_command_line_arg(cmd_arg)
    assert isinstance(resolved_cmd_arg, Text)
    resolved_command_line.append(resolved_cmd_arg)
  return resolved_command_line
