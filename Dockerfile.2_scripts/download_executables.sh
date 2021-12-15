#!/bin/sh

set -x

if [ "$TARGETPLATFORM" = linux/arm64 ]
then
  HELM_PLATFORM=linux-arm64
else
  HELM_PLATFORM=linux-amd64
fi

# Install kubectl
curl -sLo_ https://storage.googleapis.com/kubernetes-release/release/v"${KUBE_VERSION}"/bin/"${TARGETPLATFORM}"/kubectl && \
    mv _ "${EXE_FOLDER}"/kubectl && \
    chmod +x "${EXE_FOLDER}"/kubectl && \
    mkdir -p /home/tgf/.kube && \
    touch "${KUBECONFIG}" && \
    chmod 666 "${KUBECONFIG}"

# Install helm (git is also required by helm)
curl -sL https://get.helm.sh/helm-v"${HELM_VERSION}"-${HELM_PLATFORM}.tar.gz | tar xzo && \
    mv ./${HELM_PLATFORM}/helm "${EXE_FOLDER}"/helm && \
    rm -rf ./${HELM_PLATFORM} && \
    chmod +x "$EXE_FOLDER"/helm
