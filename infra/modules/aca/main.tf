resource "azurerm_container_registry" "sdr_container_registry" {
  name                = "sdrcontainerregistry"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
  admin_enabled       = true       #with admin_enabled = true, the registry has a built-in admin username/password you can use directly, no Azure AD role requiredChange for prod env
}

resource "azurerm_container_app_environment" "sdr_container_env" {
  name                       = "sdr-container-app-environment"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  infrastructure_subnet_id   = var.sdr_container_subnet_id
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.container_app_logs.id

  lifecycle {
    ignore_changes = [
      infrastructure_resource_group_name,
    ]
  }

}

resource "azurerm_log_analytics_workspace" "container_app_logs" {
  name                       = "sdr-container-app-logs-workspace"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app" "sdr_container_app" {
  name                         = "sdr-container-app"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = azurerm_container_app_environment.sdr_container_env.id
  revision_mode                = "Single"

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.sdr_container_registry.admin_password
  }

  # Step 2 — tell the job how to authenticate to ACR using the secret
  registry {
    server               = azurerm_container_registry.sdr_container_registry.login_server
    username             = azurerm_container_registry.sdr_container_registry.admin_username
    password_secret_name = "acr-password"   # must match secret name above exactly
  }


  template {
    container {
      name   = "agent-server"
      image  = "${azurerm_container_registry.sdr_container_registry.login_server}/sdr-agent:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "FOUNDRY_PROJECT_ENDPOINT"
        value = var.foundry_project_endpoint
      }

      env {
        name  = "AZURE_AI_MODEL_DEPLOYMENT_NAME"
        value = var.azure_ai_model_deployment_name
      }
    }
  }

  ingress {
    external_enabled = false
    target_port      = 8088
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.agent.id]
  }
  
  #depends_on = [azurerm_role_assignment.acr_pull] we dont need this since admin_enabled       = true in the ACR
}


# --- The user-assigned identity --------------------------------------------
resource "azurerm_user_assigned_identity" "agent" {
  name                = "agent-test-uami"
  resource_group_name = var.resource_group_name
  location            = var.location
}

#resource "azurerm_role_assignment" "acr_pull" {
  #scope                = azurerm_container_registry.sdr_container_registry.id   # or var.acr_id
  #role_definition_name = "AcrPull"
  #principal_id         = azurerm_user_assigned_identity.agent.principal_id
#}

resource "azurerm_role_assignment" "foundry_user" {
  scope                = var.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.agent.principal_id
}



#resource "azurerm_role_assignment" "cognitive_user" {
  #scope                = var.cognitive_account_id
  #role_definition_name = "Foundry User"
  #principal_id         = azurerm_container_app_job.sdr_container_app_job.identity[0].principal_id
#}
