#!/bin/sh

set -xeu

if [ "$TARGETPLATFORM" = linux/arm64 ]
then
  TF_PLATFORM=linux_arm64
  EXT=linux_arm64
else
  TF_PLATFORM=linux_amd64
  EXT=linux_64-bits
fi


TERRAFORM_PATH=https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${TF_PLATFORM}.zip
echo "Downloading terraform from $TERRAFORM_PATH"
curl -sLo_ "${TERRAFORM_PATH}"
unzip -p _ > "${EXE_FOLDER}"/terraform
chmod +x "${EXE_FOLDER}"/terraform
rm -f _

TERRAGRUNT_PATH=https://github.com/coveo/terragrunt/releases/download/v${TERRAGRUNT_VERSION}/terragrunt_${TERRAGRUNT_VERSION}_${EXT}.zip
echo "Downloading terragrunt from $TERRAGRUNT_PATH"
curl -sLo_ "${TERRAGRUNT_PATH}"
unzip -p _ > "${EXE_FOLDER}"/terragrunt
chmod +x "${EXE_FOLDER}"/terragrunt
rm -f _

GOTEMPLATE_PATH=https://github.com/coveo/gotemplate/releases/download/v${GOTEMPLATE_VERSION}/gotemplate_${GOTEMPLATE_VERSION}_${EXT}.zip
echo "Downloading gotemplate from $GOTEMPLATE_PATH"
curl -sLo_ "${GOTEMPLATE_PATH}"
unzip -p _ > "${EXE_FOLDER}"/gotemplate
chmod +x "${EXE_FOLDER}"/gotemplate
rm -f _
