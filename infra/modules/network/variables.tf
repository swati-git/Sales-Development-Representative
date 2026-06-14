variable "resource_group_name" {
    type = string
   
    }

variable "location" {
    type = string
    
    }

variable "private_connection_resource_id" {
    type = string
    sensitive = "true"
    }
    
variable "custom_subdomain_name" {
    type = string
    sensitive = "true"
    }