output "private_connection_resource_id" {
  value     = azurerm_cognitive_account.sdr_account.id
  sensitive = true
}

output "custom_subdomain_name" {

    value = azurerm_cognitive_account.sdr_account.custom_subdomain_name
    sensitive = true
}