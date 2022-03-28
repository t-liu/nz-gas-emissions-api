resource "aws_vpc" "vpc" {
  cidr_block           = var.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name        = "${var.name}-vpc-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.name}-igw-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = element(var.public_subnets, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  count                   = length(var.public_subnets)
  map_public_ip_on_launch = true
  tags = {
    Name        = "${var.name}-public-subnet-${var.environment}-${format("%03d", count.index+1)}"
    Environment = var.environment
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = element(var.private_subnets, count.index)
  availability_zone = element(var.availability_zones, count.index)
  count             = length(var.private_subnets)
  map_public_ip_on_launch = false
  tags = {
    Name        = "${var.name}-private-subnet-${var.environment}-${format("%03d", count.index+1)}"
    Environment = var.environment
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.name}-routing-table-public"
    Environment = var.environment
  }
}

resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.internet_gateway.id
}

resource "aws_route_table" "private" {
  count  = length(var.private_subnets)
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.name}-routing-table-private-${format("%03d", count.index+1)}"
    Environment = var.environment
  }
}

resource "aws_route" "private" {
  count                  = length(compact(var.private_subnets))
  route_table_id         = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.internet_gateway.id
}

resource "aws_route_table_association" "public_route_table_association" {
  count          = length(var.public_subnets)
  subnet_id      = element(aws_subnet.public_subnet.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_route_table_association" {
  count          = length(var.private_subnets)
  subnet_id      = element(aws_subnet.private_subnet.*.id, count.index)
  route_table_id = element(aws_route_table.private.*.id, count.index)
}

# outputs
output "id" {
  value = aws_vpc.vpc.id
}

output "public_subnets" {
  value = aws_subnet.public_subnet
}

output "private_subnets" {
  value = aws_subnet.private_subnet
}