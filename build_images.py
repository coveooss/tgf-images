import argparse
import logging
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
    command_line = " ".join(command)
    logging.info(f"Running command: {command_line}")
    return subprocess.run(command, check=True, capture_output=capture_output)


@contextmanager
def docker_buildx_builder() -> Generator[str, None, None]:
    logging.info("Creating a docker buildx builder")

    process = _run_command(["docker", "buildx", "create"], capture_output=True)
    builder_name = process.stdout.decode("utf-8").strip()

    logging.info(f"Created docker buildx builder named {builder_name}")

    try:
        yield builder_name
    finally:
        logging.info(f"Removing docker buildx builder named {builder_name}")
        _run_command(["docker", "buildx", "rm", builder_name])


def build_and_push_dockerfile(
    builder: str,
    dockerfile: Path,
    platform: str,
    git_tag: str,
    push: bool = False,
    beta: bool = False,
) -> None:
    name = dockerfile.name
    logging.info(f"Processing file {name}")

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

    logging.info(f"Building {target_tag} from {dockerfile.relative_to(Path.cwd())}")
    if not push:
        logging.info(f"Not pushing, call with --push to do so")
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
        + ["--platform", platform]
        + (["--push"] if push else [])
        + ["."]
    )

    _run_command(build_command)
    temp_dockerfile.unlink()


def main(platform: str, push: bool = False, beta: bool = False) -> None:
    git_tag = os.getenv("GIT_TAG")
    if not git_tag:
        git_tag = (
            subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
            .decode("utf-8")
            .strip()
        )
    logging.info(f"Git tag: {git_tag}")

    if not git_tag.startswith("v"):
        logging.info('Tag does not start with "v", ignoring')
        sys.exit(0)

    dockerfiles = [
        dockerfile
        for dockerfile in Path.cwd().glob("Dockerfile*")
        if dockerfile.is_file()
    ]
    dockerfiles = sorted(dockerfiles)

    relative_dockerfiles = [str(dockerfile.relative_to(Path.cwd())) for dockerfile in dockerfiles]
    logging.info(f"Will build the following dockerfiles in order: {relative_dockerfiles}")

    with docker_buildx_builder() as builder:
        for dockerfile in dockerfiles:
            build_and_push_dockerfile(
                builder, dockerfile, platform, git_tag, push, beta
            )


if __name__ == "__main__":
    logging.getLogger().setLevel(os.getenv("BUILD_IMAGE_LOG_LEVEL", "info").upper())

    parser = argparse.ArgumentParser(description="Build and push TGF images")
    parser.add_argument(
        "--push", action="store_true", help="Push images to GitHub Container Registry"
    )
    parser.add_argument("--beta", action="store_true", help="Add -beta to tags")
    parser.add_argument(
        "--platform",
        type=str,
        default="linux/arm64/v8,linux/amd64",
        help=(
            "What platform to build for. "
            "Matches docker buildx build --platform. "
            "Multiple values can be separated by commas."
        ),
    )
    args = parser.parse_args()

    main(args.platform, args.push, args.beta)
