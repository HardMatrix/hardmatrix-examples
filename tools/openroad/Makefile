ORFS_IMAGE ?= openroad/orfs:latest
ORFS_PULL_POLICY ?= missing
ORFS_FLOW := /OpenROAD-flow-scripts/flow
ORFS_WORK := /work
ORFS_DIRS := results reports logs objects
ORFS_DESIGN_NICKNAME ?= $(patsubst tb_%,%,$(DESIGN_NAME))
ORFS_MEMORY_LIMIT ?= 24g
ORFS_MEMORY_SWAP_LIMIT ?= $(ORFS_MEMORY_LIMIT)
PLATFORM ?= asap7
SYNTH_HIERARCHICAL ?= 1
SYNTH_MINIMUM_KEEP_SIZE ?= $(if $(filter asap7,$(PLATFORM)),1000,10000)
SYNTH_KEEP_MODULES ?=
SYNTH_OPT_HIER ?= $(SYNTH_HIERARCHICAL)
SYNTH_ARGS ?=
ABC_AREA ?= 0
ABC_CLOCK_PERIOD_IN_PS ?=
ABC_CLOCK_PERIOD_ENV := $(if $(strip $(ABC_CLOCK_PERIOD_IN_PS)),--env ABC_CLOCK_PERIOD_IN_PS="$(ABC_CLOCK_PERIOD_IN_PS)")
export SYNTH_HIERARCHICAL
export SYNTH_MINIMUM_KEEP_SIZE
export SYNTH_KEEP_MODULES
export SYNTH_OPT_HIER

.PHONY: synth-report clean

synth-report:
	@case "$(PLATFORM)" in \
		asap7|gt2n) ;; \
		*) echo "Unsupported ORFS platform '$(PLATFORM)'; expected asap7 or gt2n" >&2; exit 2 ;; \
	esac
	@case "$(SYNTH_OPT_HIER)" in \
		0|1) ;; \
		*) echo "Unsupported SYNTH_OPT_HIER value '$(SYNTH_OPT_HIER)'; expected 0 or 1" >&2; exit 2 ;; \
	esac
	@case "$(ABC_AREA)" in \
		0|1) ;; \
		*) echo "Unsupported ABC_AREA value '$(ABC_AREA)'; expected 0 or 1" >&2; exit 2 ;; \
	esac
	@echo "[HardMatrix ORFS] platform=$(PLATFORM) memory=$(ORFS_MEMORY_LIMIT) memory+swap=$(ORFS_MEMORY_SWAP_LIMIT)"
	@echo "[HardMatrix ORFS] hierarchical=$${SYNTH_HIERARCHICAL} opt-hier=$${SYNTH_OPT_HIER} minimum-keep-size=$${SYNTH_MINIMUM_KEEP_SIZE} keep-modules=$${SYNTH_KEEP_MODULES}"
	@echo "[HardMatrix ORFS] synth-args=$(SYNTH_ARGS) abc-area=$(ABC_AREA) abc-clock-period-ps=$(if $(strip $(ABC_CLOCK_PERIOD_IN_PS)),$(ABC_CLOCK_PERIOD_IN_PS),derived)"
	mkdir -p $(ORFS_DIRS)
	docker run --rm --pull=$(ORFS_PULL_POLICY) \
		--user "$$(id -u):$$(id -g)" \
		--memory="$(ORFS_MEMORY_LIMIT)" \
		--memory-swap="$(ORFS_MEMORY_SWAP_LIMIT)" \
		--env HOME=/tmp \
		--env PLATFORM="$(PLATFORM)" \
		--env SYNTH_HIERARCHICAL \
		--env SYNTH_MINIMUM_KEEP_SIZE \
		--env SYNTH_KEEP_MODULES \
		--env SYNTH_OPT_HIER="$(if $(filter 1,$(SYNTH_OPT_HIER)),1,)" \
		--env SYNTH_ARGS="$(SYNTH_ARGS)" \
		--env ABC_AREA="$(ABC_AREA)" $(ABC_CLOCK_PERIOD_ENV) \
		--env STA_CLK_PERIOD_NS \
		--env VERILOG_TOP_PARAMS \
		--volume "$(CURDIR):$(ORFS_WORK):ro" \
		--volume "$(CURDIR)/results:$(ORFS_FLOW)/results" \
		--volume "$(CURDIR)/reports:$(ORFS_FLOW)/reports" \
		--volume "$(CURDIR)/logs:$(ORFS_FLOW)/logs" \
		--volume "$(CURDIR)/objects:$(ORFS_FLOW)/objects" \
		--workdir $(ORFS_FLOW) \
		$(ORFS_IMAGE) \
		bash -lc 'source ../env.sh && make \
			DESIGN_NAME=$(DESIGN_NAME) \
			DESIGN_NICKNAME=$(ORFS_DESIGN_NICKNAME) \
			DESIGN_CONFIG=$(ORFS_WORK)/config.mk \
			synth-report'

clean:
	rm -rf $(ORFS_DIRS)
