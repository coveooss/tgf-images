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
  TF_PLATFORM=linux_arm64
  EXT=linux_arm64
else
  TF_PLATFORM=linux_amd64
  EXT=linux_64-bits
fi

TERRAFORM_PATH=https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${TF_PLATFORM}.zip
echo "Downloading terraform from $TERRAFORM_PATH"
download_and_install "$TERRAFORM_PATH" "$EXE_FOLDER/terraform"

TERRAGRUNT_PATH=https://github.com/coveo/terragrunt/releases/download/v${TERRAGRUNT_VERSION}/terragrunt_${TERRAGRUNT_VERSION}_${EXT}.zip
echo "Downloading terragrunt from $TERRAGRUNT_PATH"
download_and_install "$TERRAGRUNT_PATH" "$EXE_FOLDER/terragrunt"

GOTEMPLATE_PATH=https://github.com/coveo/gotemplate/releases/download/v${GOTEMPLATE_VERSION}/gotemplate_${GOTEMPLATE_VERSION}_${EXT}.zip
echo "Downloading gotemplate from $GOTEMPLATE_PATH"
download_and_install "$GOTEMPLATE_PATH" "$EXE_FOLDER/gotemplate"
