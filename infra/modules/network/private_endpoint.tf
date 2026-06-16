
resource "azurerm_private_endpoint" "sdr_pe" {
  name                = "sdr-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = azurerm_subnet.sdr_subnet.id

  private_service_connection {
    name                           = "sdr-psc"
    private_connection_resource_id = var.private_connection_resource_id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  # ONE zone group, BOTH zone ids. Azure creates an A record in each zone,
  # all pointing at private IPs on this same PE NIC 
  private_dns_zone_group {
    name = "default"
    private_dns_zone_ids = [
      azurerm_private_dns_zone.sdr_dns.id,
      azurerm_private_dns_zone.private_pe_dns_servicesai.id,
    ]
  }
}


resource "azurerm_private_dns_zone" "sdr_dns" {
  name                = "privatelink.cognitiveservices.azure.com"
  resource_group_name = var.resource_group_name
}


resource "azurerm_private_dns_zone_virtual_network_link" "sdr_dns_link" {
  name                  = "sdr-dns-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.sdr_dns.name
  virtual_network_id    = azurerm_virtual_network.sdr_vnet.id
  registration_enabled  = false
}

resource "azurerm_private_dns_a_record" "sdr_dns_record" {
  name                = var.custom_subdomain_name
  zone_name           = azurerm_private_dns_zone.sdr_dns.name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = [
    azurerm_private_endpoint.sdr_pe.private_service_connection[0].private_ip_address
  ]
}

resource "azurerm_private_dns_zone" "private_pe_dns_servicesai" {
  name                = "privatelink.services.ai.azure.com"
  resource_group_name = var.resource_group_name
}

resource "azurerm_private_dns_zone_virtual_network_link" "link_servicesai" {
  name                  = "link-services-ai"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.private_pe_dns_servicesai.name
  virtual_network_id    = azurerm_virtual_network.sdr_vnet.id
  registration_enabled  = false
}