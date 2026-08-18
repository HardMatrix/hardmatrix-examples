"""Config-driven FuseSoC/OpenROAD sweep engine."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from omegaconf import DictConfig, OmegaConf


_MISSING = object()


def _cfg_select(cfg: DictConfig, path: str) -> Any:
    value = OmegaConf.select(cfg, path, default=_MISSING)
    if value is _MISSING:
        raise ValueError(f"Missing config value: {path}")
    return value


def _result_key(path: str) -> str:
    return path.rsplit(".", 1)[-1]


def _coerce_number(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        if any(char in value for char in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value


def _ceil_log(value: Any, base: Any) -> int:
    value = int(value)
    base = int(base)
    if value < 1 or base <= 1:
        raise ValueError("ceil_log requires value >= 1 and base > 1")
    stages = 0
    covered = 1
    while covered < value:
        covered *= base
        stages += 1
    return stages


class ConfigExpression:
    """Evaluate a deliberately small arithmetic language over Hydra config."""

    _ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Attribute,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )
    _FUNCTIONS = {
        "ceil": math.ceil,
        "ceil_log": _ceil_log,
        "floor": math.floor,
        "int": int,
        "max": max,
        "min": min,
        "round": round,
        "bit_length": lambda value: int(value).bit_length(),
    }

    def __init__(self, cfg: DictConfig) -> None:
        self._cfg = cfg

    def eval(self, expression: str) -> Any:
        tree = ast.parse(expression, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, self._ALLOWED_NODES):
                raise ValueError(f"Unsupported expression syntax: {expression}")
            if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name):
                raise ValueError(
                    f"Unsupported function call in expression: {expression}"
                )
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self._FUNCTIONS:
                return self._FUNCTIONS[node.id]
            return _coerce_number(_cfg_select(self._cfg, node.id))
        if isinstance(node, ast.Attribute):
            return _coerce_number(_cfg_select(self._cfg, self._attr_path(node)))
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return +operand
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left**right
        if isinstance(node, ast.Call):
            function = self._eval_node(node.func)
            arguments = [self._eval_node(argument) for argument in node.args]
            return function(*arguments)
        raise ValueError(f"Unsupported expression node: {ast.dump(node)}")

    @staticmethod
    def _attr_path(node: ast.Attribute) -> str:
        parts = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            raise ValueError(f"Unsupported config reference: {ast.dump(node)}")
        parts.append(current.id)
        return ".".join(reversed(parts))


def apply_derived_values(cfg: DictConfig) -> None:
    expression = ConfigExpression(cfg)
    for path, formula in cfg.get("derive", {}).items():
        value = expression.eval(str(formula))
        OmegaConf.update(cfg, str(path), value, merge=False, force_add=True)


def _project_path(project_root: Path, value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else (project_root / path).resolve()


def clock_period_ns(cfg: DictConfig) -> float:
    clock_mhz = float(_cfg_select(cfg, "experiment.clock_mhz"))
    if clock_mhz <= 0:
        raise ValueError("experiment.clock_mhz must be positive")
    return 1000.0 / clock_mhz


def build_fusesoc_command(
    cfg: DictConfig, work_root: Path, project_root: Path
) -> list[str]:
    fusesoc_cfg = cfg.get("fusesoc", {})
    command = [str(fusesoc_cfg.get("executable", "fusesoc"))]
    for root in fusesoc_cfg.get("cores_roots", []):
        command.extend(["--cores-root", str(_project_path(project_root, root))])
    command.append("run")
    if bool(fusesoc_cfg.get("clean", True)):
        command.append("--clean")
    command.extend(
        [
            "--target",
            str(cfg.target),
            "--work-root",
            str(work_root),
            str(cfg.core),
        ]
    )
    for name, value in cfg.get("parameters", {}).items():
        command.append(f"--{name}={value}")
    command.extend(str(argument) for argument in fusesoc_cfg.get("arguments", []))
    return command


def run_fusesoc(cfg: DictConfig, work_root: Path, project_root: Path) -> None:
    environment = os.environ.copy()
    environment["STA_CLK_PERIOD_NS"] = f"{clock_period_ns(cfg):.6f}"
    parameters = cfg.get("parameters", {})
    if parameters:
        environment["VERILOG_TOP_PARAMS"] = " ".join(
            f"{name} {value}" for name, value in parameters.items()
        )
    for section in ("environment", "openroad"):
        for name, value in cfg.get(section, {}).items():
            name = str(name)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise ValueError(f"Invalid environment variable name: {name}")
            if value is None:
                environment.pop(name, None)
            else:
                environment[name] = (
                    "1" if value is True else "0" if value is False else str(value)
                )
    subprocess.run(
        build_fusesoc_command(cfg, work_root, project_root),
        cwd=project_root,
        check=True,
        env=environment,
    )


def _single_match(root: Path, pattern: str) -> Path:
    matches = sorted(root.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one match for {pattern} under {root}, found {len(matches)}"
        )
    return matches[0]


def find_orfs_reports(work_root: Path) -> tuple[Path, Path, Path]:
    timing = _single_match(work_root / "reports", "**/1_Post_synthesis.rpt")
    statistics = timing.with_name("synth_stat.txt")
    checks = timing.with_name("synth_check.txt")
    for required in (statistics, checks):
        if not required.is_file():
            raise RuntimeError(f"Missing final ORFS report: {required}")
    return timing, statistics, checks


def validate_synth_check(path: Path) -> None:
    if "Found and reported 0 problems." not in path.read_text(errors="replace"):
        raise RuntimeError(f"OpenROAD synthesis check reported problems: {path}")


def parse_worst_setup_path(path: Path) -> dict[str, str]:
    text = path.read_text(errors="replace")
    marker = "Post synthesis report_checks -path_delay max"
    if marker not in text:
        return {}
    startpoint = ""
    endpoint = ""
    for line in text.split(marker, 1)[1].splitlines():
        stripped = line.strip()
        if not startpoint and stripped.startswith("Startpoint:"):
            startpoint = stripped.split(":", 1)[1].strip()
        elif not endpoint and stripped.startswith("Endpoint:"):
            endpoint = stripped.split(":", 1)[1].strip()
            break
    if not startpoint and not endpoint:
        return {}
    return {
        "setup_worst_startpoint": startpoint,
        "setup_worst_endpoint": endpoint,
        "setup_worst_path": f"{startpoint} -> {endpoint}",
    }


def parse_timing(path: Path) -> dict[str, float]:
    metrics: dict[str, float] = {}
    keys = {
        "worst slack max": "setup_wns_ns",
        "worst slack min": "hold_wns_ns",
        "tns max": "setup_tns_ns",
        "tns min": "hold_tns_ns",
        "wns max": "setup_wns_report_ns",
        "wns min": "hold_wns_report_ns",
    }
    for line in path.read_text(errors="replace").splitlines():
        stripped = line.strip()
        for prefix, key in keys.items():
            if stripped.startswith(prefix):
                metrics[key] = round(float(stripped.split()[-1]) / 1000.0, 9)
    return metrics


def parse_power(path: Path) -> dict[str, float]:
    in_power_report = False
    for line in path.read_text(errors="replace").splitlines():
        if "Post synthesis report_power" in line:
            in_power_report = True
            continue
        if not in_power_report:
            continue
        match = re.match(
            r"^Total\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+"
            r"([-+0-9.eE]+)\s+([-+0-9.eE]+)",
            line,
        )
        if match:
            values = tuple(float(value) for value in match.groups())
            return dict(
                zip(
                    (
                        "power_internal_w",
                        "power_switching_w",
                        "power_leakage_w",
                        "power_total_w",
                    ),
                    values,
                )
            )
    return {}


def parse_statistics(path: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    cells = re.compile(r"^\s*(\d+)\s+\S+\s+\d+\s+\S+\s+cells\s*$")
    area = re.compile(r"^\s*Chip area for module '\\?[^']+':\s+([-+0-9.eE]+)")
    for line in path.read_text(errors="replace").splitlines():
        cell_match = cells.match(line)
        if cell_match:
            metrics["cell_count"] = int(cell_match.group(1))
        area_match = area.match(line)
        if area_match:
            metrics["area"] = float(area_match.group(1))
    missing = {"cell_count", "area"} - metrics.keys()
    if missing:
        raise RuntimeError(f"Missing synthesis statistics: {sorted(missing)}")
    return metrics


def _write_aggregate(
    cfg: DictConfig,
    output_root: Path,
    result: dict[str, Any],
    point_dir: Path,
) -> list[dict[str, Any]]:
    point_dir.mkdir(parents=True, exist_ok=True)
    (point_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )

    result_glob = "/".join(
        [
            (
                "clock_*mhz"
                if path == "experiment.clock_mhz"
                else f"{_result_key(path)}_*"
            )
            for path in sweep_dimension_paths(cfg)
        ]
        + ["result.json"]
    )
    result_files = sorted(output_root.glob(result_glob))
    rows = [json.loads(path.read_text()) for path in result_files]
    dimension_keys = [
        _result_key(path) for path in sweep_dimension_paths(cfg)
    ]
    rows.sort(
        key=lambda row: tuple(_sortable(row[key]) for key in dimension_keys)
    )

    fields = [str(field) for field in cfg.output.fields]
    for row in rows:
        missing = set(fields) - row.keys()
        if missing:
            raise RuntimeError(f"Missing configured output fields: {sorted(missing)}")

    (output_root / str(cfg.output.json)).write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n"
    )
    with (output_root / str(cfg.output.csv)).open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _sortable(value: Any) -> tuple[int, Any]:
    value = _coerce_number(value)
    if isinstance(value, (int, float)):
        return (0, float(value))
    return (1, str(value))


def sweep_dimension_paths(cfg: DictConfig) -> list[str]:
    """Return config paths that uniquely identify one synthesis point."""
    configured = cfg.get("sweep", {}).get("dimensions")
    if configured:
        paths = [str(path) for path in configured]
    else:
        paths = ["experiment.clock_mhz", str(cfg.sweep.x)]
        paths.extend(f"openroad.{name}" for name in cfg.get("openroad", {}))

    unique: list[str] = []
    for path in paths:
        _cfg_select(cfg, path)
        if path not in unique:
            unique.append(path)
    if str(cfg.sweep.x) not in unique:
        raise ValueError("sweep.dimensions must include sweep.x")
    keys = [_result_key(path) for path in unique]
    if len(keys) != len(set(keys)):
        raise ValueError("sweep dimension names must be unique")
    return unique


def _path_component(path: str, value: Any) -> str:
    if path == "experiment.clock_mhz":
        return f"clock_{value}mhz"
    key = _result_key(path)
    raw = str(value)
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("_") or "default"
    if slug != raw:
        digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
        slug = f"{slug}_{digest}"
    return f"{key}_{slug}"


def point_directory(cfg: DictConfig, output_root: Path) -> Path:
    point_dir = output_root
    for path in sweep_dimension_paths(cfg):
        point_dir /= _path_component(path, _cfg_select(cfg, path))
    return point_dir


def run_sweep_point(cfg: DictConfig) -> dict[str, Any]:
    apply_derived_values(cfg)
    project_root = Path(str(cfg.get("project_root", "."))).resolve()
    output_root = _project_path(project_root, cfg.output.root)
    x_path = str(cfg.sweep.x)
    _cfg_select(cfg, x_path)
    clock_mhz = int(_cfg_select(cfg, "experiment.clock_mhz"))
    point_dir = point_directory(cfg, output_root)
    work_root = point_dir / "work"
    output_root.mkdir(parents=True, exist_ok=True)

    if not bool(cfg.experiment.get("collect_only", False)):
        run_fusesoc(cfg, work_root, project_root)
    timing, statistics, checks = find_orfs_reports(work_root)
    validate_synth_check(checks)

    result: dict[str, Any] = {
        "clock_mhz": clock_mhz,
        "clock_period_ns": clock_period_ns(cfg),
        "status": "success",
        "work_root": str(work_root),
        "timing_report": str(timing),
        "stat_report": str(statistics),
        "check_report": str(checks),
    }
    for section in ("parameters", "experiment", "openroad"):
        for name, value in cfg.get(section, {}).items():
            result[str(name)] = _coerce_number(value)
    for name, value in cfg.get("result", {}).get("values", {}).items():
        result[str(name)] = _coerce_number(value)
    result.update(parse_timing(timing))
    result.update(parse_power(timing))
    result.update(parse_worst_setup_path(timing))
    result.update(parse_statistics(statistics))

    _write_aggregate(cfg, output_root, result, point_dir)
    return result
