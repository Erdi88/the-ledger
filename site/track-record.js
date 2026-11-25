(function(){
'use strict';
function el(tag,text,cls){var e=document.createElement(tag);if(text!=null)e.textContent=text;if(cls)e.className=cls;return e}
function pct(x,d){return x==null?'n/a':(x*100).toFixed(d==null?1:d)+'%'}
function table(head,rows){var t=el('table');t.style.cssText='width:100%;border-collapse:collapse;font-size:.8rem';var h=el('tr');head.forEach(function(c){var th=el('th',c);th.style.cssText='text-align:left;border-bottom:1px solid var(--text);padding:.35rem .4rem;vertical-align:bottom';h.appendChild(th)});t.appendChild(h);rows.forEach(function(r){var tr=el('tr');r.forEach(function(c){var td=el('td',c);td.style.cssText='border-bottom:1px solid var(--line);padding:.35rem .4rem;overflow-wrap:anywhere';tr.appendChild(td)});t.appendChild(tr)});return t}
function load(){fetch('data/bot_scorecard.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json()}).then(render).catch(function(){document.getElementById('verdict-body').textContent='The scorecard could not be loaded.'})}
function render(sc){
 document.getElementById('updated').textContent='Updated '+sc.generated_at.slice(0,16).replace('T',' ')+' UTC';
 document.getElementById('disclaimer').textContent=sc.disclaimer;
 var bt=sc.backtest,v=document.getElementById('verdict-body');v.textContent='';
 var edge=bt&&bt.edge_demonstrated;
 v.appendChild(el('p',edge?'The backtest shows a small edge over guessing the base rate. Treat it with suspicion until live results agree.':'No demonstrated edge yet. In the historical test the model does not beat simply guessing that stocks usually go up. Its guesses are logged anyway, so live results can prove or disprove that.'));
 v.appendChild(el('p','Predictions so far: '+sc.totals.predictions+' · graded: '+sc.totals.resolved+' · waiting for their date: '+sc.totals.pending));
 var sb=document.getElementById('scores-body');sb.textContent='';
 var rows=Object.keys(sc.by_horizon).map(function(h){var s=sc.by_horizon[h];return [h==='1m'?'1 month':'3 months',String(s.resolved),String(s.called)+' / '+String(s.abstained),pct(s.hit_rate),pct(s.always_up_hit_rate),pct(s.mean_return_when_up),pct(s.mean_return_when_down)]});
 sb.appendChild(table(['Horizon','Graded','Calls / abstained','Bot hit rate','"Always up" hit rate','Avg return after UP','Avg return after DOWN'],rows));
 if(sc.totals.resolved===0)sb.appendChild(el('p','Nothing has matured yet. The first 1-month predictions are graded about a month after they were made.','muted'));
 sb.appendChild(el('p','A bot is only useful if its hit rate beats "always up" over many graded calls. Early numbers on a handful of calls mean very little.','muted'));
 var bb=document.getElementById('backtest-body');bb.textContent='';
 if(bt){bb.appendChild(el('p',bt.method,'muted'));var br=Object.keys(bt.horizons).map(function(h){var m=bt.horizons[h];return [h==='1m'?'1 month':'3 months',String(m.n),pct(m.hit_rate),pct(m.base_hit_rate),m.auc==null?'n/a':m.auc.toFixed(3),m.brier.toFixed(4),m.brier_baseline.toFixed(4)]});
  bb.appendChild(table(['Horizon','Test rows','Model hit rate','Baseline hit rate','AUC (0.5 = coin flip)','Brier','Brier of baseline'],br));
  bb.appendChild(el('p',bt.edge_rule,'muted'))}else{bb.appendChild(el('p','No backtest available yet.'))}
 var lb=document.getElementById('log-body');lb.textContent='';
 var lr=sc.recent.map(function(p){var drivers=(p.drivers||[]).map(function(d){return d.feature+' '+d.pushes}).join(', ');var res=p.result?(pct(p.result.return)+(p.result.correct==null?' (no call)':p.result.correct?' ✓':' ✗')):'pending';return [p.made_at,p.ticker,p.horizon,p.call,p.p_up.toFixed(2),res,(p.red_flags&&p.red_flags.length?'⚠ '+p.red_flags.join('; ')+' · ':'')+drivers]});
 lb.appendChild(table(['Made','Stock','Horizon','Call','P(up)','Result','Flags and drivers'],lr));
}
load();
})();
