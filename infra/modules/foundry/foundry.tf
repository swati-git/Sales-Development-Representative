resource "azurerm_cognitive_account" "sdr_account" {
  name                = "cognitive-account-sdr"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "AIServices"
  sku_name            = "S0"
  project_management_enabled = true
  
  identity {
    type = "SystemAssigned"
  }

  custom_subdomain_name =  "sdr-system"

  public_network_access_enabled = false

} 

resource "azurerm_cognitive_account_project" "sdr_project" {
  name                 = "cognitive-project-sdr"
  cognitive_account_id = azurerm_cognitive_account.sdr_account.id
  location             = var.location
  description          = "A Sales Development Representative system "
  display_name         = "SDR System"

  identity {
    type = "SystemAssigned"
  }

}

resource "azurerm_cognitive_deployment" "sdr_deployment" {
  name                 = "cognitive-deployment-sdr"
  cognitive_account_id = azurerm_cognitive_account.sdr_account.id
  rai_policy_name      = "Microsoft.DefaultV2" 

  model {
    format  = "xAI"
    name = "grok-4-1-fast-reasoning"
    version = "1"
  }

  sku {
    name = "GlobalStandard"
    capacity = 20
  }
}

#resource "azurerm_role_assignemnt" "sdr_project_manager" {
  #scope = azurerm_cognitive_account_project.sdr_project.id
  #principal_id         = azurerm_container_app_job.<>.identity[0].principal_id ???
  #role_definition_name = "Foundry Project Manager"

#}
