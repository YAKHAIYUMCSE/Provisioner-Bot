import os

def generate_infra(request_id: int, env_type: str, env_name: str, services: list) -> str:
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated", str(request_id))
    os.makedirs(base_dir, exist_ok=True)

    if env_type.lower() == "docker":
        _generate_docker(base_dir, env_name, services)
    else:
        _generate_terraform(base_dir, env_name, services)

    return base_dir

def _generate_docker(base_dir, env_name, services):
    svc_blocks = ""
    for svc in services:
        if svc == "postgres":
            svc_blocks += """
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
"""
        elif svc == "redis":
            svc_blocks += """
  redis:
    image: redis:7-alpine
    networks:
      - app_network
"""
        elif svc == "nginx":
            svc_blocks += """
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - app_network
"""
        elif svc == "mongodb":
            svc_blocks += """
  mongodb:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    networks:
      - app_network
"""
        elif svc == "mysql":
            svc_blocks += """
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: secret
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app_network
"""

    if not svc_blocks:
        svc_blocks = """
  app:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - app_network
"""

    volumes = "\nvolumes:"
    has_vol = False
    for svc in services:
        if svc in ["postgres", "mongodb", "mysql"]:
            volumes += f"\n  {svc}_data:"
            has_vol = True
            
    if not has_vol:
        volumes = ""

    content = f"""version: "3.8"
# Auto-generated for {env_name} environment
services:{svc_blocks}
networks:
  app_network:
    driver: bridge
{volumes}
"""
    with open(os.path.join(base_dir, "docker-compose.yml"), "w") as f:
        f.write(content)

def _generate_terraform(base_dir, env_name, services):
    provider = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}
"""
    variables = f"""variable "region" {{
  default = "us-east-1"
}}

variable "env" {{
  default = "{env_name}"
}}

variable "instance_type" {{
  default = "t3.micro"
}}
"""
    main = f"""# Auto-generated Terraform for {env_name}

resource "aws_vpc" "main" {{
  cidr_block = "10.0.0.0/16"
  tags = {{ Name = "{env_name}-vpc" }}
}}

resource "aws_instance" "app" {{
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = var.instance_type
  tags = {{ Name = "{env_name}-instance" }}
}}
"""
    with open(os.path.join(base_dir, "provider.tf"), "w") as f:
        f.write(provider)
    with open(os.path.join(base_dir, "variables.tf"), "w") as f:
        f.write(variables)
    with open(os.path.join(base_dir, "main.tf"), "w") as f:
        f.write(main)
