resource "aws_ecr_repository" "ecr_repository" {
  name = "${var.app_ident}_repository"
}

variable "code_hash_file" {
  description = "Filename of the code hash file"
  type        = string
}

resource "null_resource" "push_image" {
  depends_on = [null_resource.login_to_ecr]
  triggers = {
    code_hash = filemd5(var.code_hash_file)
    ecr_repo = aws_ecr_repository.ecr_repository.repository_url
    force = 2
  }

  provisioner "local-exec" {
    command = <<EOF
    set -e # Exit immediately if a command exits with a non-zero status.
    cd ..

    echo "Running docker build: ${path.cwd}"

    echo "Log into AWS ECR Container Repository"
    aws ecr get-login-password \
      --region ${data.aws_region.current.name} | \
      docker login \
        --username AWS \
        --password-stdin ${aws_ecr_repository.ecr_repository.repository_url}

    # For ARM Mac: docker buildx build --platform linux/amd64 \
    # For Non-ARM (github,windows laptops): docker build \
    echo "Build the Docker Image"
    docker buildx build --platform linux/arm64 --provenance=false \
      --no-cache \
      --push \
      --build-arg PIP_INDEX_URL \
      -t ${aws_ecr_repository.ecr_repository.repository_url}:${self.triggers.code_hash} \
      -t ${aws_ecr_repository.ecr_repository.repository_url}:latest \
      .

    sleep 10
    EOF
  }
}
