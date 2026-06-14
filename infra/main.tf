terraform {


    required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.68.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id

}

resource azurerm_resource_group "sdr-systems" {
    name = "rg-sdr-systems"
    location = var.location
}

module "foundry" {
  source = "./modules/foundry"
  resource_group_name = azurerm_resource_group.sdr-systems.name
  location = azurerm_resource_group.sdr-systems.location

}

module "network" {
  source = "./modules/network"
  resource_group_name = azurerm_resource_group.sdr-systems.name
  location = var.location
  private_connection_resource_id = module.foundry.private_connection_resource_id
  custom_subdomain_name = module.foundry.custom_subdomain_name 
}

#module "acr" {
  #source = "./modules/acr"
  #resource_group_name = azurerm_resource_group.sdr-systems.name
  #location = azurerm_resource_group.sdr-systems.location

#}