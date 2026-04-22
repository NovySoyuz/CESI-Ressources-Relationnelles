terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # tfstate local pour l'instant
  # À migrer vers S3 backend pour la prod réelle :
  # backend "s3" {
  #   bucket = "rr-terraform-state"
  #   key    = "prod/terraform.tfstate"
  #   region = "eu-west-3"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ─── VPC ────────────────────────────────────────────────────────────────────
resource "aws_vpc" "rr_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "rr-vpc" }
}

# ─── Subnets (2 AZ requis par RDS) ──────────────────────────────────────────
resource "aws_subnet" "rr_subnet_a" {
  vpc_id                  = aws_vpc.rr_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = { Name = "rr-subnet-a" }
}

resource "aws_subnet" "rr_subnet_b" {
  vpc_id            = aws_vpc.rr_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = { Name = "rr-subnet-b" }
}

# ─── Internet Gateway ────────────────────────────────────────────────────────
resource "aws_internet_gateway" "rr_igw" {
  vpc_id = aws_vpc.rr_vpc.id
  tags   = { Name = "rr-igw" }
}

resource "aws_route_table" "rr_rt" {
  vpc_id = aws_vpc.rr_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.rr_igw.id
  }
  tags = { Name = "rr-rt" }
}

resource "aws_route_table_association" "rr_rta" {
  subnet_id      = aws_subnet.rr_subnet_a.id
  route_table_id = aws_route_table.rr_rt.id
}

# ─── Security Group EC2 ──────────────────────────────────────────────────────
resource "aws_security_group" "rr_ec2_sg" {
  name        = "rr-ec2-sg"
  description = "Acces SSH + HTTP vers EC2"
  vpc_id      = aws_vpc.rr_vpc.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restreindre à votre IP en prod
  }

  ingress {
    description = "HTTP Django"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "rr-ec2-sg" }
}

# ─── Security Group RDS ──────────────────────────────────────────────────────
resource "aws_security_group" "rr_rds_sg" {
  name        = "rr-rds-sg"
  description = "PostgreSQL accessible uniquement depuis EC2"
  vpc_id      = aws_vpc.rr_vpc.id

  ingress {
    description     = "PostgreSQL depuis EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rr_ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "rr-rds-sg" }
}

# ─── RDS Subnet Group ────────────────────────────────────────────────────────
resource "aws_db_subnet_group" "rr_db_subnet_group" {
  name       = "rr-db-subnet-group"
  subnet_ids = [aws_subnet.rr_subnet_a.id, aws_subnet.rr_subnet_b.id]
  tags       = { Name = "rr-db-subnet-group" }
}

# ─── RDS PostgreSQL (free tier) ──────────────────────────────────────────────
resource "aws_db_instance" "rr_postgres" {
  identifier        = "rr-postgres"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.postgres_db
  username = var.postgres_user
  password = var.postgres_password

  db_subnet_group_name   = aws_db_subnet_group.rr_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rr_rds_sg.id]

  publicly_accessible = false
  skip_final_snapshot = true

  tags = { Name = "rr-postgres" }
}

# ─── EC2 Key Pair ────────────────────────────────────────────────────────────
resource "aws_key_pair" "rr_keypair" {
  key_name   = "rr-keypair"
  public_key = file(var.ssh_public_key_path)
}

# ─── AMI Amazon Linux 2023 (free tier) ──────────────────────────────────────
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ─── EC2 Instance ────────────────────────────────────────────────────────────
resource "aws_instance" "rr_ec2" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.rr_subnet_a.id
  vpc_security_group_ids = [aws_security_group.rr_ec2_sg.id]
  key_name               = aws_key_pair.rr_keypair.key_name

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    postgres_host     = aws_db_instance.rr_postgres.address
    postgres_db       = var.postgres_db
    postgres_user     = var.postgres_user
    postgres_password = var.postgres_password
  })

  tags = { Name = "rr-ec2" }
}
