# OpenROAD launcher

This FuseSoC core packages the small Makefile adapter used by the public
area/timing sweep examples. Edalize supplies source and constraint manifests,
and the adapter runs OpenROAD Flow Scripts in Docker using the image selected by
`ORFS_IMAGE`.

The repository-level sweep configurations pin the image digest and select the
ASAP7 platform. Docker and GNU Make are therefore required on the host, while no
private HardMatrix repository is needed.

The launcher currently accepts the `asap7` and `gt2n` ORFS platforms. Generated
reports, logs, objects, and results stay under the FuseSoC work root in `build/`.
