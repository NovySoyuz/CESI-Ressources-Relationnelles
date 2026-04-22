output "ec2_public_ip" {
  description = "IP publique de l'EC2 (pour SSH et accès Django)"
  value       = aws_instance.rr_ec2.public_ip
}

output "rds_endpoint" {
  description = "Endpoint RDS PostgreSQL (interne au VPC)"
  value       = aws_db_instance.rr_postgres.address
}

output "django_url" {
  description = "URL d'accès à l'application Django"
  value       = "http://${aws_instance.rr_ec2.public_ip}:8000"
}

output "ssh_command" {
  description = "Commande SSH pour se connecter à l'EC2"
  value       = "ssh -i ~/.ssh/id_rsa ec2-user@${aws_instance.rr_ec2.public_ip}"
}
