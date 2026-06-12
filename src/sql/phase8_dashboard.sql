begin;
insert into dashboard.dashboard_metrics (metric_category, metric_name, metric_value)
select metric_category, metric_name, metric_value from (
	select 'smc'::text as metric_category, 'smc_context_count'::text as metric_name, count(smc_context_id)::text as metric_value from smc.smc_contexts
	union all
	select 'smc'::text, 'smc_structure_count'::text, count(structure_id)::text from smc.market_structure
	union all
	select 'smc'::text, 'smc_liquidity_count'::text, count(liquidity_id)::text from smc.liquidity_registry
	union all
	select 'smc'::text, 'smc_bias_count'::text, count(bias_id)::text from smc.bias_registry
	union all
	select 'smc'::text, 'smc_market_state_count'::text, count(state_id)::text from smc.market_state
	union all
	select 'smc'::text, 'smc_avg_alignment'::text, coalesce(avg(coalesce(smc_alignment,0))::text,'0'::text) from smc.smc_contexts
	union all
	select 'smc'::text, 'smc_decision_overlay_count'::text, coalesce(count(*)::text,'0'::text) from smc.smc_contexts where decision_context_id is not null
) t;
commit;
