
# API Gateway REST API
resource "aws_api_gateway_rest_api" "my_api" {
  name        = var.app_ident
  description = "API for handling POST requests"
}

# API Gateway Resource (Root Resource)
resource "aws_api_gateway_resource" "root_resource" {
  rest_api_id = aws_api_gateway_rest_api.my_api.id
  parent_id   = aws_api_gateway_rest_api.my_api.root_resource_id
  path_part   = "vivid"  # Root resource
}

# API Gateway Method (POST)
resource "aws_api_gateway_method" "post_method" {
  rest_api_id   = aws_api_gateway_rest_api.my_api.id
  resource_id   = aws_api_gateway_rest_api.my_api.root_resource_id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration with Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.my_api.id
  resource_id = aws_api_gateway_rest_api.my_api.root_resource_id
  http_method = aws_api_gateway_method.post_method.http_method
  type        = "AWS_PROXY"

  integration_http_method = "POST"
  uri                     = aws_lambda_function.lambda_function.invoke_arn
}

# Lambda permission to allow API Gateway to invoke it
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.my_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.my_api.id
  stage_name  = var.environment
}