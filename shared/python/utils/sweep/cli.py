"""Console entry point for the reusable Hydra sweep engine."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def normalize_config_arguments(argv: list[str], cwd: Path) -> list[str]:
    """Translate ``--config FILE`` into Hydra's absolute config arguments."""
    normalized = list(argv)
    config_value = None
    config_index = None
    for index, argument in enumerate(normalized[1:], start=1):
        if argument == "--config":
            if index + 1 >= len(normalized):
                raise SystemExit("--config requires a YAML file")
            config_value = normalized[index + 1]
            config_index = (index, index + 2)
            break
        if argument.startswith("--config="):
            config_value = argument.split("=", 1)[1]
            config_index = (index, index + 1)
            break

    has_native_config = any(
        argument == "--config-path" or argument.startswith("--config-path=")
        for argument in normalized[1:]
    )
    if config_value is None:
        if has_native_config or any(
            argument in {"--help", "-h", "--hydra-help", "--version"}
            for argument in normalized[1:]
        ):
            return normalized
        raise SystemExit(
            "Missing --config FILE. Example: hydra-sweep --config path/config.yaml -m"
        )

    config_path = Path(config_value)
    if not config_path.is_absolute():
        config_path = (cwd / config_path).resolve()
    if config_path.suffix not in {".yaml", ".yml"} or not config_path.is_file():
        raise SystemExit(f"Sweep config does not exist or is not YAML: {config_path}")
    if has_native_config:
        raise SystemExit("Use either --config or Hydra's --config-path, not both")

    assert config_index is not None
    start, end = config_index
    normalized[start:end] = [
        f"--config-path={config_path.parent}",
        f"--config-name={config_path.stem}",
    ]
    return normalized


def _patch_argparse_help() -> None:
    original = getattr(argparse.ArgumentParser, "_check_help", None)
    if original is None:
        return

    def check_help(self: argparse.ArgumentParser, action: argparse.Action) -> None:
        if action.help is not None and not isinstance(action.help, str):
            action.help = str(action.help)
        original(self, action)

    argparse.ArgumentParser._check_help = check_help


def main() -> None:
    sys.argv = normalize_config_arguments(sys.argv, Path.cwd())
    _patch_argparse_help()
    try:
        import hydra
        from omegaconf import DictConfig, OmegaConf
    except ImportError as exc:
        raise SystemExit(
            "Missing Hydra. Install the repository's Python dependencies "
            "before running hydra-sweep."
        ) from exc

    from .runner import run_sweep_point

    @hydra.main(version_base=None, config_path=None, config_name=None)
    def hydra_main(cfg: DictConfig) -> None:
        print(OmegaConf.to_yaml(cfg))
        result = run_sweep_point(cfg)
        print(OmegaConf.to_yaml(OmegaConf.create(result), resolve=True))

    try:
        hydra_main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
