resource "aws_ecr_repository" "ecr_repository" {
  name = "${var.app_ident}_repository"
}

variable "code_hash_file" {
  description = "Filename of the code hash file"
  type        = string
}

resource "null_resource" "push_image" {
  triggers = {
    code_hash = filemd5(var.code_hash_file)
    ecr_repo = aws_ecr_repository.ecr_repository.repository_url
    force = 3
  }

  # NOTE: if you are doing the deploy from a mac computer with an ARM processor you will need to:
  #       - change: docker build  ->  docker buildx build
  #       - add: --platform linux/amd64
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
    # For Non-ARM (bitbucket,windows laptops): docker build \
    echo "Build the Docker Image"
    docker build \
      -t ${aws_ecr_repository.ecr_repository.repository_url}:${self.triggers.code_hash} \
      -t ${aws_ecr_repository.ecr_repository.repository_url}:latest \
      .

    echo "Push Docker Image to AWS ECR Container Repository"
    docker push ${aws_ecr_repository.ecr_repository.repository_url}:${self.triggers.code_hash}
    docker push ${aws_ecr_repository.ecr_repository.repository_url}:latest
    sleep 10
    EOF
  }
}
