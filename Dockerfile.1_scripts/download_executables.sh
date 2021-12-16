#!/bin/sh
set -xeu

download_and_install() {
  url="$1"
  dest="$2"

  curl --silent --show-error --fail --location -o out.zip "$url"
  unzip -p out.zip > "$dest"
  chmod +x "$dest"
  rm -rf out.zip
}

if [ "$TARGETPLATFORM" = linux/arm64 ]; then
  PLATFORM=arm64
  TF_DOCS_PLATFORM=arm64
else
  PLATFORM=amd64
  TF_DOCS_PLATFORM=64-bits
fi

TFLINT_PATH=https://github.com/terraform-linters/tflint/releases/download/v${TF_LINT_VERSION}/tflint_linux_${PLATFORM}.zip
echo "Downloading tflint from $TFLINT_PATH"
download_and_install "$TFLINT_PATH" "$EXE_FOLDER/tflint"

TERRAFORM_DOCS_PATH=https://github.com/coveord/terraform-docs/releases/download/v${TF_DOC_VERSION}/terraform-docs_${TF_DOC_VERSION}_linux_${TF_DOCS_PLATFORM}.zip
echo "Downloading terraform-docs from $TERRAFORM_DOCS_PATH"
download_and_install "$TERRAFORM_DOCS_PATH" "$EXE_FOLDER/terraform-docs"
