import argparse
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from subprocess import CompletedProcess
from typing import Generator, List

TARGET_REGISTRY = "ghcr.io/coveooss/tgf"


def _run_command(command: List[str], capture_output: bool = False) -> CompletedProcess:
    print(" ".join(command))
    return subprocess.run(command, check=True, capture_output=capture_output)


@contextmanager
def docker_buildx_builder() -> Generator[str, None, None]:
    print("Creating a docker buildx builder")

    process = _run_command(["docker", "buildx", "create"], capture_output=True)
    builder_name = process.stdout.decode("utf-8").strip()

    print(f"Created docker buildx builder named {builder_name}")

    try:
        yield builder_name
    finally:
        print(f"Removing docker buildx builder named {builder_name}")
        _run_command(["docker", "buildx", "rm", builder_name])


def build_and_push_dockerfile(
    builder: str,
    dockerfile: Path,
    git_tag: str,
    push: bool = False,
    beta: bool = False,
) -> None:
    name = dockerfile.name
    print(f"\n----------------------------------------\nProcessing file {name}")

    tag = (re.match("Dockerfile\.\d+(\.(.+))?", name).group(2) or "").lower()
    tag_suffix = f"-{tag}" if tag else ""

    version = git_tag.lstrip("v")
    version_maj_min = ".".join(version.split(".")[:2])

    beta_part = "-beta" if beta else ""
    target_tag = f"{TARGET_REGISTRY}:{version}{beta_part}{tag_suffix}"
    target_tag_major_min = f"{TARGET_REGISTRY}:{version_maj_min}{beta_part}{tag_suffix}"

    dockerfile_content = dockerfile.read_text(encoding="utf-8")
    dockerfile_content = dockerfile_content.replace(
        "${GIT_TAG}", f"{version}{beta_part}"
    )
    dockerfile_content = dockerfile_content.replace(
        "TGF_IMAGE_MAJ_MIN=", f"TGF_IMAGE_MAJ_MIN={version_maj_min}"
    )
    temp_dockerfile = Path("dockerfile.temp")
    temp_dockerfile.open(mode="w", encoding="utf-8").write(dockerfile_content)

    print(f"== Building {target_tag} from {dockerfile.relative_to(Path.cwd())} ==")
    if not push:
        print(f"Not pushing, call with --push to do so")
    build_command = (
        [
            "docker",
            "buildx",
            "build",
            "--builder",
            builder,
            "-f",
            temp_dockerfile.name,
            "-t",
            target_tag,
        ]
        + (["-t", target_tag_major_min] if push else [])
        + ["--platform", "linux/arm64/v8,linux/amd64"]
        + (["--push"] if push else [])
        + ["."]
    )

    _run_command(build_command)
    temp_dockerfile.unlink()


def main(push: bool = False, beta: bool = False) -> None:
    git_tag = os.getenv("GIT_TAG")
    if not git_tag:
        git_tag = (
            subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
            .decode("utf-8")
            .strip()
        )
    print(f"Git tag: {git_tag}")

    if not git_tag.startswith("v"):
        print('Tag does not start with "v", ignoring')
        sys.exit(0)

    dockerfiles = [
        dockerfile
        for dockerfile in Path.cwd().glob("Dockerfile*")
        if dockerfile.is_file()
    ]
    dockerfiles = sorted(dockerfiles)

    print("Will build the following dockerfiles in order:")
    for dockerfile in dockerfiles:
        print(f"- {dockerfile.relative_to(Path.cwd())}")

    with docker_buildx_builder() as builder:
        for dockerfile in dockerfiles:
            build_and_push_dockerfile(builder, dockerfile, git_tag, push, beta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and push TGF images")
    parser.add_argument(
        "--push", action="store_true", help="Push images to GitHub Container Registry"
    )
    parser.add_argument("--beta", action="store_true", help="Add -beta to tags")
    args = parser.parse_args()

    main(args.push, args.beta)
