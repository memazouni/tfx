# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Common code shared by container based launchers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Any, Dict, List, Text

import jinja2

from tfx import types
from tfx.components.base import executor_spec
from tfx.dsl.components import _command_line_resolver
from tfx.dsl.components import structures


def resolve_container_template(
    container_spec_tmpl: executor_spec.ExecutorContainerSpec,
    input_dict: Dict[Text, List[types.Artifact]],
    output_dict: Dict[Text, List[types.Artifact]],
    exec_properties: Dict[Text, Any]) -> executor_spec.ExecutorContainerSpec:
  """Resolves Jinja2 template languages from an executor container spec.

  Args:
    container_spec_tmpl: the container spec template to be resolved.
    input_dict: Dictionary of input artifacts consumed by this component.
    output_dict: Dictionary of output artifacts produced by this component.
    exec_properties: Dictionary of execution properties.

  Returns:
    A resolved container spec.
  """
  context = {
      'input_dict': input_dict,
      'output_dict': output_dict,
      'exec_properties': exec_properties,
  }
  if isinstance(container_spec_tmpl, structures.ContainerSpec):
    return executor_spec.ExecutorContainerSpec(
        image=container_spec_tmpl.image,
        command=resolve_command_line_for_non_managed(
            container_spec=container_spec_tmpl,
            input_dict=input_dict,
            output_dict=output_dict,
            exec_properties=exec_properties,
        ),
    )
  return executor_spec.ExecutorContainerSpec(
      image=_render_text(container_spec_tmpl.image, context),
      command=_render_items(container_spec_tmpl.command, context),
      args=_render_items(container_spec_tmpl.args, context))


def _render_items(items: List[Text], context: Dict[Text, Any]) -> List[Text]:
  if not items:
    return items

  return [_render_text(item, context) for item in items]


def _render_text(text: Text, context: Dict[Text, Any]) -> Text:
  return jinja2.Template(text).render(context)


def resolve_command_line_for_non_managed(
    container_spec: structures.ContainerSpec,
    input_dict: Dict[Text, List[types.Artifact]],
    output_dict: Dict[Text, List[types.Artifact]],
    exec_properties: Dict[Text, Any],
) -> List[Text]:
  """Resolves placeholders in the command line of a container.

  Args:
    container_spec: Container structure to resolve
    input_dict: Dictionary of input artifacts consumed by this component.
    output_dict: Dictionary of output artifacts produced by this component.
    exec_properties: Dictionary of execution properties.

  Returns:
    Resolved command line.
  """

  def input_value_getter(input_name) -> Text:
    return exec_properties[input_name]

  def input_uri_getter(input_name) -> Text:
    return input_dict[input_name][0].uri

  def output_uri_getter(output_name) -> Text:
    return output_dict[output_name][0].uri

  resolved_command_line = _command_line_resolver.resolve_command_line(
      container_spec=container_spec,
      input_value_getter=input_value_getter,
      input_uri_getter=input_uri_getter,
      output_uri_getter=output_uri_getter,
  )
  return resolved_command_line


def to_swagger_dict(config: Any) -> Any:
  """Converts a config object to a swagger API dict.

  This utility method recursively converts swagger code generated configs into
  a valid swagger dictionary. This method is trying to workaround a bug
  (https://github.com/swagger-api/swagger-codegen/issues/8948)
  from swagger generated code

  Args:
    config: The config object. It can be one of List, Dict or a Swagger code
      generated object, which has a `attribute_map` attribute.

  Returns:
    The original object with all Swagger generated object replaced with
    dictionary object.
  """
  if isinstance(config, list):
    return [to_swagger_dict(x) for x in config]
  if hasattr(config, 'attribute_map'):
    return {
        swagger_name: to_swagger_dict(getattr(config, key))
        for (key, swagger_name) in config.attribute_map.items()
        if getattr(config, key)
    }
  if isinstance(config, dict):
    return {key: to_swagger_dict(value) for key, value in config.items()}
  return config
