output "private_connection_resource_id" {
  value     = azurerm_cognitive_account.sdr_account.id
  sensitive = true
}

output "custom_subdomain_name" {

    value = azurerm_cognitive_account.sdr_account.custom_subdomain_name
    sensitive = true
}

output "azurerm_cognitive_account_id" {
  value     = azurerm_cognitive_account.sdr_account.id
  sensitive = true
}

output "foundry_project_endpoint" {
  value     = azurerm_cognitive_account.sdr_account.endpoint
  sensitive = true
}


output "azure_ai_model_deployment_name" {
  value     = azurerm_cognitive_deployment.sdr_deployment.name
  sensitive = true
}
