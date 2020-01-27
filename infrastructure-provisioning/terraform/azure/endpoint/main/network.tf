# *****************************************************************************
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# ******************************************************************************

locals {
  endpoint_subnet_name       = "${var.service_base_name}-${var.endpoint_id}-subnet"
  endpoint_sg_name           = "${var.service_base_name}-${var.endpoint_id}-sg"
  endpoint_vpc_name          = "${var.service_base_name}-endpoint-vpc"
  additional_tag             = split(":", var.additional_tag)
  endpoint_ip_name           = "${var.service_base_name}-${var.endpoint_id}-eip"
}

resource "azurerm_virtual_network" "endpoint-network" {
  count               = var.vpc_id == "" ? 1 : 0
  name                = local.endpoint_vpc_name
  location            = data.azurerm_resource_group.data-endpoint-resource-group.location
  resource_group_name = data.azurerm_resource_group.data-endpoint-resource-group.name
  address_space       = [var.vpc_cidr]

  tags = {
    Name                              = local.endpoint_vpc_name
    "${local.additional_tag[0]}"      = local.additional_tag[1]
    "${var.tag_resource_id}"          = "${var.service_base_name}:${local.endpoint_vpc_name}"
    "${var.service_base_name}-Tag"    = local.endpoint_vpc_name
  }
}

data "azurerm_virtual_network" "data-endpoint-network" {
  name                = var.vpc_id == "" ? azurerm_virtual_network.endpoint-network.name : var.vpc_id
  resource_group_name = data.azurerm_resource_group.data-endpoint-resource-group.name
}

resource "azurerm_subnet" "endpoint-subnet" {
  count                = var.subnet_id == "" ? 1 : 0
  name                 = local.endpoint_subnet_name
  resource_group_name  = data.azurerm_resource_group.data-endpoint-resource-group.name
  virtual_network_name = data.azurerm_virtual_network.data-endpoint-network.name
  address_prefix       = var.subnet_cidr
}

data "azurerm_subnet" "data-endpoint-subnet" {
  name                 = var.subnet_id == "" ? azurerm_subnet.endpoint-subnet.name : var.subnet_id
  virtual_network_name = data.azurerm_virtual_network.data-endpoint-network.name
  resource_group_name  = data.azurerm_resource_group.data-endpoint-resource-group.name
}