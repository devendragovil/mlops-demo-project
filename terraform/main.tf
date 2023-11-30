resource "aws_vpc" "mlops-nico-vpc" {
  cidr_block           = "10.123.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "mlops-public-subnet" {
  vpc_id                  = aws_vpc.mlops-nico-vpc.id
  cidr_block              = "10.123.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-west-2a"
}

resource "aws_internet_gateway" "mlops-internet-gateway" {
  vpc_id = aws_vpc.mlops-nico-vpc.id
}

resource "aws_route_table" "mlops-public-route-table" {
  vpc_id = aws_vpc.mlops-nico-vpc.id
}

resource "aws_route" "default-route" {
  route_table_id         = aws_route_table.mlops-public-route-table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.mlops-internet-gateway.id
}

resource "aws_route_table_association" "mlops-public-assoc" {
  subnet_id      = aws_subnet.mlops-public-subnet.id
  route_table_id = aws_route_table.mlops-public-route-table.id
}

resource "aws_security_group" "mlops-sg" {
  name        = "mlops-sg"
  description = "mlops security group"
  vpc_id      = aws_vpc.mlops-nico-vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "mlops-ec2-key" {
  key_name   = "mlops-ec2-key"
  public_key = file("~/.ssh/mlops-nico-demo.pub")
}

resource "aws_instance" "mlops-ec2-instance" {
  instance_type = "t2.large"
  ami           = data.aws_ami.mlops-ec2-ami.id

  tags = {
    Name = "mlops-nico-ec2-instance"
  }

  key_name               = aws_key_pair.mlops-ec2-key.id
  vpc_security_group_ids = [aws_security_group.mlops-sg.id]
  subnet_id              = aws_subnet.mlops-public-subnet.id

  root_block_device {
    volume_size = 10
  }
}

resource "aws_dynamodb_table" "mlops-dynamodb" {
  name           = "customer-applications"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 2
  hash_key       = "ID"

  attribute {
    name = "ID"
    type = "S"
  }
}