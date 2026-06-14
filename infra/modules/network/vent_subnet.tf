resource "azurerm_virtual_network" "sdr_vnet" {
  name                = "vnet-sdr"
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "sdr_subnet" {
  name                 = "subnet-sdr"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.sdr_vnet.name
  address_prefixes     = ["10.0.1.0/24"]

}

resource "azurerm_subnet" "sdr_container_subnet" {
  name                 = "sdr-container-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.sdr_vnet.name
  address_prefixes     = ["10.0.2.0/24"]

   delegation {
    name = "sdr-container-app-delegation"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
   }

}
