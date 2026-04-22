variable "aws_region" {
  description = "Région AWS cible"
  type        = string
  default     = "eu-west-3" # Paris
}

variable "postgres_db" {
  description = "Nom de la base de données PostgreSQL"
  type        = string
  default     = "ressources_relationnelles"
}

variable "postgres_user" {
  description = "Utilisateur PostgreSQL"
  type        = string
  default     = "rr_user"
}

variable "postgres_password" {
  description = "Mot de passe PostgreSQL"
  type        = string
  sensitive   = true
}

variable "postgres_port" {
  description = "Port PostgreSQL"
  type        = number
  default     = 5432
}

variable "ssh_public_key_path" {
  description = "Chemin vers votre clé SSH publique locale"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
