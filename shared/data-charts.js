/* My Exams - offline-ready accessible, printable bar and pie chart renderer. */
(function(w,d){
"use strict";
if(w.MyExamsCharts)return;
const palette=["#147b5a","#d49a35","#3473b0","#c35b55","#7a62a8","#218995"];
const esc=x=>String(x==null?"":x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const number=x=>Number.isFinite(Number(x))?Math.max(0,Number(x)):0;
const show=x=>number(x).toLocaleString("en-US",{maximumFractionDigits:2});
function unpack(c){
 if(Array.isArray(c.categories)&&Array.isArray(c.series))return {labels:c.categories.map(String),series:c.series.map((s,i)=>({name:String(s.year||s.label||s.name||"Series "+(i+1)),values:c.categories.map((_,j)=>number((s.values||[])[j]))}))};
 const labels=Array.isArray(c.labels)?c.labels.map(String):[];
 return {labels,series:[{name:String(c.seriesLabel||c.label||"Value"),values:labels.map((_,j)=>number((c.values||[])[j]))}]};
}
function bars(c,labels,series){
 const max=Math.max(1,...series.flatMap(s=>s.values));
 const percent=c.unit==='%';
 const maxAxis=percent?100:Math.ceil(max/10)*10||1;
 const axisLabel=value=>show(value)+(percent?'%':'');
 let html="";
 if(series.length>1)html+='<div class="mex-legend">'+series.map((s,i)=>'<span><i style="background:'+palette[i%palette.length]+'"></i>'+esc(s.name)+'</span>').join("")+'</div>';
 html+='<div class="mex-bars" role="group" aria-label="Bar chart">';
 labels.forEach((label,i)=>{
  html+='<div class="mex-group"><strong class="mex-category">'+esc(label)+'</strong><div class="mex-lanes">';
  series.forEach((s,j)=>{
   const v=s.values[i],width=Math.min(100,100*v/maxAxis);
   html+='<div class="mex-row" role="group" aria-label="'+esc(label+" "+s.name+" "+show(v))+'">'+(series.length>1?'<span class="mex-year">'+esc(s.name)+'</span>':"")+
   '<div class="mex-track"><div class="mex-fill" style="width:'+width.toFixed(2)+'%;background:'+palette[j%palette.length]+'"></div></div><b class="mex-value">'+esc(axisLabel(v))+'</b></div>';
  });
  html+='</div></div>';
 });
 return html+'<div class="mex-axis"><span>'+axisLabel(0)+'</span><span>'+axisLabel(maxAxis/2)+'</span><span>'+axisLabel(maxAxis)+'</span></div></div>';
}
function pie(c,labels,series){
 const values=series[0].values,total=values.reduce((a,v)=>a+v,0);
 if(!total)return "<p>No data available.</p>";
 let angle=-Math.PI/2;
 const slices=values.map((v,i)=>{
  if(v===0)return "";
  if(Math.abs(v-total)<0.00001)return '<circle cx="160" cy="160" r="135" fill="'+palette[i%palette.length]+'"/>';
  const sweep=2*Math.PI*v/total,x1=160+135*Math.cos(angle),y1=160+135*Math.sin(angle),end=angle+sweep,x2=160+135*Math.cos(end),y2=160+135*Math.sin(end);
  angle=end;
  return '<path d="M160 160 L'+x1.toFixed(3)+' '+y1.toFixed(3)+' A135 135 0 '+(sweep>Math.PI?1:0)+' 1 '+x2.toFixed(3)+' '+y2.toFixed(3)+' Z" fill="'+palette[i%palette.length]+'" stroke="#fff" stroke-width="2"><title>'+esc(labels[i]+": "+show(v))+'</title></path>';
 }).join("");
 return '<div class="mex-pie-layout"><svg class="mex-pie" viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+esc(c.title||c.label||"Pie chart")+'">'+slices+'</svg><div class="mex-pie-legend">'+labels.map((label,i)=>'<div class="mex-pie-item"><i style="background:'+palette[i%palette.length]+'"></i><span>'+esc(label)+'</span><b>'+show(values[i])+' · '+(values[i]/total*100).toFixed(1)+'%</b></div>').join("")+'</div></div>';
}
function render(c){
 if(!c||typeof c!=="object")return "";
 const {labels,series}=unpack(c);
 if(!labels.length||!series.length)return "";
 const type=String(c.chartType||c.type||"bar").toLowerCase();
 const content=type==="pie"||type==="pie_chart"?pie(c,labels,series):bars(c,labels,series);
 const description=labels.map((lab,i)=>lab+": "+series.map(s=>s.name+" "+show(s.values[i])).join(", ")).join("; ");
 return '<figure class="mex-chart" aria-label="'+esc(c.title||c.label||"Data analysis chart")+'"><figcaption class="mex-title">'+esc(c.title||c.label||"Data analysis")+(c.unit?'<small> · '+esc(c.unit)+'</small>':"")+'</figcaption>'+content+'<p class="mex-sr">Data: '+esc(description)+'</p></figure>';
}
const style=d.createElement("style");style.id="mex-charts-v1";
style.textContent=[
'.mex-chart{max-width:100%;margin:16px 0 22px;padding:16px;background:#fffdf8;border:1.5px solid #d7c7a3;border-radius:16px;box-sizing:border-box;break-inside:avoid;color:#1b4037;font:15px/1.55 system-ui,Arial,sans-serif;direction:ltr;text-align:left}',
'.mex-chart *{box-sizing:border-box}.mex-title{font-size:clamp(16px,2.5vw,20px);font-weight:800;color:#0c4f3b;margin-bottom:14px}.mex-title small{font-size:13px;font-weight:500;color:#566c60}',
'.mex-legend{display:flex;flex-wrap:wrap;gap:13px;margin:5px 0 13px;font-size:13px}.mex-legend span{display:inline-flex;align-items:center;gap:6px}.mex-legend i,.mex-pie-item i{display:inline-block;flex:none;width:13px;height:13px;border-radius:3px}',
'.mex-group{display:grid;grid-template-columns:minmax(105px,25%) minmax(0,1fr);gap:9px;align-items:center;margin-bottom:13px}.mex-category{line-height:1.25;overflow-wrap:anywhere}.mex-lanes{min-width:0;display:grid;gap:5px}',
'.mex-row{display:flex;align-items:center;gap:8px;min-height:23px;min-width:0}.mex-year{flex:0 0 45px;font-size:11px;color:#50665a}.mex-track{flex:1;min-width:0;height:17px;border-radius:5px;background:#e4ece7;overflow:hidden}.mex-fill{height:100%;border-radius:5px}.mex-value{min-width:38px;text-align:right;font-size:13px;font-variant-numeric:tabular-nums}',
'.mex-axis{display:flex;justify-content:space-between;margin:5px 43px 0 27%;border-top:1px solid #b2c1b5;padding-top:4px;color:#687b70;font-size:11px}',
'.mex-pie-layout{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:22px}.mex-pie{width:min(290px,100%);height:auto;flex:0 1 290px}.mex-pie-legend{flex:1 1 220px;display:grid;gap:10px;min-width:0}.mex-pie-item{display:grid;grid-template-columns:13px minmax(0,1fr) auto;align-items:center;gap:8px;font-size:13px}.mex-pie-item b{font-size:13px;white-space:nowrap}',
'.mex-sr{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}',
'@media(max-width:520px){.mex-chart{padding:12px}.mex-group{grid-template-columns:1fr;gap:3px}.mex-row{gap:6px}.mex-axis{margin:5px 43px 0 0}.mex-pie{width:min(230px,100%);flex:0 1 230px}.mex-pie-legend{flex-basis:100%}}',
'@media print{.mex-chart{break-inside:avoid;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}.mex-track,.mex-fill,.mex-pie path,.mex-pie circle{print-color-adjust:exact;-webkit-print-color-adjust:exact}}'
].join("\n");
(d.head||d.documentElement).append(style);
w.MyExamsCharts={render};
})(window,document);
