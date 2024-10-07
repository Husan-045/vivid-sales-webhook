variable "app_timeout" {
  description = "Number of seconds until the lambda function times out"
  type        = number
}

variable "app_memory" {
  description = "Number of megabytes of memory to allocate to the lambda function"
  type        = number
}





variable "REDIS_ADDRESS" {
  default = ""
}
variable "REDIS_PORT" {
  default = ""
}


resource "aws_lambda_function" "lambda_function" {
  depends_on = [null_resource.push_image]
  function_name = var.app_ident
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.ecr_repository.repository_url}:${null_resource.push_image.triggers.code_hash}"
  timeout       = var.app_timeout
  memory_size   = var.app_memory
  publish       = true

  vpc_config {
    subnet_ids = var.PRIVATE_SUBNET_IDS
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  environment {
    variables = {
      ENVIRONMENT              = var.environment,
      CLOUDWATCH_NAMESPACE     = var.cloudwatch_namespace,
      REDIS_ADDRESS            = var.REDIS_ADDRESS,
      REDIS_PORT               = var.REDIS_PORT,
    }
  }

  # Adding tags to the Lambda function
  tags = {
    NR_MONITORING_ON = "true"
  }
}

resource "aws_security_group" "lambda_sg" {
  name   = "${var.app_ident}_lambda_sg2"
  vpc_id = data.aws_vpc.selected.id

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
