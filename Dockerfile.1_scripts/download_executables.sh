#!/bin/sh

set -xeu

if [ "$TARGETPLATFORM" = linux/arm64 ]
then
  PLATFORM=arm64
  TF_DOCS_PLATFORM=arm64
else
  PLATFORM=amd64
  TF_DOCS_PLATFORM=64-bits
fi

TFLINT_PATH=https://github.com/terraform-linters/tflint/releases/download/v${TF_LINT_VERSION}/tflint_linux_${PLATFORM}.zip
echo "Downloading tflint from $TFLINT_PATH"
curl -sLo_ "${TFLINT_PATH}"
unzip -p _ > "${EXE_FOLDER}"/tflint
chmod +x "${EXE_FOLDER}"/tflint
rm _

TERRAFORM_DOCS_PATH=https://github.com/coveord/terraform-docs/releases/download/v${TF_DOC_VERSION}/terraform-docs-v${TF_DOC_VERSION}-linux-${TF_DOCS_PLATFORM}
echo "Downloading terraform-docs from $TERRAFORM_DOCS_PATH"
curl -sLo "${EXE_FOLDER}"/terraform-docs "${TERRAFORM_DOCS_PATH}"
chmod +x "${EXE_FOLDER}"/terraform-docs
