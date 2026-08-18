current_design rs_chien_horner_pipeline

# ORFS's ASAP7 platform uses picoseconds. Hydra passes the requested clock
# period in nanoseconds through the local OpenROAD launcher.
set clk_period_ns 1.000
if {[info exists ::env(STA_CLK_PERIOD_NS)] && $::env(STA_CLK_PERIOD_NS) ne ""} {
    set clk_period_ns $::env(STA_CLK_PERIOD_NS)
}
set clk_period_ps [expr {$clk_period_ns * 1000.0}]

create_clock -name core_clk -period $clk_period_ps [get_ports clk]
set_clock_uncertainty 100 [get_clocks core_clk]
set_input_delay 0 -clock core_clk [all_inputs -no_clocks]
set_output_delay 0 -clock core_clk [all_outputs]
set_false_path -from [get_ports rst_n]
